#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name our_code_v2/Phi-3.5-mini-instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_microsoft/Phi-3.5-mini-instruct \
--incentive cooperative \
--restrict_leakage"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

# Define the command to run
COMMAND="python main.py --exp_name our_code_v2/Llama-2-13b-chat-hf \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_meta-llama/Llama-2-13b-chat-hf \
--incentive cooperative \
--restrict_leakage \
--quantization int8"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

# Define the command to run
COMMAND="python main.py --exp_name our_code_v2/Meta-Llama-3-8B-Instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_meta-llama/Meta-Llama-3-8B-Instruct \
--incentive cooperative \
--restrict_leakage"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"