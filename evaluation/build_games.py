import numpy as np
import argparse
from scipy.optimize import minimize
from eval_utils import get_iou, load_setup
import matplotlib.pyplot as plt
import os
import shutil


def check_sum_of_utilities(agents, total_utility):
    """
    Check if the sum of utilities for each agent equals the total utility.
    """
    for agent_name, agent_data in agents.items():
        total_x = 0
        for issue, scores in agent_data["scores"].items():
            total_x += np.max(scores)
        total = np.sum([np.max(scores)
                       for scores in agent_data["scores"].values()])
        print(total)
        if not np.isclose(total, total_utility, atol=1e-6):
            print(f"Sum of utilities for {agent_name} is incorrect: {
                  total} != {total_utility}")
            return False
    print("Sum of utilities for all agents is correct.")
    return True


def check_iou(agents, target_iou, tolerance=0.01):
    """
    Check if the IoU of the agents' scores is close to the target.
    """
    avg_iou = get_iou(agents, use_numpy=True)

    if abs(avg_iou - target_iou) > tolerance:
        print(f"Average IoU is outside tolerance: {avg_iou} != {target_iou}")
        return False
    print(f"Average IoU is within tolerance: {avg_iou} ≈ {target_iou}")
    return True


def softmax(x, temperature=0.5):
    e_x = np.exp((x - np.max(x)) / temperature)
    return e_x / e_x.sum(axis=0)


