## README
#### File Sturcture

- `code/` provides the codes for the experiments
  - `code/exact.py`: the exact method in Section 3
  - `code/exact_v.py`: the exact method considering data characteristics in Section 3
  - `code/approximate.py`: the median approximation algorithm in Section 4
  - `code/metrics.py`: metrics for evaluation
  - `code/main.py`: the main evaluation entry
- `data/` provides the datasets used in the experiments
  - `energy, pm, syn_labdata` are the ground truth datasets
  - `dirty_xxx` are the datasets with errors
- `iotdb-udf/` provides source code of the user defined function in time series db iotdb
  - `src` provides source code in java
  - `out` provides jar package for regestering in iotdb 



#### Example Invocation

requirement:

```
pandas = 1.1.x
```

example invocation:

```powershell
cd ./code/
python main.py
```
