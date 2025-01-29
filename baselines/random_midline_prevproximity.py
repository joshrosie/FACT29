import random
from itertools import product
import os
import shutil 
import numpy as np
import json
import sys
import argparse


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
    # convert from {'A': 2, 'B': 3, 'C': 1, 'D': 2, 'E': 2} to 'A2, B3, C1, D2, E2'
    return ', '.join([f"{k}{v}" for k, v in deal.items()])

def write_output(output_dir, filename, log):
    out_json = {}
    slot_assignment = [full_names[agent[0]] for agent in log]
    rounds = []
    for l in log:
        rounds.append({"agent": full_names[l[0]], "public_answer": "<DEAL>"+convert_deal_to_string(l[1])+"</DEAL>"})
    out_json["slot_assignment"] = slot_assignment
    out_json["rounds"] = rounds
    out_json["finished_rounds"] = ROUNDS+1
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, filename), 'w') as f:
        json.dump(out_json, f, indent=4, ensure_ascii=False)



# -------------------------------------------------------------------
# 2. Define utility functions & thresholds for each player
# -------------------------------------------------------------------

def dummy_utility(deal, player_name):
    """
    Example utility function for demonstration.
    Returns an integer in [0, 100].
    
    - player_index: which player (0 to 5).
    - deal: dict, e.g. {"A": 2, "B": 4, "C": 1, "D": 3, "E": 1}.
    """
    score = 0
    for idx, issue in enumerate(ISSUE_NAMES):
        score += utilities[player_name][idx][deal[issue]-1]

    
    # Map raw_score to [0..100] by clamping
    scaled = min(100, max(0, score))
    return scaled


def get_utility(player_name, deal):
    return dummy_utility(deal, player_name)

def get_threshold(player_name):
    return utilities[player_name]['threshold']


# -------------------------------------------------------------------
# 3. Time-based concession
# -------------------------------------------------------------------

def time_based_target_util(player_name, t, R):
    """
    Returns T_{p_i}(t) for round t in {1..R}, linearly decreasing from 100 to tau_{p_i} over R+1 steps.
    """
    tau = get_threshold(player_name)
    # T_i(t) = 100 - (100 - tau) * (t / (R+1))
    return 100 - (100 - tau) * (t / (R + 1))


# -------------------------------------------------------------------
# 4. Proposal generation: three approaches
# -------------------------------------------------------------------

def find_feasible_deals(player_name, t, R):
    """
    Find all deals that meet or exceed T_{p_i}(t) for this round.
    If none found, fallback to deals >= tau_{p_i}.
    If still none, fallback to the single best deal for this player.
    """
    target = time_based_target_util(player_name, t, R)
    feasible = [d for d in ALL_DEALS if get_utility(player_name, d) >= target]
    if not feasible:
        # fallback to deals above actual threshold
        tau = get_threshold(player_name)
        feasible = [d for d in ALL_DEALS if get_utility(player_name, d) >= tau]
        if not feasible:
            # fallback to best possible deal
            best_deal = max(ALL_DEALS, key=lambda d: get_utility(player_name, d))
            return [best_deal]
    return feasible


def generate_proposal_random_feasible(player_name, t, R, last_proposal):
    """
    Randomly pick any feasible deal from the set of deals
    that meet the agent's time-based target utility.
    """
    feasible = find_feasible_deals(player_name, t, R)
    return random.choice(feasible)


def generate_proposal_centered(player_name, t, R, last_proposal):
    """
    Among feasible deals, pick the one closest to the "center" of each issue dimension.
    The "center" is the midpoint of each dimension's min and max (in float).
    Then measure sum of absolute distance from each dimension's midpoint.
    """
    feasible = find_feasible_deals(player_name, t, R)

    # Precompute midpoints of each dimension
    dimension_midpoints = {}
    for issue, values in ISSUE_DIMENSIONS.items():
        min_val = min(values)
        max_val = max(values)
        midpoint = (min_val + max_val) / 2.0
        dimension_midpoints[issue] = midpoint

    # Among feasible deals, choose the one with minimal sum of |deal[issue] - midpoint|.
    best_deal = None
    best_score = float("inf")

    for deal in feasible:
        dist_sum = 0
        for issue in ISSUE_NAMES:
            dist_sum += abs(deal[issue] - dimension_midpoints[issue])
        if dist_sum < best_score:
            best_score = dist_sum
            best_deal = deal

    return best_deal


