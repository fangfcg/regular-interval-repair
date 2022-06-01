import os
import numpy as np
import pandas as pd
from datetime import datetime
from exact import exact_repair
from exact_v import exact_repair_v
from approximation import median_approximation_all
from metrics import cal_rmse, cal_cost, calDTW, calAccuracy
import time

def time2ts(seq, time_scale):
    ts_list = []
    for t in list(seq):
        timeArray = datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f")
        timeStamp = float(timeArray.timestamp()) * time_scale
        ts_list.append(timeStamp)
    return ts_list


def equal_series_generate(eps_t, s_0, m):
    return [s_0 + i*eps_t for i in range(m)]


def metric_res(repair, truth, fault, metric_name="cost"):
    """
    :param metric_id: 0: repair cost metric, 1: dtw metric, 2:rmse metric
    :return: loss
    """
    if metric_name == "cost":
        lmd_a = 5 * (truth[1] - truth[0])
        lmd_d = 5 * (truth[1] - truth[0])
        return cal_cost(truth, repair, lmd_a, lmd_d)
    elif metric_name == "dtw":
        return calDTW(truth, repair)
    elif metric_name == "accuracy":
        truth = pd.Series(truth)
        repair = pd.Series(repair)
        return calAccuracy(truth, fault, repair)
    else:
        truth = pd.Series(truth)
        repair = pd.Series(repair)
        return cal_rmse(truth, repair)


if __name__ == "__main__":
    parameters = {
        "energy":{
            "file_counts": 5,
            "truth_col": 1,
            "truth_dir": "../data/energy",
            "original_col": 1,
            "original_dir": "../data/dirty_energy",
            "start_point_granularity": 1,
            "interval_granularity": 1,
            "lmd_a": 100,
            "lmd_d": 100,
        },
    }

    version = "-test"
    datasets = ["energy"]
    metrics = ["rmse"]
    methods = ["exact", "approximate"]
    data_characteristic = False
    result_dfs = {}
    for m in metrics:
        result_dfs[m] = pd.DataFrame(0, columns=methods, index=datasets)
        result_dfs[m] = result_dfs[m].astype("float32")
    result_dfs["time"] = pd.DataFrame(0, columns=methods, index=datasets)
    result_dfs["time"] = result_dfs["time"].astype("float32")

    for dataset in datasets:
        param = parameters[dataset]
        file_counts = param["file_counts"]
        result_map = {}
        for method in methods:
            for metric in metrics:
                result_map[f'{method}-{metric}'] = []
            result_map[f'{method}-time'] = []

        dataset_path = os.path.join("./result", dataset)
        print(os.path.abspath("./"))
        if not os.path.exists(dataset_path):
            os.mkdir(dataset_path)
        for ts in range(file_counts):
            print(ts)
            original_dir = param["original_dir"]
            file_name = os.path.join(original_dir, f"series_{ts}.csv")
            data = pd.read_csv(file_name)
            original_seq = data.iloc[:, param["original_col"]]
            source_values = None
            # source_values = data.iloc[:, param["original_col"] + 1] # values

            truth_dir = param["truth_dir"]
            data_truth = pd.read_csv(os.path.join(truth_dir, f"series_{ts}.csv"))
            ground_truth_seq = data_truth.iloc[:, param["truth_col"]]

            if "time_scale" in param:
                original = time2ts(original_seq, param["time_scale"])
                truth = time2ts(ground_truth_seq, param["time_scale"])
            else:
                original = list(original_seq)
                truth = list(ground_truth_seq)

            lmd_a = param["lmd_a"]
            lmd_d = param["lmd_d"]
            interval_granularity = param["interval_granularity"]
            start_point_granularity = param["start_point_granularity"]

            start = time.time()
            if data_characteristic:
                eps_t_e, s_0_e, m_e = exact_repair_v(original, source_values, lmd_a, lmd_d, interval_granularity, start_point_granularity)
            else:
                eps_t_e, s_0_e, m_e = exact_repair(original, lmd_a, lmd_d, interval_granularity, start_point_granularity)
            print("exact end")
            end = time.time()
            exact_time = end - start

            start = time.time()
            eps_t_a, s_0_a, m_a = median_approximation_all(original, lmd_a, lmd_d, interval_granularity)
            print("approximate end")
            end = time.time()
            appro_time = end - start

            exact_res = equal_series_generate(eps_t_e, s_0_e, m_e)
            appro_res = equal_series_generate(eps_t_a, s_0_a, m_a)

            for metric in metrics:
                print(metric, "exact")
                result_map[f"exact-{metric}"].append(metric_res(exact_res, truth, original,metric))
                print(metric, "approximate")
                result_map[f"approximate-{metric}"].append(metric_res(appro_res, truth, original, metric))
            result_map[f"exact-time"].append(exact_time)
            result_map[f"approximate-time"].append(appro_time)

        for metric in (metrics + ["time"]):
            result_dfs[metric].at[dataset, "exact"] = np.mean(result_map[f"exact-{metric}"])
            np.savetxt(os.path.join(dataset_path, f"exact-{metric}{version}.txt"), result_map[f"exact-{metric}"])
            result_dfs[metric].at[dataset, "approximate"] = np.mean(result_map[f"approximate-{metric}"])
            np.savetxt(os.path.join(dataset_path, f"approximate-{metric}{version}.txt"), result_map[f"approximate-{metric}"])

    for metric in (metrics + ["time"]):
        result_dfs[metric].to_csv(os.path.join("result", f"exp1-{metric}{version}.csv"))



