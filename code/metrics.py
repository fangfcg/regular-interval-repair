import math
from collections import defaultdict
import numpy as np
import numpy as np

def cal_rmse(truth, repair):
    min_len = min(len(truth), len(repair))
    truth, repair = truth[:min_len], repair[:min_len]
    diff = abs(truth - repair)
    diff = diff.map(lambda x:math.pow(x,2))
    res = math.sqrt(sum(diff) / len(diff))
    return res

def calAccuracy(truth, fault, repair):
    min_len = min(len(truth), len(fault), len(repair))
    truth, fault, repair = truth[:min_len], fault[:min_len], repair[:min_len]
    error = sum(abs(truth - repair))
    cost = sum(abs(fault - repair))
    inject = sum(abs(truth - fault))
    if error == 0:
        return 1
    return (1 - (error / (cost + inject)))


def calDTW(truth, repair):
    d = DTW(truth, repair)
    return d

def cal_cost(truth, repair, lmd_a=5, lmd_d=5):
    s1 = repair
    s2 = truth
    n = len(s1)
    m = len(s2)
    dp = [[] for _ in range(n + 1)]
    dp[0].append(0)

    lmd_a = lmd_a * (truth[1] - truth[0])
    lmd_d = lmd_d * (truth[1] - truth[0])
    for i in range(1,n+1):
        dp[i].append(i*lmd_d)

    for j in range(1,m+1):
        dp[0].append(j*lmd_a)
        for i in range(1,n+1):
            s_m = s2[j-1]
            move_res = dp[i-1][j-1] + abs(s1[i-1]-s_m)
            add_res = dp[i][j - 1] + lmd_a
            del_res = dp[i-1][j]+lmd_d
            if move_res <= add_res and move_res <= del_res:
                dp[i].append(move_res)
            elif add_res <= move_res and add_res <= del_res:
                dp[i].append(add_res)
            else:
                dp[i].append(del_res)

    return dp[n][m]


def distance(w1, w2):
    d = abs(w2 - w1)
    return d


def DTW(s1, s2):
    m = len(s1)
    n = len(s2)

    dp = np.zeros((m, n))

    for i in range(m):
        dp[i][0] = abs(s1[i] - s2[0])
    for j in range(n):
        dp[0][j] = abs(s1[0] - s2[j])

    for j in range(1, n):
        for i in range(1, m):
            dp[i][j] = min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1]) + abs(s1[i] - s2[j])
    return dp[-1][-1]
