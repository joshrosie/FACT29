import argparse
import random
from itertools import product
import os
import shutil
import sys 
import numpy as np
import json

# -------------------------------------------------------------------
# 0. Some existing helper functions from your code (lightly adapted)
# -------------------------------------------------------------------

def randomize_agents_order(agents, p1, rounds):
    round_assign = []
    names = [name for name in agents.keys()]
    last_agent = p1
    for i in range(0,int(np.ceil(rounds/len(agents)))): 
        shuffled = random.sample(names, len(names))
        while shuffled[0] == last_agent or shuffled[-1]==p1: shuffled = random.sample(names, len(names))
        round_assign += shuffled 
        last_agent = shuffled[-1]
    return round_assign

def convert_deal_to_string(deal):
    return ', '.join([f"{k}{v}" for k, v in deal.items()])

def write_output(output_dir, filename, log, full_names, ROUNDS):
    """
    Writes the negotiation log (who proposed which deal) as a JSON.
    """
    out_json = {}
    slot_assignment = [full_names[agent[0]] for agent in log]
    rounds = []
    for l in log:
        rounds.append({"agent": full_names[l[0]], 
                       "public_answer": "<DEAL>"+convert_deal_to_string(l[1])+"</DEAL>"})
    out_json["slot_assignment"] = slot_assignment
    out_json["rounds"] = rounds
    out_json["finished_rounds"] = ROUNDS+1
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, filename), 'w') as f:
        json.dump(out_json, f, indent=4, ensure_ascii=False)

# -------------------------------------------------------------------
# 1. Negotiation Environment & Data Loading
# -------------------------------------------------------------------

def load_utilities_and_config(game_dir):
    """
    Example loader for your environment:
     - read config.txt
     - read each player's score file
     - store in a dictionary: utilities[player_name][issue_index] = [...scores...]
     - store threshold in utilities[player_name]['threshold']
    Returns:
      full_names: { "p1": "Alice", ... }    (labels for printing)
      utilities:  { "p1": { 0: [...], 1: [...], ..., threshold: X }, "p2": ...}
      PLAYERS:    list of player keys, e.g. ["p1","p2","p3","p4","p5","p6"]
    """
    config_file = os.path.join(game_dir, "config.txt")
    score_dir   = os.path.join(game_dir, "scores_files")

    full_names = {}
    score_files = {}
    other_player_count = 3  # your naming scheme for p3, p4, p5, p6, etc.
    with open(config_file, "r") as f:
        lines = f.readlines()
        splt = [line.strip().split(",") for line in lines if line.strip()]
        for p in splt:
            if p[2] == "p1" or p[2] == "p2":
                score_files[p[2]] = p[1]
                full_names[p[2]] = p[0]
            else:
                # players beyond p2
                score_files['p'+str(other_player_count)] = p[1]
                full_names['p'+str(other_player_count)] = p[0]
                other_player_count += 1
    
    # Load each player's utility data
    utilities = {}
    for player, file in score_files.items():
        with open(os.path.join(score_dir, file+'.txt'), "r") as f:
            lines = f.readlines()
            splt = [line.strip().split(",") for line in lines]
            utilities[player] = {}
            for idx, issue in enumerate(splt):
                if idx == len(splt) - 1:
                    # last line is threshold
                    utilities[player]['threshold'] = int(issue[0])
                else:
                    # line of scores for this issue
                    utilities[player][idx] = [int(i) for i in issue]

    PLAYERS = list(utilities.keys())
    return full_names, utilities, PLAYERS


# Example function that returns an integer in [0..100]
def get_utility(player_name, deal, utilities, ISSUE_NAMES):
    # sum the relevant scores for each sub-issue value
    score = 0
    for idx, issue in enumerate(ISSUE_NAMES):
        # the deal[issue]-1 is the index in the player's score array
        # (assuming sub-issue values start at 1)
        score += utilities[player_name][idx][deal[issue]-1]
    return min(100, max(0, score))


def get_threshold(player_name, utilities):
    return utilities[player_name]['threshold']


# -------------------------------------------------------------------
# 2. Issues and Deals
# -------------------------------------------------------------------




# -------------------------------------------------------------------
# 3. Time-based Target Utility
# -------------------------------------------------------------------

