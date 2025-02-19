# Reproducing Table 3

This document provides instructions on how to reproduce the results presented in **Table 3**. Each row in the table corresponds to a different game setting, and each column represents a specific model configuration.

## Experiment Mapping

The following table maps the **game settings** to their corresponding **experiment names** for each model in Table 4.

| Game Setting         | GPT4o-mini Experiment        | Mistral-Small Experiment                           | Qwen2.5-72B Experiment                         |
|----------------------|-----------------------------|--------------------------------------------------|-----------------------------------------------|
| **Base Rewritten**  | `base-rewritten_normal_gpt4o-mini`  | `base-rewritten_normal_Mistral-Small-Instruct-2409`  | `base-rewritten_normal_Qwen2.5-72B-Instruct`  |
| **Game 1**         | `game1_normal_gpt4o-mini`    | `game1_normal_Mistral-Small-Instruct-2409`      | `game1_normal_Qwen2.5-72B-Instruct`          |
| **Game 2**         | `game2_normal_gpt4o-mini`    | `game2_normal_Mistral-Small-Instruct-2409`      | `game2_normal_Qwen2.5-72B-Instruct`          |
| **Game 3**         | `game3_normal_gpt4o-mini`    | `game3_normal_Mistral-Small-Instruct-2409`      | `game3_normal_Qwen2.5-72B-Instruct`          |

## Running an Experiment

To reproduce the results for a specific model and game setting, run the following command:

```bash
python reproduction.py --exp_name <experiment_name>
```

For example, to reproduce the results for **Mistral-Small in Game 2**, use:

```bash
python reproduction.py --exp_name game2_normal_Mistral-Small-Instruct-2409
```

Each experiment will be executed **20 times** by default, as specified in `reproduction.py`.

## Customizing Execution

- To change the number of iterations, modify `N` in `reproduction.py`.
- To use a different Python executable, add the `--python_name` argument:

  ```bash
  python reproduction.py --exp_name game3_normal_Qwen2.5-72B-Instruct --python_name python3.12
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

To obtain the actual performance scores for each experiment, you need to run the evaluation script (`.ipynb`) on the experiment’s output folder. For detailed instructions on running the evaluation, refer to the [**Evaluation**](../README.md#evaluation) section in the original README.

