# Reproducing Table 4: Baseline Comparison

This document provides instructions on how to reproduce the results presented in **Table 4**, which compares our proposed baseline method against the original authors' baseline across different game variants.

## Running the Experiment

To reproduce the results of our baseline method for a specific game setting, run the following command:

```bash
python baselines.py --game <game_folder>
```

This will execute our proposed baseline method by default.

### Valid Game Arguments

The `--game` argument should be set to one of the following valid game folders:

- `base`
- `game1`
- `game2`
- `game3`

## Alternative Baseline Methods

While our paper focuses solely on comparing our proposed baseline with the original authors' method, other baseline methods from previous versions of our work remain available in the implementation. If you wish to run any of these methods, you can specify them using the optional `--method` argument:

```bash
python baselines.py --game <game_folder> --method <method_name>
```

**Note:** These additional methods are **not presented in the paper** but remain available for exploratory purposes.

### Available Alternative Methods

| Method (Not in Paper)           | Argument for `baselines.py` |
| ------------------------------- | --------------------------- |
| **Random**                      | `random`                    |
| **Midline**                     | `midline`                   |
| **Previous-Proposal Proximity** | `prev_prox`                 |
| **Multi-Sample Consensus**      | `multi_sample_consensus`    |
| **Frequency-Restricted**        | `freq_restricted`           |
| **Two-Phase**                   | `two_phase`                 |

For more details on the alternative baseline methods, refer to [this document](./Extra_baselines.md).

## Output Format

### Original Baseline Results:

The results of our experiments using the repeated_rule_based method, as presented in the paper, are stored under:

```bash
our_games_descriptions/<GAME>/output/baselines/repeated_rule_based
```


### Reproduced Baseline Results:

After running `baselines.py` in order to reproduce our results, the newly generated results for our proposed baseline method will be saved under:

```bash
our_games_descriptions/<GAME>/output_reproduce/baselines/repeated_rule_based
```

### Alternative Baseline Results:

If running a method other than the proposed baseline, results will be stored under:

```bash
our_games_descriptions/<GAME>/output_reproduce/baselines/<METHOD>
```

## Evaluation of Results

After running the baseline experiments, you need to process the output files to obtain the final performance scores. To do this, execute the evaluation script (`.ipynb`) on the generated output folders. Refer to the [**Evaluation**](../README.md#evaluation) section in the original README for detailed instructions on computing and comparing the performance metrics.

