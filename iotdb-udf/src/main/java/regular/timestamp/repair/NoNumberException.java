package regular.timestamp.repair;

public class NoNumberException extends Exception {

  @Override
  public String toString() {
    String s = "The value of the input time series is not numeric.\n";
    return s + super.toString(); //To change body of generated methods, choose Tools | Templates.
  }
}