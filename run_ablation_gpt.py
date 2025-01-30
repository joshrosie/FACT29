import subprocess
import time

PYTHON = 'python'

MODEL = "gpt-4o-mini"


log_file = "ablation_gpt.log"
f = open(log_file, "w")

# Number of iterations
N = 20

# Base game folder prefix
BASE_GAME = "ablations_base_"
ablation_list = [
    [True, True, True, True],
    [True, True, True, False],
    [True, True, False, True],
    [True, True, False, False],
    [True, False, True, True],
    [True, False, True, False],
    [True, False, False, True],
    [True, False, False, False],
    [False, True, True, True],
    [False, True, True, False],
    [False, True, False, True],
    [False, True, False, False],
    [False, False, True, True],
    [False, False, True, False],
    [False, False, False, True],
    [False, False, False, False],
]

for _ablation in ablation_list:
    # Ablation settings (set to True or False)
    ABLATION_PREVIOUS, ABLATION_OTHERS, ABLATION_CANDIDATES, ABLATION_PLAN = _ablation

    # Construct the game folder name based on the ablations
    game_folder_suffix = f"{int(ABLATION_PREVIOUS)}{int(ABLATION_OTHERS)}{int(ABLATION_CANDIDATES)}{int(ABLATION_PLAN)}"
    GAME = f"{BASE_GAME}{game_folder_suffix}"

    # Construct the ablations parameter based on selected ablations
    ablations = []
    if ABLATION_PREVIOUS:
        ablations.append("previous")
    if ABLATION_OTHERS:
        ablations.append("others")
    if ABLATION_CANDIDATES:
        ablations.append("candidates")
    if ABLATION_PLAN:
        ablations.append("plan")

    # Convert ablations list into a string argument for the command
    ablations_param = ",".join(ablations)

    # Command to run
    command = [
        PYTHON, "main.py",
        "--exp_name", f"ablation/{MODEL}/{GAME}",
        "--game_dir", "our_games_descriptions/base/",
        "--output_dir", "./output_reproduce/",
        "--model", MODEL,
        "--incentive", "cooperative",
    ]

    # Add ablations parameter if any ablations are enabled
    if ablations_param:
        command += ["--ablations", ablations_param]

    # Print experiment settings
    print(f"Running {N} iterations with ablations: {ablations_param}")
    print(f"Saving in folder: {GAME}")
    f.write(f"Running {N} iterations with ablations: {ablations_param}\n")
    f.write(f"Saving in folder: {GAME}\n")

    for i in range(1, N + 1):
        print(f"Running iteration {i}/{N} with ablations: {ablations_param}...")
        f.write(f"Running iteration {i}/{N} with ablations: {ablations_param}...\n")

        # Start time for tracking each iteration
        start_time = time.time()

        # Run the command
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            # Print the output or handle it
            print(f"Iteration {i} completed with return code {result.returncode}")
            f.write(f"Iteration {i} completed with return code {result.returncode}\n")
            print(result.stdout)
            if result.stderr:
                print(f"Error in iteration {i}:\n{result.stderr}")
                f.write(f"Error in iteration {i}:\n{result.stderr}\n")
        except Exception as e:
            print(f"Error during iteration {i}: {e}")
            f.write(f"Error during iteration {i}: {e}\n")

        # Print the time taken for this iteration
        elapsed_time = time.time() - start_time
        print(f"Iteration {i} completed in {elapsed_time:.2f} seconds\n")
        f.write(f"Iteration {i} completed in {elapsed_time:.2f} seconds\n")

    print("All iterations completed!")
    f.write("All iterations completed!\n")
