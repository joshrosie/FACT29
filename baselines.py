import argparse
import os
from baselines.two_phase import two_phase_approach
from baselines.random_midline_prevproximity import random_midline_prevproximity
from baselines.multi_sample_consensus import multi_sample_consensus_approach
from baselines.frequency_restricted import freq_restrict_multi_consensus_approach

if __name__ == "__main__":
    """
    This script runs baseline methods for a specified game configuration.
    Usage:
        python baselines.py --game <game_directory> --method <method_name>
    Arguments:
        --game (str): The directory of the game configuration. This argument is required.
        --method (str): The proposal generation method to use. This argument is required.
            Choices:
                - 'random': Use a random proposal generation method.
                - 'midline': Use the midline proposal generation method.
                - 'prev_prox': Use the previous proximity proposal generation method.
                - 'multi_sample_consensus': Use the multi-sample consensus proposal generation method.
                - 'freq_restricted': Use the frequency restricted proposal generation method.
                - 'two_phase': Use the two-phase proposal generation method.
    """
    parser = argparse.ArgumentParser(description='Run baseline methods.')
    parser.add_argument('--game', type=str, required=True, help='The directory of the game configuration')
    parser.add_argument('--method', type=str, required=True, choices=['random', 'midline', 'prev_prox', 'multi_sample_consensus', 'freq_restricted', 'two_phase'], help='The proposal generation method to use')
    args = parser.parse_args()

    game_dir = args.game
    method = args.method

    # Run the baseline method
    if method in ['random', 'midline', 'prev_prox']:
        random_midline_prevproximity(game_dir, method)
    elif method == 'multi_sample_consensus':
        multi_sample_consensus_approach(game_dir)
    elif method == 'freq_restricted':
        freq_restrict_multi_consensus_approach(game_dir)
    elif method == 'two_phase':
        two_phase_approach(game_dir)
    else:
        raise ValueError(f"Invalid method: {method}")