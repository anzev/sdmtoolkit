package core;
import java.util.ArrayList;

import util.Logger;

/**
 * Program entry point.
 * 
 * Usage: Usage: java -jar owl2x.jar segs (long|short) <outDir> <mapfile> [<ontology1>.owl <ontology2>.owl ... <ontologyN>.owl] 
 * 
 * @author Anže Vavpetič, April 2011 <anze.vavpetic@ijs.si>
 *
 */

public class Main 
{
	private static void usage()
	{
		Logger.info("Incorrect input arguments.");
		Logger.info("Usage: java -jar owl2x.jar (segs|prolog) (long|short) <outDir> <mapfile> <ontology1>.owl [<ontology2>.owl ... <ontologyN>.owl] ");
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) 
	{
		if (args.length < 5) {
			usage();
			System.exit(1);
		}
		
		// Parse the options.
		String format = args[0];
		boolean shortURI = args[1].equals("short");
		String outDir = args[2];
		String mapfile = args[3];
		
		ArrayList<String> ontologies = new ArrayList<String>();
		
		// Parse the ontology paths.
		for (int i = 4; i < args.length; i++) {
			ontologies.add(args[i]);
		}
		
		if (format.equals("segs")) {
			SegsWriter writer = new SegsWriter(ontologies, mapfile);
			writer.convertOntologies(outDir + "/ont", shortURI);
			writer.convertMapping(outDir + "/g2ont");
		} else if (format.equals("prolog")) {
			PrologWriter writer = new PrologWriter(ontologies, mapfile);
			writer.convertOntologies(outDir + "/b.py", shortURI);
		}
		
		Logger.info("All done.");
	}
}
