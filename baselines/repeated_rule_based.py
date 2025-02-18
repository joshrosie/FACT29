import argparse
import random
from itertools import product
import os
import shutil
import sys 
import numpy as np
import json

# -------------------------------------------------------------------
# 0. Some existing helper functions (unchanged from your baseline)
# -------------------------------------------------------------------

def randomize_agents_order(agents, p1, rounds):
    round_assign = []
    names = [name for name in agents.keys()]
    last_agent = p1
    for i in range(0,int(np.ceil(rounds/len(agents)))):
        shuffled = random.sample(names, len(names))
        # ensure we don't get the same agent in consecutive sequences
        # and also don't end with p1 if we want p1 to be last only in the final round
        while shuffled[0] == last_agent:
            shuffled = random.sample(names, len(names))
        round_assign += shuffled 
        last_agent = shuffled[-1]
    # override the very last round to ensure p1 is the final agent
    round_assign[rounds-1] = p1
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
    Reads config.txt to get player info, then reads each player's score file.
    Returns:
      full_names: { "p1": "Alice", ... }
      utilities:  { "p1": { 0: [...], 1: [...], ..., threshold: X }, "p2": ...}
      PLAYERS:    list of player keys, e.g. ["p1","p2","p3","p4","p5","p6"]
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
    score = 0
    for idx, issue in enumerate(ISSUE_NAMES):
        # sub-issue is 1-based; array is 0-based
        score += utilities[player_name][idx][deal[issue]-1]
    return min(100, max(0, score))

def get_threshold(player_name, utilities):
    return utilities[player_name]['threshold']


# -------------------------------------------------------------------
# 2. Global placeholders (populated later in multi_sample_consensus_approach)
# -------------------------------------------------------------------

ISSUE_NAMES = None
ISSUE_DIMENSIONS = None
ALL_DEALS = None
ROUNDS = None

# -------------------------------------------------------------------
# 3. Time-based Target Utility
#     (Still used for final acceptance check.)
# -------------------------------------------------------------------

def time_based_target_util(player_name, t, R, utilities):
    tau = get_threshold(player_name, utilities)
    return 100 - (100 - tau) * (t / (R + 1))

# -------------------------------------------------------------------
# 4. Repeated Rule-Based Approach
# -------------------------------------------------------------------

def get_priority_order(player, utilities, issue_count):
    """
    Returns a list of issue indices in descending order of "importance" for this agent.
    A simple metric is: (max(sub-issue scores) - min(sub-issue scores)).
    The bigger that difference, the more that agent cares about that issue.
    """
    # For each issue idx, find the range of scores
    importance = []
    for i in range(issue_count):
        rng = np.random.uniform(0, 100) # random value
        importance.append((rng, i))

    # sort descending by range
    importance.sort(reverse=True, key=lambda x: x[0])
    # extract the issue indices in order
    ordered = [issue_idx for (_, issue_idx) in importance]
    return ordered

def generate_proposal_repeated_rule_based(
    player_name,
    current_deal,
    utilities,
    issue_names,
    current_round
):
    """
    Repeated rule-based improvement:
      1) Check agent's current utility. If >= actual threshold, do nothing.
      2) Otherwise, go from highest-priority to lowest-priority issue:
         - For each issue, find the sub-value that yields the highest utility for this agent
           (keeping other issues fixed).
         - If that sub-value yields strictly higher utility, update the deal.
      3) Stop when we've updated all issues or we reach threshold.
    Returns the modified deal.
    """
    new_deal = dict(current_deal)  # copy
    agent_threshold = get_threshold(player_name, utilities)
    # agent_threshold = time_based_target_util(player_name, current_round, ROUNDS, utilities)

    current_util = get_utility(player_name, new_deal, utilities, issue_names)
    if current_util >= agent_threshold:
        # Already meets threshold, so no changes
        return new_deal

    issue_count = len(issue_names)
    # Figure out priority order for this agent
    priority_order = get_priority_order(player_name, utilities, issue_count)

    for issue_idx in priority_order:
        # If we are already above threshold, no need to keep changing
        current_util = get_utility(player_name, new_deal, utilities, issue_names)
        if current_util >= agent_threshold:
            break

        # the set of possible sub-values for this issue
        issue = issue_names[issue_idx]
        possible_vals = ISSUE_DIMENSIONS[issue]

        best_val = new_deal[issue]
        best_util = current_util  # current utility

        # Try each possible sub-value
        for val in possible_vals:
            if val == new_deal[issue]:
                continue
            test_deal = dict(new_deal)
            test_deal[issue] = val
            test_util = get_utility(player_name, test_deal, utilities, issue_names)
            if test_util > best_util:
                best_util = test_util
                best_val = val
        
        # If we found a better sub-value, update
        if best_val != new_deal[issue]:
            new_deal[issue] = best_val

    return new_deal


# -------------------------------------------------------------------
# 5. Main Negotiation Loop (Modified to Support repeated_rule_based)
# -------------------------------------------------------------------

