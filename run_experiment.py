import subprocess
import time

# Number of iterations
N = 2

# Base game folder prefix
BASE_GAME = "ablations_base_"

# Ablation settings (set to True or False)
ABLATION_PREVIOUS = True
ABLATION_OTHERS = True
ABLATION_CANDIDATES = False
ABLATION_PLAN = False

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
    "python3",
    "main.py",
    "--game_dir",
    f"./games_descriptions/{GAME}",
]

# Add ablations parameter if any ablations are enabled
if ablations_param:
    command += ["--ablations", ablations_param]

# Print experiment settings
print(f"Running {N} iterations with ablations: {ablations_param}")
print(f"Saving in folder: {GAME}")

for i in range(1, N + 1):
    print(f"Running iteration {i}/{N} with ablations: {ablations_param}...")

    # Start time for tracking each iteration
    start_time = time.time()

    # Run the command
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        # Print the output or handle it
        print(f"Iteration {i} completed with return code {result.returncode}")
        print(result.stdout)
        if result.stderr:
            print(f"Error in iteration {i}:\n{result.stderr}")
    except Exception as e:
        print(f"Error during iteration {i}: {e}")

    # Print the time taken for this iteration
    elapsed_time = time.time() - start_time
    print(f"Iteration {i} completed in {elapsed_time:.2f} seconds\n")

print("All iterations completed!")
