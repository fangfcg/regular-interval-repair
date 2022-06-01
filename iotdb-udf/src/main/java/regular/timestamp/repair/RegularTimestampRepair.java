package regular.timestamp.repair;

import org.apache.iotdb.db.query.udf.api.access.Row;
import org.apache.iotdb.db.query.udf.api.access.RowIterator;

import java.util.ArrayList;
import regular.timestamp.repair.Utils;
import java.io.*;
import java.util.*;
import java.text.SimpleDateFormat;

import static com.google.common.math.IntMath.pow;
import static java.lang.Math.abs;
import static java.lang.Math.min;


public class RegularTimestampRepair {
  protected int n;
  protected long time[];
  protected double original[];
  protected long repairedTime[];
  protected boolean repairedFlag[];
  protected double repairedValue[];
  protected long lmb_d;
  protected long lmb_a;
  private long lmd_a;
  private long lmd_d;
  private long interval_gran;
  private long st_gran;
  private long interval;

  public RegularTimestampRepair(RowIterator dataIterator, int lmd_a_, int lmd_d_, int interval_gran_, int st_gran_) throws Exception{
    lmd_a = lmd_a_;
    lmd_d = lmd_d_;
    interval_gran = interval_gran_;
    st_gran = st_gran_;
    ArrayList<Long> timeList = new ArrayList<>();
    ArrayList<Double> originList = new ArrayList<>();
    while (dataIterator.hasNextRow()) { // read data
      Row row = dataIterator.next();
      double v = Utils.getValueAsDouble(row);
      timeList.add(row.getTime());
      if (!Double.isFinite(v)) { // deal with nan and special values
        originList.add(Double.NaN);
      } else {
        originList.add(v);
      }
    }
    // save time series
    time = Utils.toLongArray(timeList);
    original = Utils.toDoubleArray(originList);
    n = time.length;
  }

  public void repair(){
    interval = determineInterval();
    medianApproximation(interval);
  }

