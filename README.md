# MLHC2018-reproducible-survival-seer
Machine Learning for Healthcare 2018 - Reproducible Survival Prediction with SEER Cancer Data

```
$ python main.py --output . --incidences example/INCIDENCES.txt --specifications /home/stefanhgm/Sciebo/SEER-Dataset/SEER_1973_2014_TEXTDATA/incidence/read.seer.research.nov16.sas --cases example/CASES.csv --task survival60 --oneHotEncoding --model MLPConv --mlpLayers 2 --mlpWidth 20 --mlpEpochs 1 --mlpDropout 0.1 --mlpConvNeurons 3 --test --importance --plotData --plotResults
[...]
Read ASCII data files.
Raw data: (10000; 133) cases and attributes
Filtered SEER*Stat cases from ASCII: (5000; 133) cases and attributes
Remove irrelevant, combined, post-diagnosis, and treatment attributes: (5000; 960) cases and attributes
Create target label indicating cancer survival for survival60: (2780; 959) cases and attributes
Remove inputs with constant values: (2780; 925) cases and attributes
Data:  (2780, 925) -> x:(2780, 924), y:(2780,)
Train: x:(2224, 924), y:(2224,)
Valid: x:(278, 924), y:(278,)
Test:  x:(278, 924), y:(278,)
Embed input data.

Train on 2224 samples, validate on 278 samples
Epoch 1/1
 - 7s - loss: 0.4274 - acc: 0.8903 - val_loss: 0.4000 - val_acc: 0.8705
Validation results: auc = 0.4874885215794307, f1 = 0.9307692307692308, acc = 0.8705035971223022
Test results: auc = 0.4567588932806324, f1 = 0.9529190207156308, acc = 0.9100719424460432
```
