#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name our_outputs/base_coop_Phi-3-small-128k-instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"