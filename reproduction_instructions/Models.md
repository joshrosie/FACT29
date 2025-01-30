# Using Different Models

This document provides instructions on how to specify different models for experiments using the `--model` command-line argument in `main.py`. The models listed below are the ones we used for our experiments and can be selected by passing their corresponding argument values.

## Specifying a Model in an Experiment
To use a specific model in an experiment, include the `--model` argument in the execution command. For example:

```bash
python main.py --exp_name experiment_name --model <MODEL_NAME> --other_parameters
```

Replace `<MODEL_NAME>` with the desired model from the list below.

## Models Used in Our Experiments
The following models were used in our experiments:

| Model Name | Command-Line Argument |
|------------|----------------------|
| **DeepSeek-R1-Distill-Llama-70B** | `hf_deepseek-ai/DeepSeek-R1-Distill-Llama-70B` |
| **DeepSeek-R1-Distill-Qwen-32B** | `hf_deepseek-ai/DeepSeek-R1-Distill-Qwen-32B` |
| **Llama-2-13b Chat** | `hf_meta-llama/Llama-2-13b-chat-hf` |
| **Meta-Llama-3-8B Instruct** | `hf_meta-llama/Meta-Llama-3-8B-Instruct` |
| **Ministral-8B Instruct (2410)** | `hf_mistralai/Ministral-8B-Instruct-2410` |
| **Mistral-Small Instruct (2409)** | `hf_mistralai/Mistral-Small-Instruct-2409` |
| **Mixtral-8x7B Instruct (v0.1)** | `hf_mistralai/Mixtral-8x7B-Instruct-v0.1` |
| **Phi-3.5 Mini Instruct** | `hf_microsoft/Phi-3.5-mini-instruct` |
| **Qwen2.5-72B Instruct** | `hf_Qwen/Qwen2.5-72B-Instruct` |
| **Qwen2.5-7B Instruct** | `hf_Qwen/Qwen2.5-7B-Instruct` |
| **Llama-3.3-70B Instruct** | `hf_meta-llama/Llama-3.3-70B-Instruct` |
| **Phi-4** | `hf_microsoft/phi-4` |
| **GPT-4o-mini** | `gpt-4o-mini` |

## Using Additional Models
If a new model needs to be used, set the `--model` parameter to `hf_<MODEL_NAME>`, where `<MODEL_NAME>` is the Hugging Face model path. For example:

```bash
python main.py --exp_name new_experiment --model hf_neworg/New-Model-Name --other_parameters
```


## Additional Considerations
- Ensure that the model names are written exactly as shown above.
- If running on a system with limited memory, consider using the `--quantization` argument for Hugging Face models to enable lower precision computation.
- When using GPT models, ensure that the corresponding API keys or endpoints are correctly configured.
- Some Hugging Face models require users to agree to specific terms and provide a Hugging Face token for access. Ensure that the necessary permissions are granted and set up the Hugging Face authentication token before using these models.