def time_based_target_util(player_name, t, R, utilities):
    """
    Linear schedule from 100 down to threshold over (R+1) steps.
    """
    tau = get_threshold(player_name, utilities)
    return 100 - (100 - tau) * (t / (R + 1))


# -------------------------------------------------------------------
# 4. Multi-Sample "Consensus + Center" Approach
# -------------------------------------------------------------------

def find_feasible_deals(player_name, t, R, utilities):
    """
    All deals above T_{p_i}(t) for this agent. Fallback if none found.
    """
    target = time_based_target_util(player_name, t, R, utilities)
    feasible = [d for d in ALL_DEALS if get_utility(player_name, d, utilities, ISSUE_NAMES) >= target]
    if feasible:
        return feasible

    # fallback #1: deals >= threshold (the final fallback)
    tau = get_threshold(player_name, utilities)
    feasible = [d for d in ALL_DEALS if get_utility(player_name, d, utilities, ISSUE_NAMES) >= tau]
    if feasible:
        return feasible

    # fallback #2: single best
    best_deal = max(ALL_DEALS, key=lambda d: get_utility(player_name, d, utilities, ISSUE_NAMES))
    return [best_deal]


def generate_proposal_multisample_consensus_center(
    player_name, t, R, last_proposal, history, utilities, K=30, alpha=0.5
):
    """
    Proposes a deal by sampling up to K random deals from the feasible set
    and picking the one that is closest to a combination of:
      1) The 'consensus average' of all previously proposed deals
      2) The global midpoint of each issue dimension

    Weighted by alpha in [0..1]:
        score(deal) = alpha*dist_from_history + (1-alpha)*dist_from_midpoint
    We pick the deal with the smallest score.
    """
    # 1. Feasible set for this agent at round t
    feasible = find_feasible_deals(player_name, t, R, utilities)
    if not feasible:
        # should not happen because find_feasible_deals always returns fallback
        return random.choice(ALL_DEALS)

    # 2. Build "history consensus" (dimension-wise average) if possible
    if len(history) == 0:
        # fallback: pick random from feasible
        return random.choice(feasible)
    # compute average of all deals in history
    sum_dims = {iss: 0.0 for iss in ISSUE_NAMES}
    for (_, deal, _) in history:
        for iss in ISSUE_NAMES:
            sum_dims[iss] += deal[iss]
    count = len(history)
    avg_dims = {iss: sum_dims[iss]/count for iss in ISSUE_NAMES}

    # 3. Build global dimension midpoints
    midpoints = {}
    for iss, values in ISSUE_DIMENSIONS.items():
        midpoints[iss] = (min(values) + max(values)) / 2.0

    # 4. From feasible, pick K random deals (or all if fewer than K)
    if len(feasible) <= K:
        sample_set = feasible
    else:
        sample_set = random.sample(feasible, K)

    # 5. Compute a score for each deal in sample_set
    best_deal = None
    best_score = float("inf")

    for deal in sample_set:
        # Distance to history average
        dist_hist = sum(abs(deal[iss] - avg_dims[iss]) for iss in ISSUE_NAMES)
        # Distance to global midpoint
        dist_mid = sum(abs(deal[iss] - midpoints[iss]) for iss in ISSUE_NAMES)
        score = alpha*dist_hist + (1-alpha)*dist_mid
        if score < best_score:
            best_score = score
            best_deal = deal

    return best_deal


# -------------------------------------------------------------------
# 5. Main Negotiation Loop
# -------------------------------------------------------------------

