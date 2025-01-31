# Reproducing Table 3: Ablation Study Results

This document provides instructions on how to reproduce the results presented in **Table 3**, which contains the results of an ablation study conducted on two models: **GPT4o-mini** and **Qwen2.5-72B-Instruct** for the "base" game.

Each row in the table represents an ablation setting, where different components were selectively disabled (ablated) to analyze their impact on model performance. To reproduce these results, a user needs to execute a dedicated Python script for each model:
- **For Open-Source Model (Qwen2.5-72B-Instruct):** `run_ablation_opensource.py`
- **For GPT-based Model (GPT4o-mini):** `run_ablation_gpt.py`

## Experiment Mapping

Each ablation setting corresponds to a specific configuration of four factors:
1. **Previous Deals**
2. **Others Preferences**
3. **Candidates**
4. **Planning**

These factors are represented in binary format (`1` = Enabled, `0` = Ablated). Each row in the table corresponds to an experiment where one or more of these factors are ablated.

## Running an Ablation Experiment

To reproduce the results for a specific model, run the corresponding script:

### Open-Source Model (Qwen2.5-72B-Instruct):
```bash
python run_ablation_opensource.py
```

### GPT Model (GPT4o-mini):
```bash
python run_ablation_gpt.py
```

Each script executes **20 iterations** for every ablation setting, as specified in the script parameters.

## Output Format

### Original Ablation Results:
The original results are stored under:
```bash
our_games_descriptions/base/output/ablation/<MODEL>/<ABLATION_CONFIGURATION>
```
For example:
```bash
our_games_descriptions/base/output/ablation/Qwen2.5-72B-Instruct/ablations_base_0000
```

### Reproduced Ablation Results:
The newly generated results will be saved separately under:
```bash
our_games_descriptions/base/output_reproduce/ablation/<MODEL>/<ABLATION_CONFIGURATION>
```
This separation ensures that reproduced results remain distinct from the original logged outputs.

## Customizing Execution

- To change the number of iterations, modify `N` in the respective script (`run_ablation_opensource.py` or `run_ablation_gpt.py`).
- To use a different Python executable, change the `PYTHON` variable inside the script and run the script with a different interpreter:

  ```bash
  python3.12 run_ablation_opensource.py
  ```

## Evaluation of Results

After running the ablation experiments, you need to process the output files to obtain the final performance scores. To do this, execute the evaluation script (`.ipynb`) on the generated output folders. Refer to the [**Evaluation**](../README.md#evaluation) section in the original README for detailed instructions on how to compute and compare the performance metrics.