def generate_utility_functions(
    num_agents,
    subissues_per_issue,
    total_utility,
    target_iou,
    seed_dir=None,
    tol=1e-7,
    lambda_reg=0
):
    """
    Generate utility functions for agents with constraints on:
      - total utility
      - target IoU
      - *Sparsity*: If an initial weight is 0, it remains 0.
      - *Ordering*: Preserve subissue ordering per issue.
    """

    # ----------------------------------------------
    # 1. Initialize agents with random scores
    #    (Or load from seed_dir if needed)
    # ----------------------------------------------
    if seed_dir:
        # Load scores from seed_dir directory
        agents, role_to_agents, incentives_to_agents = load_setup(
            seed_dir, num_agents, len(subissues_per_issue))
        for agent_name, agent_data in agents.items():

            agent_data["threshold"] = agent_data["scores"]["min"]
            del agent_data["scores"]["min"]
    else:
        agents = {}
        for i in range(num_agents):
            # For each agent, create a dict of issues->scores
            # and store a "threshold" in parallel
            scores_for_issues = {}
            for j, s in enumerate(subissues_per_issue):
                # Random scores in [0, 1)
                scores_for_issues[f"issue_{j}"] = np.random.rand(s)

            threshold = np.random.normal(0.5, 0.1, 1) * total_utility

            agents[f"agent_{i}"] = {
                "scores": scores_for_issues,
                "threshold": threshold,
            }

    # ----------------------------------------------
    # 2. Build our "initial" flattened array and
    #    record subindex boundaries for each agent/issue.
    # ----------------------------------------------
    # Use a mask to keep track of variable we want to regularize.
    # These are the variables that are initially near zero.
    # This is because we want to preserve sparsity.
    flat_init_scores = []
    index_map = []
    # True for variables initially near zero (to be regularized)
    near_zero_mask = []
    for agent_name, agent_data in agents.items():
        for issue_name, scores in agent_data["scores"].items():
            start_idx = len(flat_init_scores)
            flat_init_scores.extend(scores)
            end_idx = len(flat_init_scores)
            index_map.append((agent_name, issue_name, start_idx, end_idx))
            # Identify near-zero variables for regularization
            near_zero_mask.extend([abs(score) < tol for score in scores])

    flat_init_scores = np.array(flat_init_scores)
    near_zero_mask = np.array(near_zero_mask)

    # ----------------------------------------------
    # 3. Define the objective: Minimize deviation
    #    from the target IoU
    # ----------------------------------------------
    # def objective(flat_scores):
    #     # Reshape flattened scores into the agents' utility structure
    #     # so we can compute IoU
    #     for (agent_name, issue_name, sidx, eidx) in index_map:
    #         agents[agent_name]["scores"][issue_name] = flat_scores[sidx:eidx]

    #     avg_iou = get_iou(agents, use_numpy=True)
    #     # Our objective is to push avg_iou close to target_iou
    #     return abs(avg_iou - target_iou)

    def objective(flat_scores, sharpness_weight=1e-3):
        # Reshape scores into agent structure
        for (agent_name, issue_name, sidx, eidx) in index_map:
            agents[agent_name]["scores"][issue_name] = flat_scores[sidx:eidx]

        # 1. Compute IoU
        avg_iou = get_iou(agents, use_numpy=True)
        iou_term = abs(avg_iou - target_iou)

        # 2. Regularization term (original sparsity term)
        diff = flat_scores - flat_init_scores
        reg_term = lambda_reg * np.sum(np.abs(diff[near_zero_mask]))

        # 3. Encourage "sharp" distributions to approximate argmax
        sharpness_penalty = 0
        for (agent_name, issue_name, sidx, eidx) in index_map:
            scores = flat_scores[sidx:eidx]
            max_score = np.max(scores)
            sharpness_penalty += np.sum((scores - max_score) ** 2)
        sharpness_term = sharpness_weight * sharpness_penalty

        return iou_term + reg_term + sharpness_term

    # ----------------------------------------------
    # 4. Constraints
    #
    #    4.1. Sum-of-max-subissues = total_utility
    #         (or = 100, whichever your scenario is)
    #
    #    4.2. Sparsity: If initial score ~ 0, fix
    #         bounds to [0, 0].
    #
    #    4.3. Ordering: If initial subissue_i > subissue_j,
    #         enforce final_i >= final_j.
    # ----------------------------------------------
    constraints = []
    bounds = [None] * len(flat_init_scores)

    # 4.1 Build total-utility constraints for each agent
    #     Here, we interpret your "sum of utilities" constraint
    #     as: sum_of_max_subissue(agent) = total_utility.
    #     Adjust as needed if your constraint differs.
    def make_sum_of_max_constraint(agent_name, temperature=0.1):
        indices_by_issue = {}
        for (a_name, issue_name, sidx, eidx) in index_map:
            if a_name == agent_name:
                indices_by_issue.setdefault(
                    issue_name, []).append((sidx, eidx))

        def _constraint_fun(x):
            sum_soft = 0
            for issue_name, segs in indices_by_issue.items():
                sidx, eidx = segs[0]
                issue_vals = x[sidx:eidx]
                weights = softmax(issue_vals, temperature)
                sum_soft += np.dot(issue_vals, weights)
            return sum_soft - total_utility

        return _constraint_fun

    agent_names = [agent_name for agent_name in agents.keys()]
    for agent_name in agent_names:
        constraints.append({
            'type': 'eq',
            'fun': make_sum_of_max_constraint(agent_name)
        })

    # 4.2 Sparsity + 4.3 Ordering
    #     We do them in a single pass for each agent and each issue.
    for (agent_name, issue_name, sidx, eidx) in index_map:
        init_vals = flat_init_scores[sidx:eidx]
        # subissue_count = len(init_vals)

        # 4.2. If a weight is zero (within tolerance), lock it to zero by bounds DEPRECATED
        # for local_idx, val in enumerate(init_vals):
        #     global_idx = sidx + local_idx
        #     if abs(val) < tol:
        #         # Force final value to remain zero
        #         bounds[global_idx] = (0.0, 0.0)
        #     else:
        #         # Otherwise nonnegative
        #         bounds[global_idx] = (0.0, None)

        # 4.3. Preserve ordering among subissues
        #      If init_vals[i] > init_vals[j] => final_vals[i] >= final_vals[j].
        #      If init_vals[i] < init_vals[j] => final_vals[i] <= final_vals[j].
        #      We skip ties.
        for i in range(len(init_vals)):
            for j in range(i + 1, len(init_vals)):
                if abs(init_vals[i] - init_vals[j]) < tol:
                    continue
                elif init_vals[i] > init_vals[j]:
                    # Enforce final_i >= final_j + tol
                    def ordering_ij(x, g_i=sidx+i, g_j=sidx+j, eps=tol):
                        return x[g_i] - x[g_j] - eps
                    constraints.append({'type': 'ineq', 'fun': ordering_ij})
                else:
                    # Enforce final_j >= final_i + tol
                    def ordering_ji(x, g_i=sidx+i, g_j=sidx+j, eps=tol):
                        return x[g_j] - x[g_i] - eps
                    constraints.append({'type': 'ineq', 'fun': ordering_ji})

    # At this point, any indices that are not set in bounds
    # must be non-negative; fill them in (though we did it above,
    # let's just ensure no None remain).
    for i, b in enumerate(bounds):
        if b is None:
            bounds[i] = (0.0, None)

    # ----------------------------------------------
    # 5. Perform optimization using SLSQP
    # ----------------------------------------------
    iou_history = []

    def callback(xk):
        # Reshape xk into the agent structure
        for (agent_name, issue_name, sidx, eidx) in index_map:
            agents[agent_name]["scores"][issue_name] = xk[sidx:eidx]
        # Compute IoU
        avg_iou = get_iou(agents, use_numpy=True)
        iou_history.append(avg_iou)
        print(f"Iteration {len(iou_history)}: IoU = {avg_iou:.4f}")

    result = minimize(
        objective,
        flat_init_scores,   # Initial guess
        constraints=constraints,
        bounds=bounds,
        method='SLSQP',
        callback=callback,
        options={'maxiter': 10000, 'disp': True},
    )

    # ----------------------------------------------
    # 6. Update the agent dictionary with the
    #    optimized scores
    # ----------------------------------------------
    final_scores = result.x
    for (agent_name, issue_name, sidx, eidx) in index_map:
        agents[agent_name]["scores"][issue_name] = final_scores[sidx:eidx]

    return agents, iou_history


