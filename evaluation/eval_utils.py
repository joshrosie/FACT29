import numpy as np
import os
import string
import re
from itertools import product


def load_setup(output_dir, agents_num, num_issues):

    with open(os.path.join(output_dir, 'config.txt'), 'r') as f:
        agents_config_file = f.readlines()

    issue_names = string.ascii_uppercase[:26]

    agents = {}
    role_to_agents = {}
    incentive_to_agents = {}

    assert len(agents_config_file) == agents_num

    for line in agents_config_file:
        agent_game_name, file_name, role, incentive, model = line.split(',')
        model = model.strip()
        agents[agent_game_name] = {
            'file_name': file_name, 'role': role, 'incentive': incentive}
        if not role in role_to_agents:
            role_to_agents[role] = []
        if not incentive in incentive_to_agents:
            incentive_to_agents[incentive] = []
        role_to_agents[role].append(agent_game_name)
        incentive_to_agents[incentive].append(agent_game_name)

    for agent in agents:
        scores = {}
        with open(os.path.join(output_dir, 'scores_files', agents[agent]['file_name'])+'.txt', 'r') as f:
            Lines = f.readlines()
            assert len(Lines) == num_issues + 1
            for i, line in enumerate(Lines):
                if i == len(Lines) - 1:  # min thresholds
                    scores['min'] = int(line.strip())
                    break
                scores[issue_names[i]] = [int(num.strip())
                                          for num in line.split(',')]
        agents[agent]['scores'] = scores

    for role in role_to_agents:
        if len(role_to_agents[role]) == 1:
            role_to_agents[role] = role_to_agents[role][0]

    for incentive in incentive_to_agents:
        if len(incentive_to_agents[incentive]) == 1:
            incentive_to_agents[incentive] = incentive_to_agents[incentive][0]

    return agents, role_to_agents, incentive_to_agents


def calculator(scores, deal, num_issues=5, return_array=False):
    if len(deal) != num_issues:
        return 0
    deal_sum = 0
    deal_array = []
    for issue in deal:
        if issue == '' or len(issue) != 2:
            return 0
        issue, number = issue[0], int(issue[1])
        if issue not in scores:
            return 0
        deal_sum += scores[issue][number-1]
        deal_array.append(scores[issue][number-1])
    if return_array:
        return deal_array
    return deal_sum


def extract_deal(answer, num_issues=5):
    answer = answer.replace('\n', '')
    issue_names = string.ascii_uppercase[:26]
    deal = []
    issues_suggested = 0
    for i in range(0, num_issues):
        option = re.findall(f'{issue_names[i]}[1-9]', answer, re.DOTALL)
        deal.append(option[0]) if option else deal.append('')
        if option:
            issues_suggested += 1

    return deal, issues_suggested


def get_all_deals(agents):
    first_agent_scores = next(iter(agents.values()))['scores']
    issues = [issue for issue in first_agent_scores.keys() if issue != 'min']
    num_options_per_issue = {issue: len(
        first_agent_scores[issue]) for issue in issues}

    # Generate all possible deals (Cartesian product of sub-issues)
    all_deals = product(
        *[[(issue, i + 1) for i in range(num_options_per_issue[issue])] for issue in issues])
    return list(all_deals)


def is_valid(role_to_agents, deal, agents):
    """
    Check if a deal is valid.
    A deal is valid if:
    - It is acceptable for all players (over their thresholds).
    - Both Player 1 (p1) and Player 2 (p2) must also accept the deal.
    """
    # Check for all agents if the deal meets their thresholds
    for agent_name, agent_data in agents.items():
        scores = agent_data['scores']
        threshold = scores['min']  # The threshold for this agent
        deal_score = calculator(scores, deal)

        if deal_score < threshold:
            return False  # Deal not acceptable for this agent

    for role in ['p1', 'p2']:
        agent_name = role_to_agents[role]
        scores = agents[agent_name]['scores']
        threshold = scores['min']
        deal_score = calculator(scores, deal)

        if deal_score < threshold:
            return False  # Deal not acceptable for Player 1 or Player 2

    return True


