#!/bin/bash

# Define the command to run
COMMAND="python main.py --exp_name emission_test/Qwen2.5-7B-Instruct \
--game_dir our_games_descriptions/base/ \
--hf_home hf_models/ \
--model hf_Qwen/Qwen2.5-7B-Instruct \
--incentive cooperative \
--restrict_leakage \
--quantization int8 \
--emission_project Qwen2.5-7B-Instruct"

$COMMAND