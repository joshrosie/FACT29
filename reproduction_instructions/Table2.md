# Reproducing Table 2

This document provides instructions on how to reproduce the results presented in **Table 2**. Each row in the table corresponds to an experiment with a specific model configuration.

## Experiment Mapping

| Model in Paper                                   | Experiment Name in Code                     |
|-------------------------------------------------|--------------------------------------------|
| gpt4o-mini                                      | `base_normal_gpt4o-mini`                   |
| **Llama-2-13b (int8)**                          | `base_normal_Llama-2-13b-chat-hf`          |
| Llama-3-8B                                      | `base_normal_Meta-Llama-3-8B-Instruct`     |
| **Llama-3.3-70B (int4)**                        | `base_normal_Llama-3.3-70B-Instruct`       |
| Qwen2.5-7B                                     | `base_normal_Qwen2.5-7B-Instruct`          |
| Qwen2.5-72B (int4)                             | `base_normal_Qwen2.5-72B-Instruct`         |
| Phi-3.5-mini                                   | `base_normal_Phi-3.5-mini-instruct`        |
| Phi-4 (int8)                                   | `base_normal_phi-4`                        |
| Minstrel-8B                                    | `base_normal_Minstrel-8B-Instruct-2410`    |
| Mistral-Small (int8)                           | `base_normal_Mistral-Small-Instruct-2409`  |
| **Mixtral-8x7B (int4)**                        | `base_normal_Mixtral-8x7B-Instruct-v0.1`   |
| DeepSeek-R1-Distill-Qwen-32B (int8)            | `base_normal_DeepSeek-R1-Distill-Qwen-32B` |
| DeepSeek-R1-Distill-Llama-70B (int4)           | `base_normal_DeepSeek-R1-Distill-Llama-70B` |

## Running an Experiment

To reproduce the results for a specific model, run the following command:

```bash
python reproduction.py --exp_name <experiment_name>
```

For example, to reproduce the results for **Llama-2-13b (int8)**, use:

```bash
python reproduction.py --exp_name base_normal_Llama-2-13b-chat-hf
```

Each experiment will be executed **20 times** by default, as specified in `reproduction.py`.

## Customizing Execution

- To change the number of iterations, modify `N` in `reproduction.py`.
- To use a different Python executable, add the `--python_name` argument:

  ```bash
  python reproduction.py --exp_name base_normal_Mixtral-8x7B-Instruct-v0.1 --python_name python3.12
  ```

## Experiment Results

After running the script, the new results will be saved separately from the original logs to facilitate easy comparison. The original logs follow this structure:
```bash
our_games_descriptions/<GAME>/output/<EXPERIMENT>/MODEL
```
The newly generated results will be stored under:
```bash
our_games_descriptions/<GAME>/output_reproduce/<EXPERIMENT>/MODEL
```
This ensures that all reproduced results remain distinct from the originally logged outputs.

To obtain the actual performance scores for each experiment, you need to run the evaluation script (`.ipynb`) on the experiment’s output folder. For detailed instructions on running the evaluation, refer to the **Evaluation** section in the original README.


