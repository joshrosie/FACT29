# Reproducing Figure 2
# (a): Effect of Varying thresholds

This document provides instructions on how to reproduce **Figure 2(a)**, which examines how modifying the negotiation acceptance threshold impacts acceptance rates in the **base** game.

## Steps to Reproduce the Experiment

### Step 1: Select a Threshold Variation
In our experiments, we evaluated the effect of changing the acceptance threshold by applying different variations. The valid threshold variations that can be used for reproduction are:
- `minus_3`
- `minus_5`
- `minus_10`
- `minus_20`
- `plus_3`
- `plus_5`
- `plus_10`

Each variation adjusts the acceptance criteria used during negotiation, influencing the final agreement rates.

### Step 2: Run the Experiment
To reproduce the results for a specific threshold variation, execute the following command:

```bash
python main.py --exp_name gpt-4o-mini --game_dir ./games_descriptions/base_varying_thresholds/<THRESHOLD_VARIATION>/ --output_dir ./output_reproduce/ --model gpt-4o-mini
```

Replace `<THRESHOLD_VARIATION>` with one of the valid variations listed above. For example, to run the experiment with a threshold variation of **minus_10**, use:

```bash
python main.py --exp_name gpt-4o-mini --game_dir ./games_descriptions/base_varying_thresholds/minus_10/ --output_dir ./output_reproduce/ --model gpt-4o-mini
```

### Step 3: Output Structure

#### Original Results:
```bash
our_games_descriptions/base_varying_thresholds/<THRESHOLD_VARIATION>/output/<MODEL>
```
For example:
```bash
our_games_descriptions/base_varying_thresholds/minus_10/output/gpt-4o-mini
```

#### Reproduced Results:
```bash
our_games_descriptions/base_varying_thresholds/<THRESHOLD_VARIATION>/output_reproduce/<MODEL>
```
For example:
```bash
our_games_descriptions/base_varying_thresholds/minus_10/output_reproduce/gpt-4o-mini
```

This structure ensures that all reproduced results remain distinct from the originally logged outputs.

### Step 4: Evaluating the Results
After completing the experiment, process the output data using the evaluation script (`.ipynb`) to extract acceptance rates. Refer to the [**Evaluation**](../NEW-README.md#evaluation) section in the original README for detailed instructions.


# (b): Effect of Number of Players on Acceptance

This document provides detailed instructions on how to reproduce **Figure 2(b)**, which investigates how varying the number of players in the **base** game affects acceptance rates.

## Steps to Reproduce the Experiment

### Step 1: Modify the Configuration File
To adjust the number of players, you need to edit the **config.txt** file of the game directory. This file defines the participating agents. Follow these steps:
1. **Navigate to the config file:**
   ```bash
   cd our_games_descriptions/base/
   nano config.txt
   ```
2. **Reduce the number of players** to the desired value by removing lines corresponding to non-essential players.
   - **Important:** Ensure that **p1** and **p2** remain in the list.
3. **Save and exit** the file after making changes.

#### Configuration files used
The configuration files that we used for our experiments are:
- [3 players](../our_games_descriptions/base/output/changing_num_players/gpt4o-mini/3_players/config.txt)
- [4 players](../our_games_descriptions/base/output/changing_num_players/gpt4o-mini/5_players/config.txt)
- [5 players](../our_games_descriptions/base/output/changing_num_players/gpt4o-mini/4_players/config.txt)

### Step 2: Run the Experiment with `main.py`
Once the configuration file has been modified, execute the following command to run the experiment:

To reproduce our results run:
```bash
python main.py --exp_name changing_num_players/gpt4o-mini/<NUM_PLAYERS>_players --agents_num <NUM_PLAYERS> --game_dir ./our_games_descriptions/base/
```

To use an open-source model, run:
```bash
python main.py --exp_name varying_players/<NUM_PLAYERS>_players/<MODEL_ALIAS> --agents_num <NUM_PLAYERS> --game_dir ./our_games_descriptions/base/
```

Replace `<NUM_PLAYERS>` with the number of players specified in `config.txt`.
Replace `<MODEL>` with desired model. See [Detailed instructions](./Models.md) for more details.

For example, to run an experiment with **4 players**, use:

```bash
python main.py --exp_name changing_num_players/gpt4o-mini/4_players --agents_num 4 --game_dir ./our_games_descriptions/base/
```

### Step 3: Output Structure
The output files will be saved under the following structure:

#### Original Results:
```bash
our_games_descriptions/base/output/changing_num_players/gpt4o-mini/<NUM_PLAYERS>_players/
```
#### Reproduced Results:
```bash
our_games_descriptions/base/output_reproduce/changing_num_players/gpt4o-mini/<NUM_PLAYERS>_players/
```

This ensures that all reproduced results remain distinct from the originally logged outputs.

### Step 4: Evaluating the Results
After completing the experiment, process the output data using the evaluation script (`.ipynb`) to extract acceptance rates. Refer to the [**Evaluation**](../NEW-README.md#evaluation) section in the original README for detailed instructions.


