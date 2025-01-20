#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Qwen2.5-7B-Instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-7B-Instruct \
--incentive cooperative \
--restrict_leakage \
--emission_project Qwen2.5-7B-Instruct"

$COMMAND

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Ministral-8B-Instruct-2410 \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_mistralai/Ministral-8B-Instruct-2410 \
--incentive cooperative \
--restrict_leakage \
--emission_project Ministral-8B-Instruct-2410"

$COMMAND

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Mixtral-8x7B-Instruct-v0.1 \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_mistralai/Mixtral-8x7B-Instruct-v0.1 \
--incentive cooperative \
--restrict_leakage \
--quantization int4 \
--emission_project Mixtral-8x7B-Instruct-v0.1"

$COMMAND

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Llama-3.3-70B-Instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_meta-llama/Llama-3.3-70B-Instruct \
--incentive cooperative \
--restrict_leakage \
--quantization int4 \
--emission_project Llama-3.3-70B-Instruct"

$COMMAND

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Qwen2.5-72B-Instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-72B-Instruct \
--incentive cooperative \
--restrict_leakage \
--quantization int4 \
--emission_project Qwen2.5-72B-Instruct"

$COMMAND