def adjust_agent_scores(agents):
    """
    Floors all utility scores for each agent, calculates the difference between
    the total utility and 100, and adds the difference to the maximum sub-issue of
    random issues.

    Note: This function will invariably decrease the average IoU of the agents so
    set the target IoU accordingly.

    Parameters:
        agents (dict): Agent data containing scores for each issue.

    Returns:
        dict: Updated agent data with adjusted scores.
    """
    adjusted_agents = {}
    for agent_name, agent_data in agents.items():

        # Floor all scores
        # max_index = np.argmax([np.max(scores) for scores in agent_data["scores"].values()])
        floored_scores = {
            issue: np.floor(scores)
            for issue, scores in agent_data["scores"].items()
        }

        # Calculate the total utility
        total_utility = sum(np.sum(np.max(scores))
                            for scores in floored_scores.values())

        # Calculate the difference to 100
        utility_difference = 100 - total_utility
        print(f"Utility difference for {agent_name}: {utility_difference}")
        # Redistribute remaining utility mass randomly
        while utility_difference > 0:
            random_int = np.random.randint(len(floored_scores))
            issue = chr(ord('@')+(random_int+1))
            scores = floored_scores[issue]
            original_scores = agent_data["scores"][issue]
            max_index = np.argmax(original_scores)
            scores[max_index] += 1
            floored_scores[issue] = scores
            utility_difference -= 1

        # Update the agent's data
        adjusted_agents[agent_name] = {
            "scores": floored_scores,
            # Keep threshold unchanged
            "threshold": np.floor(agent_data["threshold"]),
            "file_name": agent_data["file_name"]
        }

    return adjusted_agents


