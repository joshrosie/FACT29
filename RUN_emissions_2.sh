#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Phi-3.5-mini-instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_microsoft/Phi-3.5-mini-instruct \
--incentive cooperative \
--restrict_leakage \
--emission_project Phi-3.5-mini-instruct"

$COMMAND

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Llama-2-13b-chat-h \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_meta-llama/Llama-2-13b-chat-hf \
--incentive cooperative \
--restrict_leakage \
--quantization int8 \
--emission_project Llama-2-13b-chat-h"

$COMMAND

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Meta-Llama-3-8B-Instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_meta-llama/Meta-Llama-3-8B-Instruct \
--incentive cooperative \
--restrict_leakage \
--quantization int4 \
--emission_project Meta-Llama-3-8B-Instruct"

$COMMAND

# Define the command to run
COMMAND="python main.py --exp_name emission_test/phi-4 \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_microsoft/phi-4 \
--incentive cooperative \
--restrict_leakage \
--quantization int8 \
--emission_project phi-4"

$COMMAND

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Mistral-Small-Instruct-2409 \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_mistralai/Mistral-Small-Instruct-2409 \
--incentive cooperative \
--restrict_leakage \
--quantization int8 \
--emission_project Mistral-Small-Instruct-2409"

$COMMAND