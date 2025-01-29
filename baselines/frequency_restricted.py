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

def load_utilities_and_config(game_dir):
    """
    Reads config.txt to get player info, then reads each player's score file.
    Returns:
      full_names: { "p1": "Alice", ... }    
      utilities:  { "p1": { 0: [...], 1: [...], ..., 'threshold': X }, "p2": ...}
      PLAYERS:    e.g. ["p1","p2","p3","p4","p5","p6"]
    """
    config_file = os.path.join(game_dir, "config.txt")
    score_dir   = os.path.join(game_dir, "scores_files")

    full_names = {}
    score_files = {}
    other_player_count = 3
    with open(config_file, "r") as f:
        lines = f.readlines()
        splt = [line.strip().split(",") for line in lines if line.strip()]
        for p in splt:
            if p[2] == "p1" or p[2] == "p2":
                score_files[p[2]] = p[1]
                full_names[p[2]] = p[0]
            else:
                score_files['p'+str(other_player_count)] = p[1]
                full_names['p'+str(other_player_count)] = p[0]
                other_player_count += 1
    
    utilities = {}
    for player, file in score_files.items():
        with open(os.path.join(score_dir, file+'.txt'), "r") as f:
            lines = f.readlines()
            splt = [line.strip().split(",") for line in lines]
            utilities[player] = {}
            for idx, issue in enumerate(splt):
                if idx == len(splt) - 1:
                    utilities[player]['threshold'] = int(issue[0])
                else:
                    utilities[player][idx] = [int(i) for i in issue]

    PLAYERS = list(utilities.keys())
    return full_names, utilities, PLAYERS

def get_utility(player_name, deal, utilities, ISSUE_NAMES):
    """
    Returns an integer [0..100].
    'utilities' is a dict: utilities[player_name][issue_idx] -> list of possible scores
    deal[issue] - 1 is the index in that list (assuming sub-issue values start at 1).
    """
    score = 0
    for idx, issue in enumerate(ISSUE_NAMES):
        score += utilities[player_name][idx][deal[issue]-1]
    return min(100, max(0, score))

def get_threshold(player_name, utilities):
    return utilities[player_name]['threshold']

# -------------------------------------------------------------------
# 1. Issues Setup
# -------------------------------------------------------------------



# -------------------------------------------------------------------
# 2. Frequency Counter for Dimension Values
# -------------------------------------------------------------------

def init_frequency_counter():
    """
    freq_counter[issue_name][sub_value] = 0 initially.
    """
    freq_counter = {}
    for issue, values in ISSUE_DIMENSIONS.items():
        freq_counter[issue] = {}
        for v in values:
            freq_counter[issue][v] = 0
    return freq_counter

def update_frequency_counter(freq_counter, deal):
    """
    Increment the count for each dimension's sub-value in the proposed deal.
    """
    for issue in ISSUE_NAMES:
        val = deal[issue]
        freq_counter[issue][val] += 1

def get_restricted_domain(freq_counter, top_k=2):
    """
    For each issue, pick the top_k sub-values (by frequency).
    Then form the Cartesian product of those sub-values to get restricted deals.
    """
    restricted_dims = {}
    for issue in ISSUE_NAMES:
        # sort sub-values by descending frequency
        sorted_vals = sorted(freq_counter[issue].items(), key=lambda x: x[1], reverse=True)
        # pick top_k
        chosen = [val for (val, freq) in sorted_vals[:top_k]]
        restricted_dims[issue] = chosen

    restricted_deals = []
    from itertools import product
    combos = product(*[restricted_dims[i] for i in ISSUE_NAMES])
    for combo in combos:
        restricted_deals.append(dict(zip(ISSUE_NAMES, combo)))
    return restricted_deals


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
# 4. Feasibility & Frequency-Restricted Multi-Sample “Consensus + Center”
# -------------------------------------------------------------------

