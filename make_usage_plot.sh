#!/bin/bash

# Use can specify input prefix, but default is job_stats (the default output for get_usage.py)
INPUT_PREFIX=${1:-"job_stats"}

# Activate virtual environment
source $HOME/vm_env/bin/activate

SCRIPT_DIR=$(dirname -- "$0")
SCRIPT_DIR_PATH=$(realpath "$SCRIPT_DIR")

# Run the plotting script.
# The --stats line determines which outputs are included in the plot.
python3 "$SCRIPT_DIR_PATH/make_usage_plot.py" --input_prefix="$INPUT_PREFIX" \
                                              --stats mem cpu disk \
