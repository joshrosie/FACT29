# Reproducing Table 17

This document provides instructions on how to reproduce the results presented in **Table 1** and **Table 17**. These tables compare model leakage and performance, respectively, before and after resolving the leakage issue. The left block (**Original Code**) contains experiments from **Table 2**, while the right block (**Our Code**) contains newly executed experiments.

## Experiment Mapping

The following table maps the **models** to their corresponding **experiment names** in both versions of the code.

| Model             | Original Code  (from Table 2)          | Our Code                    |
|-----------------------|-------------------------------------------------|---------------------------------------------|
| **Llama-2-13b**      | `base_normal_Llama-2-13b-chat-hf`                | `base_our-code_Llama-2-13b-chat-hf`        |
| **Llama-3-8B**       | `base_normal_Meta-Llama-3-8B-Instruct`           | `base_our-code_Meta-Llama-3-8B-Instruct`   |
| **Minstrel-8B**      | `base_normal_Minstral-8B-Instruct-2410`          | `base_our-code_Minstral-8B-Instruct-2410`  |
| **Mixtral-8x7B**     | `base_normal_Mixtral-8x7B-Instruct-v0.1`         | `base_our-code_Mixtral-8x7B-Instruct-v0.1` |
| **Phi-3.5-mini**     | `base_normal_Phi-3.5-mini-instruct`              | `base_our-code_Phi-3.5-mini-instruct`      |
| **Qwen2.5-7B**       | `base_normal_Qwen2.5-7B-Instruct`                | `base_our-code_Qwen2.5-7B-Instruct`        |

## Running an Experiment

To reproduce the results for a specific model, run the following command:

```bash
python reproduction.py --exp_name <experiment_name>
```

For example, to reproduce the results for **Minstrel-8B with Our Code**, use:

```bash
python reproduction.py --exp_name base_our-code_Minstral-8B-Instruct-2410
```

Each experiment will be executed **20 times** by default, as specified in `reproduction.py`.

## Customizing Execution

- To change the number of iterations, modify `N` in `reproduction.py`.
- To use a different Python executable, add the `--python_name` argument:

  ```bash
  python reproduction.py --exp_name base_our-code_Qwen2.5-7B-Instruct --python_name python3.12
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

To obtain the actual performance scores and leakage statistics for each experiment, you need to run the evaluation script (`.ipynb`) on the experiment’s output folder. For detailed instructions on running the evaluation, refer to the **Evaluation** section in the original README.

