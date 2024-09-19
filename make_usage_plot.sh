#!/bin/bash

# Use can specify input prefix, but default is job_stats (the default output for get_usage.py)
INPUT_PREFIX=${1:-"job_stats"}

# Activate virtual environment
source $HOME/vm_env/bin/activate

# Run the plotting script.
# The --stats line determines which outputs are included in the plot.
python3 make_usage_plot.sh --input_prefix="$INPUT_PREFIX" \
                           --stats mem cpu disk \
