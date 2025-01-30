
  

## Setup 

- Create a new enviroment and install the following:
```
conda install pytorch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 pytorch-cuda=12.1 -c pytorch -c nvidia
conda install conda-forge::transformers
pip install google-cloud-aiplatform
pip install openai
pip install accelerate
pip install -U bitsandbytes
pip install seaborn
pip install matplotlib
pip install ipython
pip install codecarbon
```

**TODO: ADD NEW PACKAGES**



## Running Experiments

The codebase is structured into multiple Python scripts, with `main.py` as the entry point for running experiments. Key components include `agent.py` for defining agent behavior, `rounds.py` for managing negotiations, `utils.py` for auxiliary functions, `initial_prompts.py` for predefined prompts, and `save_utils.py` for data handling. These modules work together to initialize agents, configure the negotiation environment, execute rounds, and compile results.

### Configuration and Execution

The new version allows full customization of experiments via command-line arguments, removing the need to modify `config.txt`. Users can now specify key parameters directly:
- `--temp`: Temperature setting for agent responses.
- `--agents_num`: Number of agents participating in the negotiation.
- `--issues_num`: Number of issues in the negotiation.
- `--rounds_num`: Number of negotiation rounds.
- `--window_size`: Number of previous rounds considered in decision-making.
- `--game_dir`: Path to the game description directory.
- `--output_dir`: Path to the directory for storing experiment results.
- `--exp_name`: Name of the experiment.
- `--restart`: Flag to restart an experiment from an existing history file.
- `--output_file`: Name of the history file for continuing previous experiments.
- `--model`: Specifies the models used for agents (no need to edit `config.txt`). For more details see: [Detailed instructions](./reproduction_instructions/Models.md)
- `--incentive`: Defines the incentives of agents (now configurable via command-line).
- `--role`: Specifies agent roles (eliminating manual edits in `config.txt`).
- `--quantization`: Enables quantization for Hugging Face models.
- `--restrict_leakage`: Restricts sensitive information leakage during negotiations.
- `--dry_run`: Enables a mode where API calls to language models are disabled for debugging.
- `--emission_project`: Specifies a project name for tracking carbon emissions.
- `--ablations`: Allows ablation studies on specific negotiation strategies.

With these options, all modifications previously requiring manual edits in `config.txt` can now be done via command-line parameters, streamlining the experiment setup process.

### Running the Experiment

Below you can find some example commands:

Base game with gpt-4o-mini / All agents cooperative
```bash
python main.py --model "gpt-4o-mini" --exp_name "test/gpt-4o-mini/" --game_dir ./our_games_descriptions/base --incentive "cooperative"
```
Base game with Qwen2.5-72B / All agents cooperative
```bash
python main.py --model "hf_Qwen/Qwen2.5-72B-Instruct" --exp_name "test/Qwen2.5-72B/" --game_dir "./our_games_descriptions/base"  --quantization "int4" --incentive "cooperative" --hf_home "hf_models/"
```

Base game with Qwen2.5-72B / Adversarial targeted behavior
```bash
python main.py --exp_name "changing_behaviour/Qwen2.5-72B-Instruct/adversarial_untargeted" --game_dir "our_games_descriptions/base/" --hf_home "hf_models/" --output_dir "./output_reproduce/" --model "hf_Qwen/Qwen2.5-72B-Instruct" --quantization "int4" --incentive "cooperative" "cooperative" "cooperative" "cooperative" "cooperative" "targeted_adv" --role "player" "player" "target" "p1" "p2" "player"
```

Additional options include:
- **TODO: SAY MORE ABOUT OPENAI and HUGGINGFACE keys**
- If using OpenAI APIs, specify `--api_key`.
- In order to distinguish emission tracking between experiments, you can set a project name for each experiment by: `--emission_project <PROJECT_NAME>`.
- To test without making API calls, use `--dry_run`.

The training script will create an output directory under `./our_games_descriptions/<GAME>/output_reproduce/<exp_name>`, where it will store experiment results, including a copy of `config.txt` for reference.

### Enhancements and Sustainability Features

