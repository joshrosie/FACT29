#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name Qwen2.5-72B-Instruct \
--game_dir our_games_descriptions/base_iou_0.1/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-72B-Instruct \
--incentive cooperative \
--restrict_leakage \
--quantization int4 \
--emission_project New-games_Qwen2.5-72B"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"