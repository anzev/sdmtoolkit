package util;
import java.io.PrintStream;

/**
 * Logger class.
 * 
 * @author Anže Vavpetič, 2010 <anze.vavpetic@ijs.si>
 */

public class Logger 
{
	public static PrintStream out = System.out;
	
	public static boolean debug = false;
	
	/**
	 * Set a non-default stream.
	 * 
	 * @param ps
	 */
	public static void setStream(PrintStream ps) 
	{
		out = ps;
	}
	
	public static void debug(String s)
	{
		if (debug) out.println("OWL2X DEBUG: " + s); 
	}
	
	public static void info(String s)
	{
		out.println("OWL2X INFO: " + s);
	}
	
	public static void warning(String s)
	{
		out.println("OWL2X WARNING: " + s);
	}
	
	public static void error(String s)
	{
		out.println("OWL2X ERROR: " + s);
		System.exit(1);
	}
}
