import numpy as np
import os
import string
import re
from itertools import product


#####################
# 1) LOADING SETUP
#####################
def load_setup(output_dir, agents_num, num_issues):
    with open(os.path.join(output_dir, "config.txt"), "r") as f:
        agents_config_file = f.readlines()

    issue_names = string.ascii_uppercase[:26]

    agents = {}
    role_to_agents = {}
    incentive_to_agents = {}

    assert len(agents_config_file) == agents_num

    for line in agents_config_file:
        agent_game_name, file_name, role, incentive, model = line.split(",")
        model = model.strip()
        agents[agent_game_name] = {
            "file_name": file_name,
            "role": role,
            "incentive": incentive,
        }

        if role not in role_to_agents:
            role_to_agents[role] = []
        if incentive not in incentive_to_agents:
            incentive_to_agents[incentive] = []
        role_to_agents[role].append(agent_game_name)
        incentive_to_agents[incentive].append(agent_game_name)

    for agent in agents:
        scores = {}
        with open(
            os.path.join(output_dir, "scores_files", agents[agent]["file_name"])
            + ".txt",
            "r",
        ) as f:
            Lines = f.readlines()
            assert len(Lines) == num_issues + 1
            for i, line in enumerate(Lines):
                if i == len(Lines) - 1:  # min thresholds
                    scores["min"] = int(line.strip())
                    break
                scores[issue_names[i]] = [int(num.strip()) for num in line.split(",")]
        agents[agent]["scores"] = scores

    # If there's only one agent in a given role/incentive, store the string rather than a list
    for role in role_to_agents:
        if len(role_to_agents[role]) == 1:
            role_to_agents[role] = role_to_agents[role][0]

    for incentive in incentive_to_agents:
        if len(incentive_to_agents[incentive]) == 1:
            incentive_to_agents[incentive] = incentive_to_agents[incentive][0]

    return agents, role_to_agents, incentive_to_agents

#####################
# 2) CALCULATOR -> Score calculating function
#####################
def calculator(scores, deal, num_issues=5, return_array=False):
    """
    Summation of the agent's score for each issue in the deal.
    deal: list of (issue_letter, level) e.g. ('A', 1)
    scores: dict of the form { 'A': [...], 'B': [...], ..., 'min': 55 }
    """
    if len(deal) != num_issues:
        return 0
    deal_sum = 0
    deal_array = []
    for issue_letter, level in deal:
        if issue_letter not in scores:
            print(f"Error: Issue {issue_letter} not in scores.")
            return 0
        # level is 1-based index, so adjust to 0-based for the array
        issue_score = scores[issue_letter][level - 1]
        deal_sum += issue_score
        deal_array.append(issue_score)
    if return_array:
        return deal_array
    return deal_sum



def calculator_old(scores, deal, num_issues=5):
    if len(deal) != num_issues:
        return 0
    deal_sum = 0
    for issue in deal:
        if issue == "" or len(issue) != 2:
            return 0
        issue, number = issue[0], int(issue[1])
        if issue not in scores:
            return 0
        deal_sum += scores[issue][number - 1]
    return deal_sum


#####################
# 3) GET ALL DEALS
#####################
def get_all_deals(agents):
    """
    Generate all possible deals (Cartesian product of sub-issues).
    Returns a list of deals, each a tuple of (issue_letter, chosen_level).
    """
    first_agent_scores = next(iter(agents.values()))["scores"]
    # Exclude "min"
    issues = [issue for issue in first_agent_scores.keys() if issue != "min"]
    num_options_per_issue = {issue: len(first_agent_scores[issue]) for issue in issues}

    all_deals_iter = product(
        *[
            [(issue, i + 1) for i in range(num_options_per_issue[issue])]
            for issue in issues
        ]
    )
    # product(...) yields an iterator of tuples-of-tuples
    return list(all_deals_iter)