# construct feasibility set
def compute_feasibility_set(agents, all_deals):
    feasibility_set = []

    # Iterate over each deal
    for deal in all_deals:
        acceptable_count = 0
        key_players_accepted = set()

        for _, agent_data in agents.items():
            scores = agent_data['scores']
            # Compute the total score for this agent based on the deal
            agent_score = sum(
                # level - 1 to adjust for 0-based indexing
                scores[issue][level - 1]
                for issue, level in deal
            )

            # Check if the agent accepts the deal (score >= min threshold)
            if agent_score >= scores['min']:
                acceptable_count += 1
                # Check if key player (p1 or p2)
                if agent_data['role'] in {'p1', 'p2'}:
                    key_players_accepted.add(agent_data['role'])

        # Add the deal to the feasibility set if at least 5 agents accept, including p1 and p2
        if acceptable_count >= 5 and {'p1', 'p2'}.issubset(key_players_accepted):
            feasibility_set.append(deal)

    return feasibility_set
# construct pareto frontier


def get_pareto_frontier(agent_info, deals):
    def get_total_scores(deal):
        """
        Calculate the total scores for all agents for a given deal.
        """
        scores = {}
        for agent, details in agent_info.items():
            role_scores = details['scores']
            total_score = 0
            for option, choice in deal:
                total_score += role_scores[option][choice - 1]
            scores[agent] = total_score
        return scores

    def is_dominated(deal1_scores, deal2_scores):
        """
        Check if deal1 is dominated by deal2.
        """
        dominates = False
        for agent in deal1_scores:
            if deal2_scores[agent] > deal1_scores[agent]:
                dominates = True
            elif deal2_scores[agent] < deal1_scores[agent]:
                return False
        return dominates

    pareto_set = []

    for deal in deals:
        deal_scores = get_total_scores(deal)
        dominated = False

        for other_deal in deals:
            if deal == other_deal:
                continue

            other_deal_scores = get_total_scores(other_deal)
            if is_dominated(deal_scores, other_deal_scores):
                dominated = True
                break

        if not dominated:
            pareto_set.append(deal)

    return pareto_set


def compute_usw(deal, agents, num_issues):

    # FIRST IMPLEMENTATION:
    # This checks whether the deal is valid and returns the sum of the scores of all agents
    # Which does not provide intuitive results since many deals are not valid and we want to see a progression
    # For the sake of visulization I will obtain usw as the sum of the scores of all agents no matter the validity of the deal

    # Compute the utilitarian social welfare for a deal
    # if is_valid(deal, agents):
    #     print(f"Deal {deal} is valid")
    #     return sum([get_score(agent_name, deal) for agent_name in agents])
    # else:
    #     # Sum of thresholds
    #     return sum([agents[agent_name]['scores']['min'] for agent_name in agents])

    # SECOND IMPLEMENTATION:
    # This implementation returns the sum of the scores of all agents for a valid deal
    return sum([calculator(agents[agent_name]['scores'], deal, num_issues) for agent_name in agents])


def compute_optimal_usw(agents, all_deals, num_issues):
    # Initialize variables to track the optimal deal and its USW
    optimal_deal = None
    highest_usw = float('-inf')

    # Loop through all possible deals
    for deal in all_deals:
        # Compute the utilitarian social welfare for the current deal
        usw = compute_usw(deal, agents, num_issues)

        # Update the optimal deal if this deal has a higher USW
        if usw > highest_usw:
            highest_usw = usw
            optimal_deal = deal

    # Return the deal with the highest USW
    return optimal_deal, highest_usw


def compute_esw(deal, agents, num_issues):
    """
    Compute the egalitarian social welfare (ESW) for a given deal.
    ESW is the minimum utility achieved by any agent for the deal.

    Parameters:
    - deal: The deal being evaluated (list of tuples representing sub-issues).
    - agents: A dictionary of agents with their scores and thresholds.

    Returns:
    - Egalitarian social welfare (minimum utility among all agents).
    """
    # Initialize ESW to a large positive value
    esw = float('inf')

    # Compute utility for each agent and update ESW
    for agent_name, _ in agents.items():
        agent_utility = calculator(
            agents[agent_name]['scores'], deal, num_issues)
        esw = min(esw, agent_utility)  # Update ESW with the minimum utility

    return esw