To improve performance and configurability, several enhancements have been introduced:
- The `--model`, `--incentive`, and `--role` parameters eliminate the need to modify `config.txt` manually.
- The `--quantization` option optimizes Hugging Face models for reduced memory usage and faster execution.
- The `--restrict_leakage` flag helps mitigate the risk of sensitive information leakage during negotiations.
- The `--dry_run` mode enables debugging without incurring API costs.
- The integration of the `codecarbon` EmissionsTracker records the carbon footprint of experiments, supporting sustainable research practices.

These improvements make the framework more efficient, scalable, and environmentally conscious, facilitating robust experimentation.

## Reproducing Results

To ensure the reproducibility of the experimental results presented in this study, this section provides references to detailed instructions for replicating each experiment. Each subsection corresponds to a specific table or figure and includes a link to a dedicated document containing the required command-line parameters, configuration modifications, and execution steps.

### **Tables 1 and 17: Model Performance Before and After Fixing Leakage Issues**
These tables present a comparison of model performance and leakage metrics before and after resolving leakage issues. The linked document explains how to reproduce experiments for both the original and corrected model versions.
[Detailed instructions](./reproduction_instructions/Table1_and_17.md)

### **Table 2: Model Performance Comparison**
This table presents a comparative analysis of multiple models on the base game. The linked document provides instructions on executing experiments for each model.
[Detailed instructions](./reproduction_instructions/Table2.md)

### **Table 3: Ablation Study Results**
This table reports the outcomes of the ablation study, assessing the impact of various components on model performance. The linked document outlines the necessary execution steps for reproducing the ablation experiments on GPT4o-mini and Qwen2.5-72B-Instruct.
[Detailed instructions](./reproduction_instructions/Table3.md)

### **Table 4: Performance Comparison Across Different Games**
This table evaluates model performance across multiple game settings. The linked document details the execution procedure for experiments under different game configurations.
[Detailed instructions](./reproduction_instructions/Table4.md)

### **Table 5: Baseline Comparisons**
This table benchmarks several baseline methods against GPT4o-mini. The linked document contains step-by-step instructions on executing experiments for each baseline approach.
[Detailed instructions](./reproduction_instructions/Table5.md)


### **Table 7: Behavioral Variant Performance**
This table analyzes the effects of different behavioral strategies on negotiation performance. The linked document provides guidelines on reproducing all the experiments for various every behavioral configuration.
[Detailed instructions](./reproduction_instructions/Table7.md)


### **Figure 2: Effect of Varying Thresholds and Varying Number of Players**
These figures illustrates the impact of varying thresholds as well as varying the number of players in the base game on acceptance rates. The linked document outlines the execution procedure for reproducing all the experiments.
[Detailed instructions](./reproduction_instructions/Figure2.md)

## Evaluation

### **Evaluating a Specific Experiment**
To evaluate a single experiment and compute relevant metrics, run the [`evaluation.ipynb`](./evaluation/deals_evolution.ipynb) notebook, specifying the output directory of the experiment. This notebook calculates:
- **Pre-hoc metrics**
- **Post-hoc performance metrics**: 5-way, 6-way, Any, Wrong, Leaked
- **Post-hoc econometrics**

Ensure that the output directory contains the recorded negotiation histories. Running the notebook will generate detailed performance summaries and insights for the given experiment.

### **Evaluating and Recreating the Paper’s Results**
To evaluate all experiments performed in this study and regenerate the tables and figures presented in the paper, use the dedicated evaluation notebooks corresponding to each table or figure. These notebooks process the results and should reproduce the exact outputs reported in the paper when using the original experiment data.

#### **Recreating the Original Paper Results**
If you wish to validate our reported results without re-running the experiments, simply execute the corresponding evaluation notebooks as they are. Each notebook is designed to process our logged experimental outputs and will generate the exact figures and tables presented in the paper.

#### **Fully Reproducing and Evaluating New Experiments**
If you have followed the [**Reproducing Results**](#reproducing-results) section to generate new experimental data, you can use the same evaluation notebooks to assess the reproduced experiments. In this case:
1. Open the relevant evaluation notebook for the table or figure.
2. Modify the experiment folder path by replacing `output` with `output_reproduce` at the top of the notebook.
3. If you have run a subset of models or included additional models, update the model list in the notebook accordingly.
4. Execute the notebook to compute the results.

By following these steps, you can either validate the original reported results or fully reproduce the paper’s findings using newly generated experimental data.