def run_negotiation(
    utilities, 
    full_names,
    R=24,
    approach='repeated_rule_based',
    seed=None,
    K=30,
    alpha=0.5
):
    """
    Runs the negotiation for R rounds + 1 final proposal by p1.
    
    If approach=='repeated_rule_based':
      - We start with a *random deal* (rather than p1's best).
      - Then each round the chosen agent modifies that deal via repeated_rule_based improvement.
      - The final round is forced to p1 as the proposer.

    Returns:
      final_deal,
      negotiation_log (list of (proposer, deal, round_num))
    """
    if seed is not None:
        random.seed(seed)

    PLAYERS = list(utilities.keys())
    p1 = "p1"
    p2 = "p2"

    issue_names = ISSUE_NAMES  # E.g. ["A","B","C","D","E"]

    # 1. START with a *random* deal (the description explicitly says so)
    initial_deal = random.choice(ALL_DEALS)
    # initial_deal = dict(INITIAL_DEAL)
    # select the best deal for p1
    # initial_deal = max(ALL_DEALS, 
                    #   key=lambda d: get_utility(p1, d, utilities, ISSUE_NAMES))
    current_proposal = dict(initial_deal)
    negotiation_log = [(p1, current_proposal, 0)]  # we can say p1 "proposed" it at round 0

    # 2. Create a round assignment that ensures the last agent is p1
    round_assignment = randomize_agents_order(utilities, 'p1', R)

    # 3. R rounds
    for t in range(1, R+1):
        proposer = round_assignment[t-1]

        if approach == 'repeated_rule_based':
            new_proposal = generate_proposal_repeated_rule_based(
                player_name=proposer,
                current_deal=current_proposal,
                utilities=utilities,
                issue_names=issue_names,
                current_round=t
            )
        else:
            raise NotImplementedError("Only repeated_rule_based is implemented here.")

        negotiation_log.append((proposer, new_proposal, t))
        current_proposal = new_proposal

    # 4. Final proposal by p1 at round (R+1)
    #    (We apply the same repeated_rule_based improvement, with p1 as the agent.)
    final_deal = generate_proposal_repeated_rule_based(
        player_name=p1,
        current_deal=current_proposal,
        utilities=utilities,
        issue_names=issue_names,
        current_round=R+1
    )
    negotiation_log.append((p1, final_deal, R+1))

    # 5. Final acceptance check
    final_acceptances = []
    for player in PLAYERS:
        # needed_util = time_based_target_util(player, R+1, R, utilities)
        needed_util = get_threshold(player, utilities)
        if get_utility(player, final_deal, utilities, issue_names) >= needed_util:
            final_acceptances.append(player)

    p1_ok = (p1 in final_acceptances)
    p2_ok = (p2 in final_acceptances)
    passing_5of6 = (p1_ok and p2_ok and len(final_acceptances) >= 5)
    passing_6of6 = (len(final_acceptances) == len(PLAYERS))

    print(f"=== Approach: {approach} ===")
    if passing_5of6:
        print("[5/6-Way] Deal Achieved on final proposal.")
    else:
        print("No 5/6 acceptable final deal.")

    if passing_6of6:
        print("[6-Way] All players accepted!")
    else:
        print("Not all players accepted.")

    return final_deal, negotiation_log


# -------------------------------------------------------------------
# 7. Example usage for 100 runs
# -------------------------------------------------------------------
INITIAL_DEAL = None

def repeated_rule_based_approach(game_dir):
    """
    This replaces the multi_sample_consensus_approach with the repeated_rule_based approach.
    """
    global ISSUE_NAMES, ISSUE_DIMENSIONS, ALL_DEALS, ROUNDS, INITIAL_DEAL

    # Adjust paths as needed
    game_dir = 'our_games_descriptions/'+game_dir
    if not os.path.exists(game_dir):
        print(f"Game directory {game_dir} not found.")
        sys.exit(1)
    output_dir = os.path.join(game_dir, "output_reproduce/baselines", "repeated_rule_based")

    # copy scores_files to output_dir
    if os.path.exists(os.path.join(output_dir, "scores_files")):
        shutil.rmtree(os.path.join(output_dir, "scores_files"))
    shutil.copytree(os.path.join(game_dir, "scores_files"), os.path.join(output_dir, "scores_files"))
    # copy config.txt
    shutil.copy2(os.path.join(game_dir, "config.txt"), os.path.join(output_dir, "config.txt"))

    

    # Load environment
    full_names, utilities, PLAYERS = load_utilities_and_config(game_dir)

    # Infer ISSUE_DIMENSIONS from the utility data (assuming 5 issues labeled A..E)
    ISSUE_NAMES = ["A", "B", "C", "D", "E"]
    ISSUE_DIMENSIONS = {}
    for idx, issue in enumerate(ISSUE_NAMES):
        # # of possible sub-values = length of utilities['p1'][idx]
        dim_size = len(utilities['p1'][idx])
        ISSUE_DIMENSIONS[issue] = list(range(1, dim_size+1))

    # Build ALL_DEALS
    ALL_DEALS = []
    for combo in product(*[ISSUE_DIMENSIONS[i] for i in ISSUE_NAMES]):
        ALL_DEALS.append(dict(zip(ISSUE_NAMES, combo)))

    initial_deal_file = os.path.join(game_dir, "initial_deal.txt")
    # A1,B1,C4,D1,E5
    with open(initial_deal_file, "r") as f:
        test = f.read().strip().split(",")
        test = [int(i[1]) for i in test]
        INITIAL_DEAL = dict(zip(ISSUE_NAMES,test))

    ROUNDS = 24
    N_RUNS = 1000

    # We run 100 times
    for j in range(N_RUNS):
        final_deal, log = run_negotiation(
            utilities=utilities,
            full_names=full_names,
            R=ROUNDS,
            approach='repeated_rule_based',   # Our new approach
            seed=j
        )

        # Save results
        write_output(output_dir, f"history_{j}.json", log, full_names, ROUNDS)

if __name__ == "__main__":
    repeated_rule_based_approach("game3")