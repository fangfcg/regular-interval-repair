import os
import pandas as pd
import numpy as np

def determine_interval(t, interval_granularity):
    eps_list = [t[i] - t[i-1] for i in range(1, len(t))]
    eps_md = np.median(eps_list)
    eps = round(eps_md / interval_granularity) * interval_granularity
    return eps


def start_point_approximation(t, lmd_a=5, lmd_d=5, interval_granularity=1000):
    n = len(t)
    eps_t = determine_interval(t, interval_granularity)
    s_0 = t[0]
    dp = [[] for i in range(n + 1)]
    op = [[] for i in range(n + 1)]
    dp[0].append(0)
    op[0].append(0)
    for i in range(1, n + 1):
        dp[i].append(i * lmd_d)
        op[i].append(2)
    m_best = 10e8
    m_ub = 10e8
    min_cost = 10e8
    m = 1
    while m <= m_ub:
        dp[0].append(m * lmd_a)
        op[0].append(1)
        # print("exact", m)
        for i in range(1, n + 1):
            s_m = s_0 + (m - 1) * eps_t
            move_res = dp[i - 1][m - 1] + abs(t[i - 1] - s_m)
            add_res = dp[i][m - 1] + lmd_a
            del_res = dp[i - 1][m] + lmd_d
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
            m_ub = np.floor(min_cost / lmd_a) + n

        m += 1

    return min_cost, eps_t, s_0, m_best

def median_approximation(t, lmd_a=5, lmd_d=5, interval_granularity=1):
    n = len(t)
    eps_t = determine_interval(t, interval_granularity)
    # print(eps_t)
    n_md = int(np.floor(n/2))
    s_md = np.median(t)

    dp_l = [[] for i in range(n_md+1)]
    dp_r = [[] for i in range(n_md+1)]
    op_l = [[] for i in range(n_md+1)]
    op_r = [[] for i in range(n_md+1)]

    dp_l[0].append(0)
    op_l[0].append(0)
    dp_r[0].append(0)
    op_r[0].append(0)

    for i in range(1,n_md+1):
        dp_l[i].append(i* lmd_d)
        op_l[i].append(2)
        dp_r[i].append(i * lmd_d)
        op_r[i].append(2)

    m_best = 10e8
    m_ub = 10e8
    min_cost = 10e8
    m = 1

    while m <= m_ub:
        # print("approximate", m)
        dp_l[0].append(m*lmd_a)
        op_l[0].append(1)
        dp_r[0].append(m * lmd_a)
        op_r[0].append(1)

        for i in range(1, n_md+1):
            if n % 2 == 1:
                s_m_l = s_md - m * eps_t
                s_m_r = s_md + m * eps_t
                t_i_l = t[int((n-1)/2)-i]
                t_i_r = t[int((n+1)/2)+(i-1)]
            else:
                s_m_l = s_md - (m - 0.5)*eps_t
                s_m_r = s_md + (m - 0.5)*eps_t
                t_i_l = t[int(n / 2)-i]
                t_i_r = t[int(n / 2)+i-1]

            move_res_l = dp_l[i - 1][m - 1] + abs(t_i_l - s_m_l)
            move_res_r = dp_r[i - 1][m - 1] + abs(t_i_r - s_m_r)
            add_res_l = dp_l[i][m - 1] + lmd_a
            add_res_r = dp_r[i][m - 1] + lmd_a
            del_res_l = dp_l[i - 1][m] + lmd_d
            del_res_r = dp_r[i - 1][m] + lmd_d

            min_res_l = min(move_res_l, add_res_l, del_res_l)
            if move_res_l == min_res_l:
                dp_l[i].append(move_res_l)
                op_l[i].append(0)
            elif add_res_l == min_res_l:
                dp_l[i].append(add_res_l)
                op_l[i].append(1)
            else:
                dp_l[i].append(del_res_l)
                op_l[i].append(2)

            min_res_r = min(move_res_r, add_res_r, del_res_r)
            if move_res_r == min_res_r:
                dp_r[i].append(move_res_r)
                op_r[i].append(0)
            elif add_res_r == min_res_r:
                dp_r[i].append(add_res_r)
                op_r[i].append(1)
            else:
                dp_r[i].append(del_res_r)
                op_r[i].append(2)


        if dp_r[n_md][m] + dp_l[n_md][m] < min_cost:
            min_cost = dp_r[n_md][m] + dp_l[n_md][m]
            m_best = m
            if n % 2 == 1:
                m_ub = (int(np.floor(min_cost/lmd_a + n)) - 1) / 2
            else:
                m_ub = (int(np.floor(min_cost / lmd_a + n))) / 2
        m += 1

    if n % 2 == 1:
        s_0 = s_md - m_best * eps_t
        m = m_best * 2 + 1
    else:
        s_0 = s_md - (m_best - 0.5) * eps_t
        m = m_best * 2

    return min_cost, eps_t, s_0, m


def trace_back(op, t, s):
    s_0, eps_t, m_best = s
    n = len(t)
    M = []
    i = n - 1
    j = m_best - 1
    while i >= 0 and j >= 0:
        if op[i][j] == 0:
            M.append((i,j))
            i = i - 1
            j = j - 1
        elif op[i][j] == 1:
            M.append((-1, j))
            j = j - 1
        else:
            M.append((i, -1))
            i = i - 1
    M.reverse()
    return M

def median_approximation_all(t, lmd_a=5, lmd_d=5, interval_granularity=1):

    print("approximate:median")
    median_min_cost, median_eps_t, median_s_0, median_m = median_approximation(t, lmd_a, lmd_d, interval_granularity)
    print("approximate:start point")
    sp_min_cost, sp_eps_t, sp_median_s_0, sp_m = start_point_approximation(t, lmd_a, lmd_d, interval_granularity)

    if median_min_cost <= sp_min_cost:
        return median_eps_t, median_s_0, median_m
    else:
        return sp_eps_t, sp_median_s_0, sp_m










