#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name Meta-Llama-3-8B-Instruct \
--game_dir our_games_descriptions/base_rewritten/ \
--hf_home hf_models/ \
--model hf_meta-llama/Meta-Llama-3-8B-Instruct \
--incentive cooperative"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

COMMAND="python main.py --exp_name Meta-Llama-3-8B-Instruct \
--game_dir our_games_descriptions/game1/ \
--hf_home hf_models/ \
--model hf_meta-llama/Meta-Llama-3-8B-Instruct \
--incentive cooperative"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

COMMAND="python main.py --exp_name Meta-Llama-3-8B-Instruct \
--game_dir our_games_descriptions/game2/ \
--hf_home hf_models/ \
--model hf_meta-llama/Meta-Llama-3-8B-Instruct \
--incentive cooperative"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

COMMAND="python main.py --exp_name Meta-Llama-3-8B-Instruct \
--game_dir our_games_descriptions/game3/ \
--hf_home hf_models/ \
--model hf_meta-llama/Meta-Llama-3-8B-Instruct \
--incentive cooperative"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"