# MLHC 2018 - Reproducible Survival Prediction with SEER Cancer Data
This repository contains the code that was used for experiments reported in _Reproducible Survival Prediction with SEER Cancer Data_ submitted to the Machine Learning for Healthcare 2018 conference.

Repository overview:
- **/bin/cluster**: Slurm submission scripts for all parameter tuning experiments on the HPC cluster.
- **/cohort**: SEER*Stat session files to reproduce cohort selections.
- **/example**: Randomly generated SEER example to test the software without sensitive data.
- **/example/CASES.csv**: Example case export. To reproduce experiments, this should be generated for each cohort by loading the provided session files into SEER*Stat, executing the case listing, and exporting it via Matrix->Export->Results as Text File... with "CSV Defaults".
- **/example/INCIDENCES.txt**: Example SEER incidences. To reproduce experiments, this should contain all incidences provided by SEER 1973-2014 data (November 2016 submission) in ASCII format (e.g. by merging them into a single file). The according ASCII data files are available from SEER on request.
- **/lib**: Python classes and functions used for the experiments.
- **main.py**: Main routine to perform the experiments.
- **requirements.txt**: Python dependencies (can be installed with pip, e.g. in a virtual environment).

To execute main.py and reproduce our experiments Python3 (we used version 3.5.2) is necessary and all dependencies in requirements.txt must be satisfied. The easiest way would be to setup an according [virtual environment and to install requirements with pip](https://docs.python.org/3/tutorial/venv.html).

The option -h gives an overview of all command line arguments. Note that this code provides some additional functionality such as SVM models and survival regression that were not used for the paper's experiments.

```
$ python main.py -h
```

An experiment with the randomly generated examples and an MLP model can be performed as shown below. This will produce a folder in the current directory containing results and a plot for the AUC score.

```
$ python main.py --incidences example/INCIDENCES.txt --specifications example/read.seer.research.nov2016.sas --cases example/CASES.csv --task survival60 --oneHotEncoding --model MLP --mlpLayers 2 --mlpWidth 20 --mlpEpochs 1 --mlpDropout 0.1 --importance --plotData --plotResults
[...]
Read ASCII data files.
Raw data: (10000; 133) cases and attributes
Filtered SEER*Stat cases from ASCII: (5000; 133) cases and attributes
Remove irrelevant, combined, post-diagnosis, and treatment attributes: (5000; 960) cases and attributes
Create target label indicating cancer survival for survival60: (2831; 959) cases and attributes
Remove inputs with constant values: (2831; 925) cases and attributes
Data:  (2831, 925) -> x:(2831, 924), y:(2831,)
Train: x:(2264, 924), y:(2264,)
Valid: x:(283, 924), y:(283,)
Test:  x:(284, 924), y:(284,)

Train on 2264 samples, validate on 283 samples
Epoch 1/1
 - 1s - loss: 0.4241 - acc: 0.8913 - val_loss: 0.2623 - val_acc: 0.9293
Validation results: auc = 0.48878326996197724, f1 = 0.9633699633699635, acc = 0.9293286219081273
```
