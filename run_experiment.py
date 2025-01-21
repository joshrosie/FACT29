import subprocess
import time

# Number of iterations
N = 20

# Construct the game folder name based on the ablations
GAME = f"base_higher_threshold_3"

# Command to run
command = [
    "python3",
    "main.py",
    "--game_dir",
    f"./games_descriptions/{GAME}",
]


# Print experiment settings
print(f"Running {N} iterations ")
print(f"Saving in folder: {GAME}")

for i in range(1, N + 1):
    print(f"Running iteration {i}/{N}...")

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
