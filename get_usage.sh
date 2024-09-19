#!/bin/bash
OUTPUT_PATH=${1:-"job_stats.txt"}
INTERVAL=${2:-5}

source $HOME/vm_env/bin/activate

python get_usage.py --output_file=$OUTPUT_PATH --interval=$INTERVAL