def compute_optimal_esw(agents, all_deals, num_issues):
    """
    Compute the optimal egalitarian social welfare (ESW) and the corresponding deal.

    Parameters:
    - agents: A dictionary of agents with their scores and thresholds.

    Returns:
    - optimal_deal: The deal with the highest egalitarian social welfare.
    - highest_esw: The value of the highest ESW.
    """

    # Initialize variables to track the optimal deal and its ESW
    optimal_deal = None
    highest_esw = float('-inf')

    # Loop through all possible deals
    for deal in all_deals:
        # Compute the egalitarian social welfare for the current deal
        esw = compute_esw(deal, agents, num_issues)

        # Update the optimal deal if this deal has a higher ESW
        if esw > highest_esw:
            highest_esw = esw
            optimal_deal = deal

    # Return the deal with the highest ESW
    return optimal_deal, highest_esw


def compute_nash(deal, agents, num_issues, epsilon=0.001):
    """
    Compute the Nash Bargain Value (NBV) for a given deal.

    Parameters:
    - deal: The deal being evaluated (list of tuples representing sub-issues).
    - agents: A dictionary of agents with their scores and thresholds.

    Returns:
    - The Nash Bargain Value for the given deal. Returns 0 if any agent's utility is below their threshold.

    We compute the Weighted Nash Bargain Value (WNBV) for a deal.
    Adds a small penalty (epsilon) for utilities below thresholds.
    """

    wnbv = 1  # Initialize WNBV as 1 (product accumulator)

    for agent_name, agent_data in agents.items():
        scores = agent_data['scores']
        threshold = scores['min']
        utility = calculator(scores, deal, num_issues)

        # Add epsilon for utilities below thresholds
        wnbv *= max(utility - threshold, epsilon)

    return wnbv


def compute_max_nash(agents, all_deals, num_issues):
    """
    Compute the deal with the maximum Nash Bargain Value (NBV).

    Parameters:
    - agents: A dictionary of agents with their scores and thresholds.

    Returns:
    - optimal_deal: The deal with the highest Nash Bargain Value.
    - max_nbv: The maximum Nash Bargain Value.
    """

    # Initialize variables to track the optimal deal and its NBV
    optimal_deal = None
    max_nbv = float('-inf')

    # Loop through all possible deals
    for deal in all_deals:
        # Compute the Nash Bargain Value for the current deal
        nbv = compute_nash(deal, agents, num_issues)

        # Update the optimal deal if this deal has a higher NBV
        if nbv > max_nbv:
            max_nbv = nbv
            optimal_deal = deal

    # Return the deal with the highest NBV
    return optimal_deal, max_nbv


def compute_distance(deal1, deal2, method='usw', norm='l1'):
    # Compute the distance between two deals
    if method == 'usw':
        usw1 = compute_usw(deal1, agents)
        usw2 = compute_usw(deal2, agents)
        if norm == 'l1':
            return np.abs(usw1 - usw2)
        elif norm == 'l2':
            return np.linalg.norm(usw1 - usw2)
    elif method == 'nash':
        # TODO: Implement Nash distance
        return Exception("Nash distance not implemented yet")
    elif method == 'esw':
        if norm == 'l1':
            # d(deal_i, deal_j) = |min_p S_p(deal_i) - min_p S_p(deal_j)|
            return np.abs(compute_esw(deal1, agents) - compute_esw(deal2, agents))
        elif norm == 'l2':
            return np.linalg.norm(compute_esw(deal1, agents) - compute_esw(deal2, agents))
    elif method == 'hamming':
        if len(deal1) != len(deal2):
            raise ValueError("Deals must have the same number of elements.")
        differences = sum([abs(tup1[1] - tup2[1]) for tup1, tup2 in zip(deal1, deal2)])
        return differences
    else:
        return Exception("Invalid method")


# Change accordingly
OUTPUT_DIR = f'/Users/joshuarosenthal/Masters/FACT/FACT29/our_games_descriptions/base/output/our_outputs/base_Qwen2.5-72B-Instruct-GPTQ-Int4'
AGENTS_NUM = 6
ISSUES_NUM = 5

agents, role_to_agents, incentive_to_agents = load_setup(
    OUTPUT_DIR, AGENTS_NUM, ISSUES_NUM)
all_deals = get_all_deals(agents)
print(len(all_deals))
feasibility_set = compute_feasibility_set(agents, all_deals)

pareto_frontier = get_pareto_frontier(agents, feasibility_set)
# Compute metrics for all deals
print(feasibility_set[0])
print(compute_max_nash(agents,all_deals,5)[0])
print(compute_distance(feasibility_set[0],compute_max_nash(agents,all_deals,5)[0],'hamming'))