def extract_deal(answer, num_issues=5):
    """
    Extract the deal from the agent's answer.

    Parameters:
    - answer: The agent's answer containing the deal.
    - num_issues: The number of issues in the negotiation.

    Returns:
    - deal: A list of sub-issues representing the deal.
    - issues_suggested: The number of issues suggested in the deal.
    """
    answer = answer.replace("\n", "")
    issue_names = string.ascii_uppercase[:26]
    deal = []
    issues_suggested = 0
    for i in range(0, num_issues):
        option = re.findall(f"{issue_names[i]}[1-9]", answer, re.DOTALL)
        deal.append(option[0]) if option else deal.append("")
        if option:
            issues_suggested += 1

    return deal, issues_suggested


def format_deal(deal, num_issues=5):
    """
    Input: List (e.g. ['A1', 'B2', 'C3', 'D4', 'E5'])
    Output: Tuple (e.g. (('A', 1), ('B', 2), ('C', 3), ('D', 4), ('E', 5)))
    """

    if len(deal) != num_issues:
        return None

    issue_names = string.ascii_uppercase[:26]
    formatted_deal = []
    for i in range(num_issues):
        issue, level = deal[i][0], int(deal[i][1])
        formatted_deal.append((issue, level))
    return tuple(formatted_deal)


#####################
# 4) COMPUTING FEASIBILITY
#####################
def compute_feasibility_set(agents, all_deals):
    """
    Feasibility rule in your code:
    - A deal is feasible if >=5 agents accept (score >= min)
    - p1 and p2 are definitely among those who accept
    """
    # feasibility_set = []

    # for deal in all_deals:
    #     acceptable_count = 0
    #     key_players_accepted = set()

    #     for agent_name, agent_data in agents.items():
    #         scores = agent_data["scores"]
    #         agent_score = calculator(scores, deal, num_issues=len(deal))
    #         if agent_score >= scores["min"]:
    #             acceptable_count += 1
    #             if agent_data["role"] in {"p1", "p2"}:
    #                 key_players_accepted.add(agent_data["role"])

    #     # If at least 5 accept, and p1 + p2 accept, it's feasible
    #     if acceptable_count >= 5 and {"p1", "p2"}.issubset(key_players_accepted):
    #         feasibility_set.append(deal)

    # return feasibility_set

    return [deal for deal in all_deals if is_feasible(agents, deal)]


def is_feasible(agents, deal):
    """
    Feasibility rule in your code:
    - A deal is feasible if >=5 agents accept (score >= min)
    - p1 and p2 are definitely among those who accept
    """
    acceptable_count = 0
    key_players_accepted = set()

    for agent_name, agent_data in agents.items():
        scores = agent_data["scores"]
        agent_score = calculator(scores, deal, num_issues=len(deal))
        if agent_score > scores["min"]:
            acceptable_count += 1
            if agent_data["role"] in {"p1", "p2"}:
                key_players_accepted.add(agent_data["role"])

    # If at least 5 accept, and p1 + p2 accept, it's feasible
    return acceptable_count >= 5 and {"p1", "p2"}.issubset(key_players_accepted)


#####################
# 5) SOCIAL WELFARE
#####################
def compute_usw(deal, agents, num_issues=5):
    """
    Utilitarian Social Welfare = sum of all agent utilities for 'deal'.
    """
    return sum(
        calculator(agent_data["scores"], deal, num_issues)
        for agent_data in agents.values()
    )


def compute_esw(deal, agents, num_issues=5):
    """
    Egalitarian Social Welfare = min of all agent utilities for 'deal'.
    """
    esw = float("inf")
    for agent_data in agents.values():
        agent_utility = calculator(agent_data["scores"], deal, num_issues)
        esw = min(esw, agent_utility)
    return esw


def compute_nash(deal, agents, num_issues=5, epsilon=0.001):
    """
    "Nash Bargain Value" = product( max(0, utility_i - threshold_i) ) or similar.
    But your code uses: product( max(utility - threshold, epsilon) ).
    """
    nbv = 1.0
    for agent_data in agents.values():
        scores = agent_data["scores"]
        utility = calculator(scores, deal, num_issues)
        nbv *= max(utility, epsilon)
    return nbv


