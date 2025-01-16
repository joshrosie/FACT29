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


def get_pareto_frontier(feasibility_set, agents):
    def compute_scores(deal):
        """Compute the scores for all agents for a given deal."""
        scores = {}
        for agent_name, agent_data in agents.items():
            agent_scores = agent_data['scores']
            scores[agent_name] = sum(
                agent_scores[issue][level - 1]  # Adjust level to 0-based index
                for issue, level in deal
            )
        return scores

    pareto_frontier = []

    for deal in feasibility_set:
        current_scores = compute_scores(deal)
        is_dominated = False

        for other_deal in feasibility_set:
            if deal == other_deal:
                continue

            other_scores = compute_scores(other_deal)

            if all(
                other_scores[agent] >= current_scores[agent] and
                any(other_scores[agent] > current_scores[agent]
                    for agent in agents)
                for agent in agents
            ):
                is_dominated = True
                break

        if not is_dominated:
            pareto_frontier.append((deal, current_scores))

    return pareto_frontier


game = 'base_rewritten'

# Change accordingly
OUTPUT_DIR = f'/Users/joshuarosenthal/Masters/FACT/FACT29/our_games_descriptions/base/output/our_outputs/base_Qwen2.5-72B-Instruct-GPTQ-Int4'
AGENTS_NUM = 6
ISSUES_NUM = 5

agents, role_to_agents, incentive_to_agents = load_setup(
    OUTPUT_DIR, AGENTS_NUM, ISSUES_NUM)

feasibility_set = compute_feasibility_set(agents, get_all_deals(agents))
print(len(get_pareto_frontier(feasibility_set, agents)))
# print(get_all_deals(agents))
