#!/bin/bash

current_dir=$(pwd)

# set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$current_dir

# print usage if no script file provide
if [ -z "$1" ]; then
    echo "Usage: sh py3.sh <script_path> [<args>...]"
    exit 1
fi

# run
python3 "$@"