def utility_player_usw(deal, agents, player, num_issues=5):
    """
    Utilitarian Social Welfare = sum of all agent utilities for 'deal'.
    """
    return calculator(agents[player]["scores"], deal, num_issues)


def utility_player_esw(deal, agents, player, num_issues=5):
    """
    Egalitarian Social Welfare = min of all agent utilities for 'deal'.
    """
    # Get the utility of each agent for the deal
    agent_utilities = [
        calculator(agent_data["scores"], deal, num_issues)
        for agent_data in agents.values()
    ]
    # Get the utility the minimum utility
    return min(agent_utilities)


def utility_player_nash(deal, agents, player, num_issues=5, epsilon=0.001):
    """
    "Nash Bargain Value" = product( max(0, utility_i - threshold_i) ) or similar.
    But your code uses: product( max(utility - threshold, epsilon) ).
    """
    utility = calculator(agents[player]["scores"], deal, num_issues, return_array=True)
    return np.prod([max(utility[i], epsilon) for i in range(num_issues)])


#####################
# 6) OPTIMAL DEALS UNDER DIFFERENT METRICS
#####################
def compute_optimal_usw(agents, all_deals, num_issues=5):
    highest_usw = float("-inf")
    best_deals = []
    for deal in all_deals:
        usw = compute_usw(deal, agents, num_issues)
        if usw > highest_usw:
            highest_usw = usw
            best_deals = [deal]
        elif usw == highest_usw:
            best_deals.append(deal)
    return best_deals, highest_usw


def compute_optimal_esw(agents, all_deals, num_issues=5):
    highest_esw = float("-inf")
    best_deals = []
    for deal in all_deals:
        esw = compute_esw(deal, agents, num_issues)
        if esw > highest_esw:
            highest_esw = esw
            best_deals = [deal]
        elif esw == highest_esw:
            best_deals.append(deal)
    return best_deals, highest_esw


def compute_optimal_nash(agents, all_deals, num_issues=5):
    max_nbv = float("-inf")
    best_deals = []
    for deal in all_deals:
        nbv = compute_nash(deal, agents, num_issues)
        if nbv > max_nbv:
            max_nbv = nbv
            best_deals = [deal]
        elif nbv == max_nbv:
            best_deals.append(deal)
    return best_deals, max_nbv


#####################
# 7) VECTOR VARIATION OF THE SCORE FUNCTIONS
#####################
def compute_usw_vector(deal, agents, num_issues=5):
    """
    Return a vector (array of length 'num_issues') for the deal,
    where each element is the sum of all agents' partial-utility
    for that specific issue.
    """
    # Initialize a vector of zeros, one per issue
    # (assuming the 'deal' is something like [('A', 1), ('B', 2), ...])
    vector_score = [0] * num_issues

    for issue_letter, level_idx in deal:
        # 'issue_index' depends on how you map 'A','B','C' -> 0,1,2, etc.
        # But let's assume each position in 'deal' matches an index in [0..num_issues-1].
        pass

    # We'll need to find the position of each (issue_letter, level_idx).

    for i, (issue_letter, level_idx) in enumerate(deal):
        # Summation over all agents
        sum_over_agents = 0
        for agent_data in agents.values():
            # agent_data["scores"][issue_letter] is a list
            # level_idx is 1-based, so subtract 1
            partial_utility = agent_data["scores"][issue_letter][level_idx - 1]
            sum_over_agents += partial_utility

        vector_score[i] = sum_over_agents

    return vector_score


def compute_esw_vector(deal, agents, num_issues=5):
    """
    Vector of length 'num_issues' where each entry is the *minimum* of
    that issue's partial-utility across all agents.
    """
    vector_score = [0] * num_issues
    for i, (issue_letter, level_idx) in enumerate(deal):
        # Initialize min_value to a large number
        min_val = float("inf")
        for agent_data in agents.values():
            val = agent_data["scores"][issue_letter][level_idx - 1]
            if val < min_val:
                min_val = val
        vector_score[i] = min_val
    return vector_score