  public void medianApproximation(long interval){
    ArrayList<Long>[] dp = new ArrayList[n];
    ArrayList<Integer>[] op = new ArrayList[n];
    long eps_t = interval;
    int n_md = n/2;
    long s_md = median(time);

    ArrayList<Long>[] dp_l = new ArrayList[n_md + 1];
    ArrayList<Long>[] dp_r = new ArrayList[n_md + 1];
    ArrayList<Integer>[] op_l = new ArrayList[n_md + 1];
    ArrayList<Integer>[] op_r = new ArrayList[n_md + 1];
    for (int i = 0; i < n_md+1; i++) {
      dp_l[i] = new ArrayList<Long>();
      dp_r[i] = new ArrayList<Long>();
      op_l[i] = new ArrayList<Integer>();
      op_r[i] = new ArrayList<Integer>();
    }


    dp_l[0].add((long)0);
    dp_r[0].add((long)0);
    op_l[0].add(0);
    op_r[0].add(0);

    for (int i = 1; i < n_md + 1; i++) {
      dp_l[i].add(i*lmd_d);
      op_l[i].add(2);
      dp_r[i].add(i * lmd_d);
      op_r[i].add(2);
    }

    int m_best = Integer.MAX_VALUE;
    int m_ub = Integer.MAX_VALUE;
    long min_cost = Long.MAX_VALUE;
    int m = 1;

    while(m <= m_ub) {
      dp_l[0].add(m*lmd_a);
      op_l[0].add(1);
      dp_r[0].add(m * lmd_a);
      op_r[0].add(1);
      for (int i = 1; i < n_md+1; i++) {
        long s_m_l;
        long s_m_r;
        long t_i_l;
        long t_i_r;
        if (n % 2 == 1) {
          s_m_l = s_md - m * eps_t;
          s_m_r = s_md + m * eps_t;
          t_i_l = time[(int) ((n - 1) / 2) - i];
          t_i_r = time[(int) ((n + 1) / 2) + (i - 1)];
        } else {
          s_m_l = s_md - (long) ((m - 0.5) * eps_t);
          s_m_r = s_md + (long) ((m - 0.5) * eps_t);
          t_i_l = time[(n / 2) - i];
          t_i_r = time[(n / 2) + i - 1];
        }
        long move_res_l = dp_l[i - 1].get(m - 1) + abs(t_i_l - s_m_l);
        long move_res_r = dp_r[i - 1].get(m - 1) + abs(t_i_r - s_m_r);
        long add_res_l = dp_l[i].get(m - 1) + lmd_a;
        long add_res_r = dp_r[i].get(m - 1) + lmd_a;
        long del_res_l = dp_l[i - 1].get(m) + lmd_d;
        long del_res_r = dp_r[i - 1].get(m) + lmd_d;

        if ((move_res_l <= add_res_l) && (move_res_l <= del_res_l)) {
          dp_l[i].add(move_res_l);
          op_l[i].add(0);
        } else if ((add_res_l <= move_res_l) && (add_res_l <= del_res_l)) {
          dp_l[i].add(add_res_l);
          op_l[i].add(1);
        } else {
          dp_l[i].add(del_res_l);
          op_l[i].add(2);
        }

        if ((move_res_r <= add_res_r) && (move_res_r <= del_res_r)) {
          dp_r[i].add(move_res_r);
          op_r[i].add(0);
        } else if ((add_res_r <= move_res_r) && (add_res_r <= del_res_r)) {
          dp_r[i].add(add_res_r);
          op_r[i].add(1);
        } else {
          dp_r[i].add(del_res_r);
          op_r[i].add(2);
        }
      }
      if (dp_r[n_md].get(m) + dp_l[n_md].get(m) < min_cost) {
        min_cost = dp_r[n_md].get(m) + dp_l[n_md].get(m);
        m_best = m;
        if (n % 2 == 1) {
          m_ub = ((int) (min_cost / lmd_a + n) - 1) / 2;
        } else {
          m_ub = ((int) (min_cost / lmd_a + n)) / 2;
        }
      }
      m += 1;
    }


    int total_length;
    if (n % 2 == 1) {
      total_length = m_best * 2 + 1;
    }
    else{
      total_length = m_best * 2;
    }

    repairedTime = new long[total_length];
    repairedValue = new double[total_length];
    repairedFlag = new boolean[total_length];
    for (int i = 0; i < repairedFlag.length; i++){
      repairedFlag[i] = false;
    }
    if (n % 2 == 1){
      for (int i = 0; i <= m_best; i++){
        repairedTime[m_best+i] = s_md + i*eps_t;
        repairedTime[m_best-i] = s_md - i*eps_t;
      }
    }
    else {
      for (int i = 0; i < m_best; i++){
        repairedTime[m_best+i] = s_md + i*eps_t + eps_t/2;
        repairedTime[m_best-i-1] = s_md - i*eps_t - eps_t/2;
      }
    }

    int i = n_md;
    int j = m_best;
    while ((i > 0) && (j > 0)) {
      if (op_r[i].get(j) == 0) {
        if (n % 2 == 0) {
          repairedValue[m_best+j-1] = original[n_md+i-1];
          repairedFlag[m_best+j-1] = true;
        }
        else {
          repairedValue[m_best+j] = original[n_md+i];
          repairedFlag[m_best+j] = true;
        }
        i = i - 1;
        j = j - 1;
      }
      else if (op_r[i].get(j) == 1) {
        j = j - 1;
      }
      else {
        i = i - 1;
      }
    }

    i = n_md;
    j = m_best;
    while (i > 0 && j > 0) {
      if (op_l[i].get(j) == 0) {
        repairedValue[m_best-j] = original[n_md-i];
        repairedFlag[m_best-j] = true;
        i = i - 1;
        j = j - 1;
      }
      else if (op_l[i].get(j) == 1) {
        j = j - 1;
      }
      else {
        i = i - 1;
      }
    }

    if (n % 2 == 1){
      repairedValue[m_best] = original[n_md];
    }

    // interpolation
    for (i = 0; i < repairedValue.length; i++) {
      if (!repairedFlag[i]) {
        int left = i-1;
        while (left >= 0) {
          if (repairedFlag[left]){
            break;
          }
          left --;
        }
        int right = i-1;
        while (right <repairedValue.length) {
          if (repairedFlag[right]){
            break;
          }
          right ++;
        }
        if (left < 0) {
          repairedValue[i] = repairedValue[right];
        }
        else if (right >= repairedValue.length) {
          repairedValue[i] = repairedValue[left];
        }
        else {
          long leftWeight = abs(repairedTime[left] - repairedTime[i]);
          long rightWeight = abs(repairedTime[right] - repairedTime[i]);

          repairedValue[i] = (leftWeight * repairedValue[left] + rightWeight * repairedValue[right])/(leftWeight+rightWeight);
        }
      }
    }
  }

  public void startPointApproximation(long interval){

  }

  public long determineInterval(){
    long[] intervalList = new long[n-1];
    long median;
    for (int i = 1; i < n; i++) {
      intervalList[i-1] = time[i] - time[i-1];
    }
    Arrays.sort(intervalList);
    int middle = ((intervalList.length) / 2);
    if(intervalList.length % 2 == 0){
      long medianA = intervalList[middle];
      long medianB = intervalList[middle-1];
      median = (medianA + medianB) / 2;
    } else{
      median = intervalList[middle + 1];
    }
    return median;
  }

  public long median(long[] valueList){
    int middle = ((valueList.length) / 2);
    long median;
    if(valueList.length % 2 == 0){
      long medianA = valueList[middle];
      long medianB = valueList[middle-1];
      median = (medianA + medianB) / 2;
    } else{
      median = valueList[middle + 1];
    }
    return median;
  }

  public int median(int[] valueList){
    int middle = ((valueList.length) / 2);
    int median;
    if(valueList.length % 2 == 0){
      int medianA = valueList[middle];
      int medianB = valueList[middle-1];
      median = (medianA + medianB) / 2;
    } else{
      median = valueList[middle + 1];
    }
    return median;
  }
}
