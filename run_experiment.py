import subprocess
import time

# Number of iterations
N = 20

# Command to run
command = [
    "python3",
    "main.py",
    "--game_dir",
    "./games_descriptions/game3",
]

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
