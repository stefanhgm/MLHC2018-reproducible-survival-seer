#!/bin/bash

# SLURM submission file for parameter tuning on the HPC PALMA cluster.
# https://www.uni-muenster.de/ZIV/en/Technik/PALMA/index.html

# set the number of nodes
#SBATCH --nodes=1

# set the number of CPU cores per node
#SBATCH --ntasks-per-node 2

# set a partition
#SBATCH --partition normal,u0dawin

# set max wallclock time
#SBATCH --time=24:00:00

# set name of job
#SBATCH --job-name=SEER-MLPEmb-LUNG-2004

# mail alert at start, end and abortion of execution
#SBATCH --mail-type=ALL

# set an output file
#SBATCH --output output.dat

# send mail to this address
#SBATCH --mail-user=mail@uni-muenster.de

# array job
#SBATCH --array=0-863

# In the u0dawin queue, you will need the following line
source /etc/profile.d/modules.sh; source /etc/profile.d/modules_local.sh

# Python venv
source /home/user/VirtualEnv/bin/activate

# constant arguments
OUTPUT=/home/user/experiments/LUNG2004_MLPEmb_SURV12
INCIDENCES=/home/user/SEER-Dataset/RESPIR_MERGED_2004_2009.TXT
SPECIFICATIONS=/home/user/SEER-Dataset/SEER_1973_2014_TEXTDATA/incidence/read.seer.research.nov16.sas
CASES=/home/user/SEER-Dataset/SEERStat/Lung_2004_2009_229011.csv

# parameters
# TASK=(survival12 survival60 mort12 mort60)
TASK=(survival12)
# ONE_HOT_ENCODING=(False True)
ONE_HOT_ENCODING=(True)

# MODEL=(MLP MLPEmb LogR NAIVE)
MODEL=(MLPEmb)

# MLP* parameters - 288 combinations
MLP_LAYERS=(1 2 3 4)
MLP_WIDTH=(20 50 100 200)
MLP_DROPOUT=(0.0 0.1 0.2 0.3 0.4 0.5)
MLP_EPOCHS=(20 50 100)

# MLPEmb parameters
# MLP_EMB_NEURONS=(3 5 10)
MLP_EMB_NEURONS=(3 5 10)

# LogR parameters
# LOGR_C=(0.01 0.1 1.0 10.0 100.0 1000.0 10000.0 100000.0 1000000.0 10000000.0 100000000.0 1000000000.0 10000000000.0)
LOGR_C=(1.0)

# parameter indices
ita=$(($SLURM_ARRAY_TASK_ID % ${#TASK[@]}))
ioh=$(($SLURM_ARRAY_TASK_ID / ${#TASK[@]} % ${#ONE_HOT_ENCODING[@]}))
imo=$(($SLURM_ARRAY_TASK_ID / ${#TASK[@]} / ${#ONE_HOT_ENCODING[@]} % ${#MODEL[@]}))
iml=$(($SLURM_ARRAY_TASK_ID / ${#TASK[@]} / ${#ONE_HOT_ENCODING[@]} / ${#MODEL[@]} % ${#MLP_LAYERS[@]}))
imw=$(($SLURM_ARRAY_TASK_ID / ${#TASK[@]} / ${#ONE_HOT_ENCODING[@]} / ${#MODEL[@]} / ${#MLP_LAYERS[@]} % ${#MLP_WIDTH[@]}))
imd=$(($SLURM_ARRAY_TASK_ID / ${#TASK[@]} / ${#ONE_HOT_ENCODING[@]} / ${#MODEL[@]} / ${#MLP_LAYERS[@]} / ${#MLP_WIDTH[@]} % ${#MLP_DROPOUT[@]}))
ime=$(($SLURM_ARRAY_TASK_ID / ${#TASK[@]} / ${#ONE_HOT_ENCODING[@]} / ${#MODEL[@]} / ${#MLP_LAYERS[@]} / ${#MLP_WIDTH[@]} / ${#MLP_DROPOUT[@]} % ${#MLP_EPOCHS[@]}))
icn=$(($SLURM_ARRAY_TASK_ID / ${#TASK[@]} / ${#ONE_HOT_ENCODING[@]} / ${#MODEL[@]} / ${#MLP_LAYERS[@]} / ${#MLP_WIDTH[@]} / ${#MLP_DROPOUT[@]} / ${#MLP_EPOCHS[@]} %  ${#MLP_EMB_NEURONS[@]}))
ilc=$(($SLURM_ARRAY_TASK_ID / ${#TASK[@]} / ${#ONE_HOT_ENCODING[@]} / ${#MODEL[@]} / ${#MLP_LAYERS[@]} / ${#MLP_WIDTH[@]} / ${#MLP_DROPOUT[@]} / ${#MLP_EPOCHS[@]} /  ${#MLP_EMB_NEURONS[@]} % ${#LOGR_C[@]}))

# Transform boolean arguments
if [ "${ONE_HOT_ENCODING[$ioh]}" == "False" ] ; then
    ENCODE_INPUTS_BOOL=" "
fi

python /home/user/Code/main.py --output ${OUTPUT} --incidences ${INCIDENCES} --specifications ${SPECIFICATIONS} --cases ${CASES} --task ${TASK[$ita]} ${ENCODE_INPUTS_BOOL:---oneHotEncoding} --model ${MODEL[$imo]} --mlpLayers ${MLP_LAYERS[$iml]} --mlpWidth ${MLP_WIDTH[$imw]} --mlpDropout ${MLP_DROPOUT[$imd]} --mlpEpochs ${MLP_EPOCHS[$ime]} --mlpEmbNeurons ${MLP_EMB_NEURONS[$icn]} --logrC ${LOGR_C[$ilc]} --test --importance