def generate_proposal_previous_proximity(player_name, t, R, last_proposal):
    """
    Among feasible deals, pick the one closest to the last proposal in terms
    of sum of absolute differences for each issue dimension.
    
    If last_proposal is None, fallback to random feasible or center.
    """
    feasible = find_feasible_deals(player_name, t, R)
    if last_proposal is None:
        # fallback: random or center
        return random.choice(feasible)

    best_deal = None
    best_score = float("inf")

    for deal in feasible:
        dist_sum = 0
        for issue in ISSUE_NAMES:
            dist_sum += abs(deal[issue] - last_proposal[issue])
        if dist_sum < best_score:
            best_score = dist_sum
            best_deal = deal

    return best_deal


def generate_proposal(player_name, t, R, last_proposal, approach='random'):
    """
    Wrapper to switch among the different approaches:
      'random'       -> generate_proposal_random_feasible
      'centered'     -> generate_proposal_centered
      'prev_prox'    -> generate_proposal_previous_proximity
    """
    if approach == 'random':
        return generate_proposal_random_feasible(player_name, t, R, last_proposal)
    elif approach == 'midline':
        return generate_proposal_centered(player_name, t, R, last_proposal)
    elif approach == 'prev_prox':
        return generate_proposal_previous_proximity(player_name, t, R, last_proposal)
    else:
        raise ValueError(f"Unknown approach: {approach}")


# -------------------------------------------------------------------
# 5. Main negotiation procedure
# -------------------------------------------------------------------

def run_negotiation(R=24, approach='random'):
    """
    Run the negotiation with 6 players, for R rounds, using the specified approach
    for proposal generation. Then p_1 makes a final proposal at round R+1.

    approach can be:
        - 'random'
        - 'centered'
        - 'prev_prox'

    Returns (final_deal, negotiation_log).
    """
        
    # Randomize the order of players for each round
    round_assignment = randomize_agents_order(utilities, 'p1', ROUNDS)

    # 1. Start with a predefined deal from p_1 (their best deal, or any other).
    best_for_p1 = max(ALL_DEALS, key=lambda d: get_utility("p1", d))
    current_proposal = best_for_p1  # "round 0" proposal
    negotiation_log = [("p1", current_proposal, 0)]

    # 2. R rounds of negotiation
    for t in range(1, R+1):
        proposer = round_assignment[t-1]
        
        # The proposer generates a new proposal using the chosen approach
        new_proposal = generate_proposal(proposer, t, R, current_proposal, approach)
        negotiation_log.append((proposer, new_proposal, t))
        current_proposal = new_proposal

    # 3. Final proposal by p_1 at round R+1
    final_deal = generate_proposal("p1", R+1, R, current_proposal, approach)
    negotiation_log.append(("p1", final_deal, R+1))

    # 4. Each player decides to accept or reject the final proposal
    final_acceptances = []
    for player in PLAYERS:
        # T_{p_i}(R+1) = player's threshold (by definition of the linear schedule)
        t_player = time_based_target_util(player, R+1, R)
        if get_utility(player, final_deal) >= t_player:
            final_acceptances.append(player)

    # Check 5/6 acceptance with p_1 and p_2 included
    p1_ok = "p1" in final_acceptances
    p2_ok = "p2" in final_acceptances
    passing_5_of_6 = (p1_ok and p2_ok and (len(final_acceptances) >= 5))

    # Print outcome
    if passing_5_of_6:
        print("[5/6-Way] Deal Achieved on final proposal!")
    else:
        print("No 5/6 acceptable final deal.")
    
    if len(final_acceptances) == 6:
        print("[6-Way] All players accepted!")
    else:
        print("Not all players accepted.")

    return final_deal, negotiation_log

def random_approach(seed=24):
    _out_dir = os.path.join(output_dir,"random_approach")
    random.seed(seed)
    for j in range(100):
        final_deal_random, log_random = run_negotiation(R=ROUNDS, approach='random')
        write_output(_out_dir, f"history_{j}.json", log_random)
        print("\nFinal deal (random):", final_deal_random)
    # copy scores directory to output directory
    shutil.copytree(score_dir, os.path.join(_out_dir, "scores_files"))
    # copy config file to output directory
    shutil.copy(config_file, os.path.join(_out_dir, "config.txt"))