def compute_nash_vector(deal, agents, num_issues=5):
    """
    Vector of length 'num_issues' where each entry is the product of that
    issue's partial-utility across all agents.
    """
    vector_score = [1] * num_issues
    for i, (issue_letter, level_idx) in enumerate(deal):
        prod_val = 1
        for agent_data in agents.values():
            val = agent_data["scores"][issue_letter][level_idx - 1]
            prod_val *= val
        vector_score[i] = prod_val
    return vector_score


#####################
# 8) DISTANCE BETWEEN TWO DEALS
#####################
def compute_distance(deal1, deal2, agents, metric="usw", norm="l1", num_issues=5):
    """
    Computes the distance between two deals (deal1, deal2) under different frameworks:

      1. Score-space distance (usw, esw, or nash):
         - Both are scalar utilities across the entire deal
         - The 'norm' for a scalar difference is effectively absolute difference in 'l1' or 'l2'
      2. Hamming (deal-space) distance:
         - Summation of |level_i - level_j| for each issue.

    Args:
        deal1, deal2: Each is a list or tuple of (issue_letter, choice).
        agents: dict of agent data (with "scores" etc.).
        metric: "usw", "esw", "nash", or "hamming"
        norm: "l1" (absolute difference), "l2" is same for scalars,
              not used for "hamming" except if we wanted to define something else.
        num_issues: number of issues.

    Returns:
        A float (or int) indicating the distance.
    """
    # 1. Hamming distance in the deal space
    if metric.lower() == "hamming":
        if len(deal1) != len(deal2):
            raise ValueError("Deals must have the same number of issues.")
        # sum of differences in levels
        dist = 0
        for (issue1, lvl1), (issue2, lvl2) in zip(deal1, deal2):
            if issue1 != issue2:
                # If the issue letters differ, either reorder or assume the same ordering in both deals
                raise ValueError(f"Issue mismatch: {issue1} != {issue2}")
            dist += abs(lvl1 - lvl2)
        return dist

    # 2. Score-space distance (usw, esw, nash -> each yields a single scalar)
    if metric.lower() == "usw":
        score1 = compute_usw_vector(deal1, agents, num_issues)
        score2 = compute_usw_vector(deal2, agents, num_issues)
    elif metric.lower() == "esw":
        score1 = compute_esw_vector(deal1, agents, num_issues)
        score2 = compute_esw_vector(deal2, agents, num_issues)
    elif metric.lower() == "nash":
        score1 = compute_nash_vector(deal1, agents, num_issues)
        score2 = compute_nash_vector(deal2, agents, num_issues)
    else:
        raise ValueError(f"Unknown metric: {metric}")

    # Return the l-norm
    diff = np.array(score1) - np.array(score2)
    if norm.lower() == "l1":
        return np.sum(np.abs(diff))
    elif norm.lower() == "l2":
        return np.sqrt(np.sum(diff**2))
    elif norm == "linf":
        return np.max(np.abs(diff))
    else:
        raise ValueError(f"Unknown norm: {norm}")


#####################
# 9) PRE-HOC ANALYSIS
#####################
def get_sparsity(agents):
    """
    Get the sparsity (%) of the agents' scores.
    That is, perecentage of values in the scores that are zero.
    """
    total_values = 0
    zero_values = 0
    for agent_data in agents.values():
        for issue_scores in agent_data["scores"].values():
            # Exclude the "min" key
            if isinstance(issue_scores, int):
                continue
            total_values += len(issue_scores)
            zero_values += len([val for val in issue_scores if val == 0])
    return zero_values / total_values


def iou(scores1, scores2):
    """
    Intersection over Union (IoU) of two lists of scores.
    That is, intersection for issue 1 sub-issues and issue 2 sub-issues.
    """
    intersection = sum(min(s1, s2) for s1, s2 in zip(scores1, scores2))
    union = sum(max(s1, s2) for s1, s2 in zip(scores1, scores2))
    if union == 0:
        return 0.0
    return intersection / union


