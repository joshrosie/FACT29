#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name DeepSeek-R1-Distill-Llama-70B \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_deepseek-ai/DeepSeek-R1-Distill-Llama-70B \
--quantization int4 \
--incentive cooperative \
--restrict_leakage \
--emission_project DeepSeek-R1-Distill-Llama-70B"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"