def find_feasible_deals(player_name, t, R, utilities):
    """
    Returns all deals with U_{p_i} >= T_{p_i}(t).
    Fallback if none found.
    """
    target = time_based_target_util(player_name, t, R, utilities)
    feasible = [d for d in ALL_DEALS if get_utility(player_name, d, utilities, ISSUE_NAMES) >= target]
    if feasible:
        return feasible

    # fallback #1: deals >= threshold
    tau = get_threshold(player_name, utilities)
    feasible = [d for d in ALL_DEALS if get_utility(player_name, d, utilities, ISSUE_NAMES) >= tau]
    if feasible:
        return feasible

    # fallback #2: single best
    best_deal = max(ALL_DEALS, key=lambda d: get_utility(player_name, d, utilities, ISSUE_NAMES))
    return [best_deal]


def generate_proposal_freq_restrict_multi_consensus(
    player_name, t, R, last_proposal, history, utilities,
    freq_counter, top_k=2, K=30, alpha=0.5
):
    """
    1) Build the restricted domain from top_k frequent sub-values per issue.
    2) Intersect that domain with the feasible set for player_name at round t.
    3) If intersection is empty/small, fallback to full feasible set.
    4) From that final set, sample up to K deals and pick the one that
       minimizes alpha*dist_from_history + (1-alpha)*dist_from_midpoint.
    """
    # Build or find feasible set
    feasible_full = find_feasible_deals(player_name, t, R, utilities)

    # 1) restricted domain
    restricted_deals = get_restricted_domain(freq_counter, top_k=top_k)

    # turn restricted_deals into a set for quick membership test
    restricted_signatures = {
        tuple(d[iss] for iss in ISSUE_NAMES) for d in restricted_deals
    }

    # 2) intersection with feasible
    feasible_restricted = []
    for d in feasible_full:
        sig = tuple(d[iss] for iss in ISSUE_NAMES)
        if sig in restricted_signatures:
            feasible_restricted.append(d)

    # fallback if empty
    if len(feasible_restricted) < 1:
        final_candidates = feasible_full
    else:
        final_candidates = feasible_restricted

    # If no previous history, pick random from final_candidates
    if len(history) == 0:
        return random.choice(final_candidates)

    # compute history average
    sum_dims = {iss: 0.0 for iss in ISSUE_NAMES}
    for (_, deal, _) in history:
        for iss in ISSUE_NAMES:
            sum_dims[iss] += deal[iss]
    count = len(history)
    avg_dims = {iss: sum_dims[iss]/count for iss in ISSUE_NAMES}

    # compute global midpoints
    midpoints = {}
    for iss, values in ISSUE_DIMENSIONS.items():
        midpoints[iss] = (min(values) + max(values)) / 2.0

    # sample up to K deals
    if len(final_candidates) <= K:
        sample_set = final_candidates
    else:
        sample_set = random.sample(final_candidates, K)

    best_deal = None
    best_score = float("inf")
    for d in sample_set:
        dist_hist = sum(abs(d[iss] - avg_dims[iss]) for iss in ISSUE_NAMES)
        dist_mid  = sum(abs(d[iss] - midpoints[iss]) for iss in ISSUE_NAMES)
        score = alpha*dist_hist + (1 - alpha)*dist_mid
        if score < best_score:
            best_score = score
            best_deal = d

    return best_deal


# -------------------------------------------------------------------
# 5. Main Negotiation Loop
# -------------------------------------------------------------------