def get_iou(agents):
    """
    Get the Intersection over Union (IoU) of the agents' scores.
    We return the average pair-wise IoU of the agents' scores
    """
    iou_sum = 0
    num_pairs = 0
    for agent_data1 in agents.values():
        for agent_data2 in agents.values():
            if agent_data1 == agent_data2:
                continue
            for issue_scores1, issue_scores2 in zip(
                agent_data1["scores"].values(), agent_data2["scores"].values()
            ):
                # Exclude the "min" key
                if isinstance(issue_scores1, int):
                    continue
                iou_sum += iou(issue_scores1, issue_scores2)
                num_pairs += 1
    return iou_sum / num_pairs


# # EXAMPLE USAGE
# # Change accordingly
# OUTPUT_DIR = f"/Users/administrador/Desktop/amsterdam/1.1/FACT/FACT29/our_games_descriptions/base/output/our_outputs/base_Qwen2.5-72B-Instruct-GPTQ-Int4"
# AGENTS_NUM = 6
# ISSUES_NUM = 5

# agents, role_to_agents, incentive_to_agents = load_setup(
#     OUTPUT_DIR, AGENTS_NUM, ISSUES_NUM
# )
# all_deals = get_all_deals(agents)
# feasibility_set = compute_feasibility_set(agents, all_deals)


# print(f"Number of all deals: {len(all_deals)}")
# print(f"Number of feasible deals: {len(feasibility_set)}")

# # Pick two sample deals
# dealA = all_deals[0]
# dealB = all_deals[10]

# # Get names of p1 and p2
# p1_name = role_to_agents["p1"]
# p2_name = role_to_agents["p2"]

# # Get utilities for player1 and player2
# player1_usw = utility_player_usw(dealA, agents, p1_name, num_issues=ISSUES_NUM)
# player2_usw = utility_player_usw(dealA, agents, p2_name, num_issues=ISSUES_NUM)
# player1_esw = utility_player_esw(dealA, agents, p1_name, num_issues=ISSUES_NUM)
# player2_esw = utility_player_esw(dealA, agents, p2_name, num_issues=ISSUES_NUM)
# player1_nash = utility_player_nash(dealA, agents, p1_name, num_issues=ISSUES_NUM)
# player2_nash = utility_player_nash(dealA, agents, p2_name, num_issues=ISSUES_NUM)

# print(f"Player 1 USW: {player1_usw}")
# print(f"Player 2 USW: {player2_usw}")
# print(f"Player 1 ESW: {player1_esw}")
# print(f"Player 2 ESW: {player2_esw}")
# print(f"Player 1 Nash: {player1_nash}")
# print(f"Player 2 Nash: {player2_nash}")


# print(f"Deal A: {(dealA)}")
# print(compute_esw(dealA, agents, num_issues=ISSUES_NUM))

# dist_usw_l1 = compute_distance(
#     dealA, dealB, agents, metric="usw", norm="l1", num_issues=ISSUES_NUM
# )
# dist_esw_l1 = compute_distance(
#     dealA, dealB, agents, metric="esw", norm="l1", num_issues=ISSUES_NUM
# )
# dist_usw_l2 = compute_distance(
#     dealA, dealB, agents, metric="usw", norm="l2", num_issues=ISSUES_NUM
# )
# dist_esw_l2 = compute_distance(
#     dealA, dealB, agents, metric="esw", norm="l2", num_issues=ISSUES_NUM
# )
# dist_hamming = compute_distance(
#     dealA, dealB, agents, metric="hamming", num_issues=ISSUES_NUM
# )

# print(f"Deal A: {dealA}")
# print(f"Deal B: {dealB}")
# print(f"Distance USW (L1): {dist_usw_l1}")
# print(f"Distance ESW (L1): {dist_esw_l1}")
# print(f"Distance USW (L2): {dist_usw_l2}")
# print(f"Distance ESW (L2): {dist_esw_l2}")
# print(f"Distance Hamming: {dist_hamming}")
