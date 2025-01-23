#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name variants/Qwen2.5-72B-Instruct/one_greedy \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-72B-Instruct \
--quantization int4 \
--incentive cooperative cooperative cooperative cooperative cooperative greedy \
--emission_project game_variants_Qwen72 \
--restrict_leakage"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

# Define the command to run
COMMAND="python main.py --exp_name variants/Qwen2.5-72B-Instruct/one_greedy_p1 \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-72B-Instruct \
--quantization int4 \
--incentive cooperative cooperative cooperative greedy cooperative cooperative \
--emission_project game_variants_Qwen72 \
--restrict_leakage"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

# Define the command to run
COMMAND="python main.py --exp_name variants/Qwen2.5-72B-Instruct/two_greedy \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-72B-Instruct \
--quantization int4 \
--incentive greedy cooperative greedy cooperative cooperative cooperative \
--emission_project game_variants_Qwen72 \
--restrict_leakage"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

# Define the command to run
COMMAND="python main.py --exp_name variants/Qwen2.5-72B-Instruct/all_greedy \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-72B-Instruct \
--quantization int4 \
--incentive greedy greedy greedy greedy greedy greedy \
--emission_project game_variants_Qwen72 \
--restrict_leakage"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

# Define the command to run
COMMAND="python main.py --exp_name variants/Qwen2.5-72B-Instruct/adversarial_untargeted \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-72B-Instruct \
--quantization int4 \
--incentive cooperative cooperative cooperative cooperative cooperative untargeted_adv \
--emission_project game_variants_Qwen72 \
--restrict_leakage"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"

# Define the command to run
COMMAND="python main.py --exp_name variants/Qwen2.5-72B-Instruct/adversarial_targeted \
--game_dir our_games_descriptions/base_adv/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-72B-Instruct \
--quantization int4 \
--incentive cooperative cooperative cooperative cooperative cooperative targeted_adv \
--emission_project game_variants_Qwen72 \
--restrict_leakage"

# Loop to run the command 20 times
for i in {1..20}; do
    echo "Running iteration $i..."
    $COMMAND
    echo "Iteration $i completed."
done

echo "All 20 iterations finished!"