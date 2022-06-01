package regular.timestamp.repair;

import org.apache.iotdb.db.query.udf.api.access.Row;

import java.util.ArrayList;

public class Utils {
  public static long[] toLongArray(ArrayList<Long> list) {
    int len = list.size();
    long ans[] = new long[len];
    for (int i = 0; i < len; i++) {
      ans[i] = list.get(i);
    }
    return ans;
  }

  public static double[] toDoubleArray(ArrayList<Double> list) {
    int len = list.size();
    double ans[] = new double[len];
    for (int i = 0; i < len; i++) {
      ans[i] = list.get(i);
    }
    return ans;
  }

  public static double getValueAsDouble(Row row, int index) throws NoNumberException{
    double ans = 0;
    switch (row.getDataType(index)) {
      case INT32:
        ans = row.getInt(index);
        break;
      case INT64:
        ans = row.getLong(index);
        break;
      case FLOAT:
        ans = row.getFloat(index);
        break;
      case DOUBLE:
        ans = row.getDouble(index);
        break;
      default:
        throw new NoNumberException();
    }
    return ans;
  }

  public static double getValueAsDouble(Row row) throws NoNumberException {
    return getValueAsDouble(row, 0);
  }
}
