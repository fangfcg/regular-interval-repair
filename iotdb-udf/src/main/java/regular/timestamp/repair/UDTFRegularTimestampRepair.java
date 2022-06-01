package regular.timestamp.repair;

import java.io.IOException;
import java.util.ArrayList;

import org.apache.iotdb.db.query.udf.api.UDTF;
import org.apache.iotdb.db.query.udf.api.access.Row;
import org.apache.iotdb.db.query.udf.api.access.RowIterator;
import org.apache.iotdb.db.query.udf.api.access.RowWindow;
import org.apache.iotdb.db.query.udf.api.collector.PointCollector;
import org.apache.iotdb.db.query.udf.api.customizer.config.UDTFConfigurations;
import org.apache.iotdb.db.query.udf.api.customizer.parameter.UDFParameters;
import org.apache.iotdb.db.query.udf.api.customizer.strategy.RowByRowAccessStrategy;
import org.apache.iotdb.db.query.udf.api.customizer.strategy.SlidingSizeWindowAccessStrategy;
import org.apache.iotdb.tsfile.file.metadata.enums.TSDataType;
import sun.reflect.annotation.ExceptionProxy;
import regular.timestamp.repair.RegularTimestampRepair;

public class UDTFRegularTimestampRepair implements UDTF {

  protected int n;
  protected long time[];
  protected long time_repaired[];
  protected double original[];
  protected double repaired[];
  private int lmd_a;
  private int lmd_d;
  private int interval_gran; // granularity of interval, default 1
  private int st_gran; // granularity of start point, default 1

  @Override
  public void beforeStart(UDFParameters parameters, UDTFConfigurations configurations) throws Exception{
    configurations
        .setOutputDataType(parameters.getDataType(0))
        .setAccessStrategy(new SlidingSizeWindowAccessStrategy(Integer.MAX_VALUE));
    lmd_a = parameters.getIntOrDefault("lmd_a", 1000);
    lmd_d = parameters.getIntOrDefault("lmd_d", 1000);
    interval_gran = parameters.getIntOrDefault("interval_gran", 1);
    st_gran = parameters.getIntOrDefault("st_gran", 1);
  }

  @Override
  public void transform(RowWindow rowWindow, PointCollector collector) throws Exception{
    RegularTimestampRepair ts = new RegularTimestampRepair(rowWindow.getRowIterator(), lmd_a, lmd_d, interval_gran, st_gran);
    ts.repair();
    switch (rowWindow.getDataType(0)) {
      case DOUBLE:
        for (int i = 0; i < ts.repairedTime.length; i++) {
          collector.putDouble(ts.repairedTime[i], ts.repairedValue[i]);
        }
        break;
      case FLOAT:
        for (int i = 0; i < ts.repairedTime.length; i++) {
          collector.putFloat(ts.repairedTime[i], (float) ts.repairedValue[i]);
        }
        break;
      case INT32:
        for (int i = 0; i < ts.repairedTime.length; i++) {
          collector.putInt(ts.repairedTime[i], (int) ts.repairedValue[i]);
        }
        break;
      case INT64:
        for (int i = 0; i < ts.repairedTime.length; i++) {
          collector.putLong(ts.repairedTime[i], (long) ts.repairedValue[i]);
        }
        break;
      default:
        throw new Exception();
    }
  }

  public static void main(String[] args) {
    // empty main function for outputing artifact
  }
}
