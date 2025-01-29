import argparse
import subprocess
import time
import json

def get_command(exp_name):
    with open('reproduce.json') as f:
        data = json.load(f)
    if exp_name in data:
        return data[exp_name]
    else:
        raise ValueError(f"Experiment {exp_name} not found")

def run_experiment(args):
    # Number of iterations
    N = 20


    # Command to run
    command = get_command(args.exp_name)
    command = [args.python_name, "main.py"] + command


    # Print experiment settings
    print(f"Running {N} iterations for experiment {args.exp_name}")

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

def main():
    parser = argparse.ArgumentParser(description='Experiment script')
    parser.add_argument('--exp_name', type=str, required=True, help='Name of the experiment')
    parser.add_argument('--python_name', type=str, default="python", help='Name of the python executable')
    args = parser.parse_args()
    
    run_experiment(args)

if __name__ == "__main__":
    main()