def midline_approach(seed=24):
    _out_dir = os.path.join(output_dir,"midline_approach")
    random.seed(seed)
    for j in range(100):
        final_deal_centered, log_centered = run_negotiation(R=ROUNDS, approach='midline')
        write_output(_out_dir, f"history_{j}.json", log_centered)
        print("\nFinal deal (centered):", final_deal_centered)
    # copy scores directory to output directory
    shutil.copytree(score_dir, os.path.join(_out_dir, "scores_files"))
    # copy config file to output directory
    shutil.copy(config_file, os.path.join(_out_dir, "config.txt"))

def prev_prox_approach(seed=24):
    _out_dir = os.path.join(output_dir,"prev_prox_approach")
    random.seed(seed)
    for j in range(100):
        final_deal_prevprox, log_prevprox = run_negotiation(R=ROUNDS, approach='prev_prox')
        write_output(_out_dir, f"history_{j}.json", log_prevprox)
        print("\nFinal deal (previous-proximity):", final_deal_prevprox)
    # copy scores directory to output directory
    shutil.copytree(score_dir, os.path.join(_out_dir, "scores_files"))
    # copy config file to output directory
    shutil.copy(config_file, os.path.join(_out_dir, "config.txt"))


# -------------------------------------------------------------------
# initialize global variables
output_dir = None
initial_deal_file = None
utilities = None
ROUNDS = None
full_names = None
NUM_PLAYERS = None
PLAYERS = None
ISSUE_NAMES = None
ISSUE_DIMENSIONS = None
ALL_DEALS = None
score_dir = None
config_file = None
# -------------------------------------------------------------------


def random_midline_prevproximity(game_dir, method):
    global output_dir, initial_deal_file, utilities, ROUNDS, full_names, NUM_PLAYERS, PLAYERS, ISSUE_NAMES, ISSUE_DIMENSIONS, ALL_DEALS
    global score_dir, config_file
    game_dir = 'our_games_descriptions/'+game_dir
    if not os.path.exists(game_dir):
        print(f"Game directory {game_dir} not found.")
        sys.exit(1)
    output_dir = os.path.join(game_dir, "output_reproduce/baselines")
    score_dir = os.path.join(game_dir, "scores_files")
    config_file = os.path.join(game_dir, "config.txt")
    initial_deal_file = os.path.join(game_dir, "initial_deal.txt")

    full_names = {}
    score_files = {}
    other_player_count = 3
    with open(config_file, "r") as f:
        lines = f.readlines()
        splt = [line.strip().split(",") for line in lines if line.strip() != '']
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
            for idx, issue in enumerate(splt):
                if player not in utilities:
                    utilities[player] = {}
                if idx == len(splt) - 1:
                    utilities[player]['threshold'] = int(issue[0])
                else:
                    utilities[player][idx] = [int(i) for i in issue]

    # -------------------------------------------------------------------
    # 1. Define the negotiation environment
    # -------------------------------------------------------------------

    # Suppose we have 5 issues: A, B, C, D, E
    # Let's define their discrete values:

    # calculate ISSUE_DIMENSIONS from utilities
    ISSUE_NAMES = ["A", "B", "C", "D", "E"]
    ISSUE_DIMENSIONS = {}
    for idx, issue in enumerate(ISSUE_NAMES):
        ISSUE_DIMENSIONS[issue] = list(range(1, len(utilities['p1'][idx])+1))

    # Generate all possible deals (Cartesian product of sub-issue values).
    ALL_DEALS = []
    for combo in product(*[ISSUE_DIMENSIONS[iss] for iss in ISSUE_NAMES]):
        # combo might be (1,1,1,1,1) or (1,1,1,1,2), etc.
        # We'll store the deal as a dict {issue_name: chosen_value}
        deal = dict(zip(ISSUE_NAMES, combo))
        ALL_DEALS.append(deal)

    # Number of players
    NUM_PLAYERS = len(list(utilities.keys()))  # 6
    PLAYERS = list(utilities.keys())  # ["p_1", "p_2", ..., "p_6"]
    ROUNDS = 24

    # Run the negotiation
    if method == 'random':
        random_approach()
    elif method == 'midline':
        midline_approach()
    elif method == 'prev_prox':
        prev_prox_approach()
    else:
        print("Invalid method")
        sys.exit(1)