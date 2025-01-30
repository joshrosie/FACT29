# Reproducing Table 6

This document provides instructions on how to reproduce the results presented in **Table 6**. Each row in the table corresponds to a different behavioral variant, and each column represents a specific model configuration.

## Experiment Mapping

The following table maps the **behavioral variants** to their corresponding **experiment names** for each model in Table 6.

| Behavioral Variant           | GPT4o-mini                         | Qwen2.5-72B                                 |
|------------------------------|---------------------------------------------|-----------------------------------------------------|
| **All compromising**        | `base_normal_gpt4o-mini`                             | `base_normal_Qwen2.5-72B-Instruct`                                     |
| **One greedy (p_const)** | `base_behaviour_gpt4o-mini_one-greedy`      | `base_behaviour_Qwen2.5-72B-Instruct_one-greedy`   |
| **One greedy (p1)**         | `base_behaviour_gpt4o-mini_one-greedy-p1`   | `base_behaviour_Qwen2.5-72B-Instruct_one-greedy-p1` |
| **Two greedy (P_benefit)**   | `base_behaviour_gpt4o-mini_two-greedy`      | `base_behaviour_Qwen2.5-72B-Instruct_two-greedy`   |
| **All greedy**              | `base_behaviour_gpt4o-mini_all-greedy`      | `base_behaviour_Qwen2.5-72B-Instruct_all-greedy`   |
| **Adversarial (untargeted)**| `base_behaviour_gpt4o-mini_adversarial-untargeted` | `base_behaviour_Qwen2.5-72B-Instruct_adversarial-untargeted` |
| **Adversarial (targeted)**  | `base_behaviour_gpt4o-mini_adversarial-targeted`   | `base_behaviour_Qwen2.5-72B-Instruct_adversarial-targeted`   |

## Running an Experiment

To reproduce the results for a specific model and behavioral variant, run the following command:

```bash
python reproduction.py --exp_name <experiment_name>
```

For example, to reproduce the results for **Qwen2.5-72B with Two Greedy**, use:

```bash
python reproduction.py --exp_name base_behaviour_Qwen2.5-72B-Instruct_two-greedy
```

Each experiment will be executed **20 times** by default, as specified in `reproduction.py`.

## Customizing Execution

- To change the number of iterations, modify `N` in `reproduction.py`.
- To use a different Python executable, add the `--python_name` argument:

  ```bash
  python reproduction.py --exp_name base_behaviour_gpt4o-mini_adversarial-targeted --python_name python3.12
  ```

## Experiment Results

After running the script, the new results will be saved separately from the original logs to facilitate easy comparison. The original logs follow this structure:
```bash
our_games_descriptions/<GAME>/output/changing_behaviour/<MODEL>/<EXPERIMENT>
```
The newly generated results will be stored under:
```bash
our_games_descriptions/<GAME>/output_reproduce/changing_behaviour/<MODEL>/<EXPERIMENT>
```
This ensures that all reproduced results remain distinct from the originally logged outputs.

To obtain the actual performance scores for each experiment, you need to run the evaluation script (`.ipynb`) on the experiment’s output folder. For detailed instructions on running the evaluation, refer to the [**Evaluation**](../NEW-README.md#evaluation) section in the original README.