def run_negotiation(
    utilities, 
    full_names,
    R=24,
    approach='multi_consensus_center',
    seed=None,
    K=30,
    alpha=0.5
):
    """
    Runs the negotiation for R rounds + 1 final proposal by p1.
    `approach` is our new "multi_consensus_center" approach by default.
    You can adapt it to other approaches if you like.

    Returns:
      final_deal,
      negotiation_log (list of (proposer, deal, round_num))
    """
    if seed is not None:
        random.seed(seed)

    PLAYERS = list(utilities.keys())

    # 1. Start with p1's best deal as "round 0"
    p1 = "p1"  # adapt if your naming is different
    best_for_p1 = max(ALL_DEALS, 
                      key=lambda d: get_utility(p1, d, utilities, ISSUE_NAMES))
    current_proposal = best_for_p1
    negotiation_log = [(p1, current_proposal, 0)]
    round_assignment = randomize_agents_order(utilities, 'p1', ROUNDS)
    # 2. R rounds
    for t in range(1, R+1):
        proposer = round_assignment[t-1]

        if approach == 'multi_consensus_center':
            new_proposal = generate_proposal_multisample_consensus_center(
                proposer, t, R, current_proposal, negotiation_log, utilities, K, alpha
            )
        else:
            raise NotImplementedError("Only multi_consensus_center is implemented here.")

        negotiation_log.append((proposer, new_proposal, t))
        current_proposal = new_proposal

    # 3. Final proposal by p1 at round (R+1)
    new_proposal = generate_proposal_multisample_consensus_center(
        p1, R+1, R, current_proposal, negotiation_log, utilities, K, alpha
    )
    negotiation_log.append((p1, new_proposal, R+1))

    # 4. Final acceptance check (5/6 and 6/6)
    final_deal = new_proposal
    final_acceptances = []
    for player in PLAYERS:
        needed_util = time_based_target_util(player, R+1, R, utilities)
        if get_utility(player, final_deal, utilities, ISSUE_NAMES) >= needed_util:
            final_acceptances.append(player)

    p1_ok = (p1 in final_acceptances)
    p2_ok = ("p2" in final_acceptances)
    passing_5_of_6 = (p1_ok and p2_ok and len(final_acceptances) >= 5)
    passing_6_of_6 = (len(final_acceptances) == len(PLAYERS))

    print(f"=== Approach: {approach}, K={K}, alpha={alpha} ===")
    if passing_5_of_6:
        print("[5/6-Way] Deal Achieved on final proposal.")
    else:
        print("No 5/6 acceptable final deal.")

    if passing_6_of_6:
        print("[6-Way] All players accepted!")
    else:
        print("Not all players accepted.")

    return final_deal, negotiation_log


# -------------------------------------------------------------------
# Initialize global variables
ISSUE_NAMES = None
ISSUE_DIMENSIONS = None
ALL_DEALS = None
ROUNDS = None

# -------------------------------------------------------------------
# 6. Example usage for 100 runs
# -------------------------------------------------------------------

def multi_sample_consensus_approach(game_dir):
    global ISSUE_NAMES, ISSUE_DIMENSIONS, ALL_DEALS, ROUNDS
    # Adjust these paths as needed
    game_dir = 'our_games_descriptions/'+game_dir
    if not os.path.exists(game_dir):
        print(f"Game directory {game_dir} not found.")
        sys.exit(1)
    output_dir = os.path.join(game_dir, os.path.join("output_reproduce/baselines","multi_consensus"))

    # copy scores_files to output_dir
    shutil.copytree(os.path.join(game_dir, "scores_files"), os.path.join(output_dir, "scores_files"))
    # copy config.txt to output_dir
    shutil.copy2(os.path.join(game_dir, "config.txt"), os.path.join(output_dir, "config.txt"))

    # Load the environment
    full_names, utilities, PLAYERS = load_utilities_and_config(game_dir)

    # calculate ISSUE_DIMENSIONS from utilities
    ISSUE_NAMES = ["A", "B", "C", "D", "E"]
    ISSUE_DIMENSIONS = {}
    for idx, issue in enumerate(ISSUE_NAMES):
        ISSUE_DIMENSIONS[issue] = list(range(1, len(utilities['p1'][idx])+1))
    ALL_DEALS = []
    for combo in product(*[ISSUE_DIMENSIONS[i] for i in ISSUE_NAMES]):
        ALL_DEALS.append(dict(zip(ISSUE_NAMES, combo)))

    ROUNDS = 24
    N_RUNS = 100

    # Run 100 times
    for j in range(N_RUNS):
        final_deal, log = run_negotiation(
            utilities=utilities,
            full_names=full_names,
            R=ROUNDS,
            approach='multi_consensus_center',
            seed=j,           # different seed for each iteration
            K=30,            # sample size
            alpha=1        # weighting factor
        )

        # Save the output
        write_output(output_dir, f"history_{j}.json", log, full_names, ROUNDS)