def write_game(agents, inherited_directory, new_directory):
    """
    Copy required files/directories and write agent scores to new directory.
    """
    # Create target directory structure
    os.makedirs(new_directory, exist_ok=True)

    # Copy directory structure
    dirs_to_copy = ['individual_instructions']
    for dir_name in dirs_to_copy:
        src_dir = os.path.join(inherited_directory, dir_name)
        dst_dir = os.path.join(new_directory, dir_name)
        if os.path.exists(src_dir):
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
        else:
            print(f"Warning: Source directory {src_dir} not found")

    # Copy individual files
    files_to_copy = ['initial_deal.txt',
                     'global_instructions.txt', 'config.txt']
    for file_name in files_to_copy:
        src_file = os.path.join(inherited_directory, file_name)
        dst_file = os.path.join(new_directory, file_name)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
        else:
            print(f"Warning: Source file {src_file} not found")

    # Create scores directory
    scores_dir = os.path.join(new_directory, 'scores_files')
    os.makedirs(scores_dir, exist_ok=True)

    # Write agent score files
    for _, agent_data in agents.items():
        agent_file = os.path.join(scores_dir, f"{agent_data["file_name"]}.txt")
        with open(agent_file, 'w') as f:
            # Write scores for each issue
            for _, scores in agent_data["scores"].items():
                # Convert to integers
                scores_str = ', '.join(map(str, map(int, scores)))
                f.write(scores_str + '\n')
            # Write threshold (floor to integer)
            threshold = int(agent_data["threshold"])
            f.write(str(threshold))

# Update main block to include the write_game call


if __name__ == "__main__":
    # Define argument parser
    parser = argparse.ArgumentParser(
        description="Generate a game configuration based on IoU constraints.")
    parser.add_argument("--num_agents", type=int,
                        default=6, help="Number of agents")
    parser.add_argument(
        "--subissues_per_issue", nargs="+", type=int, default=[3, 3, 4, 4, 5], help="List of subissues per issue"
    )
    parser.add_argument("--total_utility", type=int,
                        default=100, help="Total utility per agent")
    parser.add_argument("--target_iou", type=float,
                        default=0.5, help="Target IoU for agents' scores")
    parser.add_argument(
        "--inherited_directory",
        type=str,
        default="our_games_descriptions/base",
        help="Path to the inherited semantic directory",
    )
    parser.add_argument(
        "--new_directory",
        type=str,
        help="Path to the new directory. Will be dynamically generated if not provided",
    )

    # Parse arguments
    args = parser.parse_args()

    # Dynamically set new_directory if not provided
    game_name = args.inherited_directory.split("/")[-1]
    if args.new_directory is None:
        args.new_directory = f"our_games_descriptions/{
            game_name}_iou_{args.target_iou}"

    # Generate utility functions for agents
    agents, iou_history = generate_utility_functions(
        num_agents=args.num_agents,
        subissues_per_issue=args.subissues_per_issue,
        total_utility=args.total_utility,
        target_iou=args.target_iou,
        seed_dir=args.inherited_directory,
    )

    # Check the sum of utilities for each agent
    check_sum_of_utilities(agents, args.total_utility)

    # Check the IoU of the agents' scores
    check_iou(agents, args.target_iou, tolerance=0.01)

    # Adjust agent scores to meet the total utility constraint
    adjusted_agents = adjust_agent_scores(agents)

    for agent_name, agent_data in adjusted_agents.items():
        print(f"{agent_name}:")
        for issue, scores in agent_data["scores"].items():
            print(f"  {issue}: {scores}")
        print(f"  Threshold: {agent_data['threshold']}")
        print()

    write_game(adjusted_agents, args.inherited_directory, args.new_directory)
    plt.plot(iou_history)
    plt.xlabel('Iteration')
    plt.ylabel('IoU')
    plt.title('IoU During Optimization')
    plt.savefig(os.path.join(args.new_directory, 'iou_history.png'))
    plt.close()

    print("Configuration generated successfully.")
