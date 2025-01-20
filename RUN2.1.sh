#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name our_code_v3/Qwen2.5-7B-Instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-7B-Instruct \
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
COMMAND="python main.py --exp_name our_code_v3/Ministral-8B-Instruct-2410 \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_mistralai/Ministral-8B-Instruct-2410 \
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
COMMAND="python main.py --exp_name our_code_v3/Mixtral-8x7B-Instruct-v0.1 \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_mistralai/Mixtral-8x7B-Instruct-v0.1 \
--incentive cooperative \
--restrict_leakage \
--quantization int4"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"