def run_negotiation_freq_restrict(
    utilities,
    full_names,
    R=24,
    seed=None,
    K=30,
    alpha=0.5,
    top_k=2
):
    """
    Each round:
      - pick a random proposer
      - proposer uses freq_restrict_multi_consensus to propose a new deal
      - update freq_counter
    After R rounds, p1 proposes final (R+1) deal.
    Check acceptance (5/6 and 6/6).
    """
    if seed is not None:
        random.seed(seed)

    PLAYERS = list(utilities.keys())
    p1 = "p1"
    p2 = "p2"

    # Init freq_counter
    freq_counter = init_frequency_counter()

    # Round 0: p1's best
    best_for_p1 = max(ALL_DEALS, key=lambda d: get_utility(p1, d, utilities, ISSUE_NAMES))
    current_proposal = best_for_p1
    negotiation_log = [(p1, current_proposal, 0)]
    update_frequency_counter(freq_counter, current_proposal)
    round_assignment = randomize_agents_order(utilities, 'p1', ROUNDS)
    # R rounds
    for t in range(1, R+1):
        proposer = round_assignment[t-1]
        new_proposal = generate_proposal_freq_restrict_multi_consensus(
            player_name=proposer,
            t=t,
            R=R,
            last_proposal=current_proposal,
            history=negotiation_log,
            utilities=utilities,
            freq_counter=freq_counter,
            top_k=top_k,
            K=K,
            alpha=alpha
        )
        negotiation_log.append((proposer, new_proposal, t))
        current_proposal = new_proposal
        update_frequency_counter(freq_counter, current_proposal)

    # Final proposal by p1 at round R+1
    final_proposal = generate_proposal_freq_restrict_multi_consensus(
        player_name=p1,
        t=R+1,
        R=R,
        last_proposal=current_proposal,
        history=negotiation_log,
        utilities=utilities,
        freq_counter=freq_counter,
        top_k=top_k,
        K=K,
        alpha=alpha
    )
    negotiation_log.append((p1, final_proposal, R+1))
    update_frequency_counter(freq_counter, final_proposal)

    # Acceptance check
    final_deal = final_proposal
    final_acceptances = []
    for pl in PLAYERS:
        needed_util = time_based_target_util(pl, R+1, R, utilities)
        if get_utility(pl, final_deal, utilities, ISSUE_NAMES) >= needed_util:
            final_acceptances.append(pl)

    p1_ok = (p1 in final_acceptances)
    p2_ok = (p2 in final_acceptances)
    passing_5of6 = (p1_ok and p2_ok and len(final_acceptances) >= 5)
    passing_6of6 = (len(final_acceptances) == len(PLAYERS))

    print(f"=== freq_restrict_multi_consensus (K={K}, alpha={alpha}, top_k={top_k}) ===")
    if passing_5of6:
        print(" [5/6-Way] Deal Achieved on final proposal.")
    else:
        print(" No 5/6 acceptable final deal.")
    if passing_6of6:
        print(" [6-Way] All players accepted!")
    else:
        print(" Not all players accepted.")

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

def freq_restrict_multi_consensus_approach(game_dir):
    global ISSUE_NAMES, ISSUE_DIMENSIONS, ALL_DEALS, ROUNDS
    # Adjust these paths as needed
    game_dir = 'our_games_descriptions/'+game_dir
    if not os.path.exists(game_dir):
        print(f"Game directory {game_dir} not found.")
        sys.exit(1)
    output_dir = os.path.join(game_dir, "output_reproduce/baselines", "freq_restrict_multi_consensus")

    # copy scores_files to output_dir
    shutil.copytree(os.path.join(game_dir, "scores_files"), os.path.join(output_dir, "scores_files"))
    # copy config.txt to output_dir
    shutil.copy2(os.path.join(game_dir, "config.txt"), os.path.join(output_dir, "config.txt"))

    # Load environment
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



    for j in range(N_RUNS):
        final_deal, log = run_negotiation_freq_restrict(
            utilities=utilities,
            full_names=full_names,
            R=ROUNDS,
            seed=j,
            K=30,         # sample size
            alpha=1,    # weighting factor for (history-dist vs. midpoint-dist)
            top_k=2       # top 2 sub-values per issue
        )

        # Save the output
        write_output(output_dir, f"history_{j}.json", log, full_names, ROUNDS)
