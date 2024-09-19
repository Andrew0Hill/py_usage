#!/bin/bash

# Default output path is 'job_stats.txt'.
OUTPUT_PATH=${1:-"job_stats.txt"}

# Default interval is 5 seconds.
INTERVAL=${2:-5}

# Activate virtual environment
source $HOME/vm_env/bin/activate

# We may not be executing from the working directory, so figure out where we are.
SCRIPT_DIR=$(dirname -- "$0")
SCRIPT_DIR_PATH=$(realpath "$SCRIPT_DIR")

# Run the statistics script.
python "$SCRIPT_DIR_PATH/get_usage.py" --output_file=$OUTPUT_PATH --interval=$INTERVAL
