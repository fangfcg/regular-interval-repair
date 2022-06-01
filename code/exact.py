import os
import pandas as pd
import numpy as np


def determine_interval(t):
    eps = [t[i] - t[i-1] for i in range(1,len(t-1))]
    return np.median(eps)

def match_searching(t, eps_t, s_0, lmd_a, lmd_d):
    n = len(t)
    dp = [[] for i in range(n+1)]
    op = [[] for i in range(n+1)]
    dp[0].append(0)
    op[0].append(0)
    for i in range(1,n+1):
        dp[i].append(i*lmd_d)
        op[i].append(2)
    m_best = 10e8
    m_ub = 10e8
    min_cost = 10e8
    m = 1
    while m <= m_ub:
        dp[0].append(m*lmd_a)
        op[0].append(1)
        for i in range(1,n+1):
            s_m = s_0 + (m-1)*eps_t
            move_res = dp[i-1][m-1]+abs(t[i-1]-s_m)
            add_res = dp[i][m - 1] + lmd_a
            del_res = dp[i-1][m]+lmd_d
            if move_res <= add_res and move_res <= del_res:
                dp[i].append(move_res)
                op[i].append(0)
            elif add_res <= move_res and add_res <= del_res:
                dp[i].append(add_res)
                op[i].append(1)
            else:
                dp[i].append(del_res)
                op[i].append(2)

        if dp[n][m] < min_cost:
            min_cost = dp[n][m]
            m_best = m
            m_ub = np.floor(min_cost/lmd_a)+n

        m += 1

    M = trace_back(op, t, (s_0, eps_t, m_best))
    return M, min_cost, m_best


def trace_back(op, t, s):
    s_0, eps_t, m_best = s
    n = len(t)
    M = []
    i = n
    j = m_best
    while i > 0 and j > 0:
        if op[i][j] == 0:
            M.append((i-1,j-1))
            i = i - 1
            j = j - 1
        elif op[i][j] == 1:
            M.append((-1, j-1))
            j = j - 1
        else:
            M.append((i-1, -1))
            i = i - 1
    M.reverse()
    return M


def round_to_granularity(value, granularity):
    return round(value / granularity) * granularity

def exact_repair(t, lmd_a=10, lmd_d=10, interval_granularity=1, start_point_granularity=1, bias_d=1, bias_s=3):
    eps_list = [t[i] - t[i - 1] for i in range(1, len(t) - 1)]
    eps_md = np.median(eps_list)
    eps_t = round_to_granularity(eps_md, interval_granularity)
    eps_t_traverse_range = set()
    eps_t_traversed = set()
    min_cost = 10e8

    while True:
        d = 0
        while (d == 0 or check_st_lb(d, eps_list, min_cost, lmd_d, eps_t)) and d < len(eps_list) and d < bias_d:
            s_0 = t[d]
            flag_increase = False
            flag_decrease = False
            min_cost_change = False
            while s_0 <= t[d] + bias_s:
                M, cost, m = match_searching(t, eps_t, s_0, lmd_a, lmd_d)
                if cost < min_cost:
                    min_cost, m_best, min_eps_t, min_s_0 = cost, m, eps_t, s_0
                    min_cost_change = True
                    s_0 += start_point_granularity
                else:
                    flag_increase = True
                    break
            
            s_0 = t[d]-1
            while s_0 >= t[d] - bias_s:
                s_0 -= start_point_granularity
                M, cost, m = match_searching(t, eps_t, s_0, lmd_a, lmd_d)
                if cost < min_cost:
                    min_cost, m_best, min_eps_t, min_s_0 = cost, m, eps_t, s_0
                    min_cost_change = True
                else:
                    flag_decrease = True
                    break
            if flag_increase and flag_decrease:
                break
            d += 1

        if not min_cost_change or (not check_interval_lb(eps_t, min_cost, eps_list)):
            break
        if (eps_t + interval_granularity) not in eps_t_traversed and (eps_t + interval_granularity) <= round_to_granularity(eps_md, interval_granularity) + interval_granularity:
            eps_t_traverse_range.add((eps_t + interval_granularity))
        if (eps_t - interval_granularity) not in eps_t_traversed and (eps_t - interval_granularity) >= round_to_granularity(eps_md, interval_granularity) + interval_granularity:
            eps_t_traverse_range.add((eps_t - interval_granularity))
        eps_t_traversed.add(eps_t)
        if len(eps_t_traverse_range) == 0:
            break
        eps_t = eps_t_traverse_range.pop()

    return min_eps_t, min_s_0, m_best

def check_interval_lb(interval, min_cost, eps_list):
    c = 0
    for eps in eps_list:
        c += abs(interval - eps)
    return (c <= min_cost)


def check_st_lb(d, eps_list, min_cost, lmd_d, eps_t):
    c = d * lmd_d
    for eps in eps_list[d:]:
        c += abs(eps_t - eps)
    return c < min_cost












