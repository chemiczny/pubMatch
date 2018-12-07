#!/bin/env bash
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --time=72:00:00
#SBATCH --mem-per-cpu=120GB
##### Nazwa kolejki
#SBATCH -p plgrid

module add plgrid/tools/python/3.6.5

python3 run.py &> output.log
