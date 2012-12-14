package core;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Scanner;

// OWL2X imports
import util.Logger;

// Jena imports
import com.hp.hpl.jena.ontology.*;
import com.hp.hpl.jena.rdf.model.ModelFactory;

/**
 * Converts ontologies and examples to an input suitable for segs.
 * 
 * @author Anže Vavpetič, 2010 <anze.vavpetic@ijs.si>
 *
 */
public class SegsWriter //extends BaseWriter 
{
	// The ontology model representation
	private OntModel model;
	
	// Mapping file path
	private String mapping;
	
	private final static String[] SEGS_ONTOLOGIES 
		= new String[] {"molecular_function", "cellular_component", "biological_process", "KEGG_pathway"}; 
	
	private int GO_CODE_LEN = 7;
	private int KEGG_CODE_LEN = 5;
	
	// Counter of GO terms
	private int go = 0;
	
	// Counter of KEGG terms
	private int kegg = 0;
	
	// A map from ontology class to segs term id
	//private HashMap<OntClass, String> termToSegs = new HashMap<OntClass, String>();
	private HashMap<String, String> termToSegs = new HashMap<String, String>();
	
	// Print short URIs?
	private boolean shortURI = true;
	
	public SegsWriter(String ontology, String mapping)
	{
		ArrayList<String> tmp = new ArrayList<String>();
		tmp.add(ontology);
		
		init(tmp, mapping);
	}
	
	public SegsWriter(ArrayList<String> ontologies, String mapping)
	{		
		init(ontologies, mapping);
	}
	
	private void init(ArrayList<String> ontologies, String mapping)
	{
		OntDocumentManager mgr = new OntDocumentManager();
		OntModelSpec spec = new OntModelSpec(OntModelSpec.OWL_MEM);
		
		mgr.setCacheModels(true);
		spec.setDocumentManager(mgr);
		
		this.model = ModelFactory.createOntologyModel(spec);
		
		for (String ontology : ontologies) {
			if (ontology.trim().startsWith("http://")) {
				this.model.read(ontology);
			} else {
				System.out.println(ontology);
				this.model.read(new File(ontology).toURI().toString());
			}
		}
		
		// Check if the number of ontologies specified can be handled by SEGS
		if (ontologies.size() > SEGS_ONTOLOGIES.length) {
			Logger.error("The maximum number of supported ontologies by SEGS is: " + SEGS_ONTOLOGIES.length);
		}
		
		this.mapping = mapping;
	}

	public void convertOntologies(String outFile, boolean shortURI) 
	{
		Logger.info("Starting ontology conversion to SEGS...");
		PrintStream out = null;
		try {
			out = new PrintStream(outFile);
		} catch (FileNotFoundException e) {
			Logger.error("Couldn't create ontology file.");
		}
		
		this.shortURI = shortURI;
		
		// First iterate through root classes
		Iterator<OntClass> it = model.listHierarchyRootClasses();
		int br = 0;
		
		while (it.hasNext()) {
			OntClass cl = it.next();
			String branch = SEGS_ONTOLOGIES[br++];
			
			// Skip anonymous classes
			if (!cl.isAnon() && cl.getLocalName() != null) {
				
				// Generate the root definition
				String line = term(null, cl, branch);
				out.println(line);
				
				// Print the subclasses
				this.writeSubClasses(out, cl, branch);
				
			}
		}
		
		// Even if we don't need the KEGG ontology,
		// there must be an empty node for it.
		if (br < SEGS_ONTOLOGIES.length) {
			out.println("['KEGG:00000', ['KEGG_pathway', 'pathway', [], []]]");
		}
		
		out.close();
		Logger.info("Done.");
	}
	
	private void writeSubClasses(PrintStream out, OntClass base, String branch)
	{
		Iterator<OntClass> it = base.listSubClasses();
		
		while (it.hasNext()) {
			OntClass cl = it.next();
			if (!cl.isAnon() && cl.getLocalName() != null) {
				
				// Generate the class definition
				String line = term(base, cl, branch);
				out.println(line);
				
				// Recursively print the subclasses
				this.writeSubClasses(out, cl, branch);
			}
		}
	}
	
	private String term(OntClass parent, OntClass child, String branch)
	{
		String parentCode = "";
		String childCode = "";
		String childLabel = formatClass(child);
		
		// Retrieve parent code
		if (parent != null) {
			parentCode = termToSegs.get(parent.getURI());
		}
		
		// Generate child code
		if (branch != "KEGG_pathway") {
			// Handle the three GO ontology branches
			String code = new Integer(++go).toString();
			int codeLen = code.length();
			
			// Append the necessary number of zeroes to get the proper code length.
			for (int i = 0; i < GO_CODE_LEN - codeLen; i++) {
				code = "0" + code;
			}
			
			childCode = "GO:" + code;
		} else {
			// Handle the KEGG ontology
			String code = new Integer(++kegg).toString();
			int codeLen = code.length();
			
			// Append the necessary number of zeroes to get the proper code length.
			for (int i = 0; i < KEGG_CODE_LEN - codeLen; i++) {
				code = "0" + code;
			}
			
			childCode = "KEGG:" + code;
		}
		
		// Associate the given class object with the generated code
		termToSegs.put(child.getURI(), childCode);
		
		String parentList = parent == null || parentCode == null ? "[]" : "[\'" + parentCode + "\']"; 
		return "[\'" + childCode + "\'," + "[\'" + branch + "\', \'" + childLabel + "\', " + parentList + ", []]]";
	}
	
	/**
	 * Formats the class name of the given class object.
	 * 
	 * @param cl
	 * @return String representation of the class.
	 */
	private String formatClass(OntClass cl) 
	{
		if (!this.shortURI) {
			return cl.getURI();
		}
		
		return cl.getLocalName();	
	}
	
	public void convertMapping(String outFile)
	{
		FileWriter fw = null;
		try {
			fw = new FileWriter(outFile);
		} catch (IOException e1) {
			Logger.error("Can't write to: " + outFile);
		}
		
		Scanner s = null;
		try {
			s = new Scanner(new File(this.mapping));
		} catch (FileNotFoundException e) {
			Logger.error("Mapping file not found: " + this.mapping);
		}
		
		// Debug:
		for (String uri : termToSegs.keySet()) {
			System.out.printf("%s --> %s\n", uri, termToSegs.get(uri));
		}
		
		while (s.hasNextLine())
		{
			String line = s.nextLine();
			
			//System.out.println(line);
			
			String[] tokens = line.trim().split("\\s+");  // The tokens are separated with whitespace
			
			String id = tokens[0];
			String termIDList = "";
			
			for (int i = 1; i < tokens.length; i++) 
			{
				String uri = tokens[i];
				String goCode = "";
				if (termToSegs.containsKey(uri)) {
					goCode = termToSegs.get(uri);
				} else {
					Logger.warning("URI not found in the given ontologies: " + uri);
					continue;
				}
				termIDList += "\"" + goCode + "\"" + (i == tokens.length-1 ? "" : ", ");
			}
			
			try {
				//System.out.println(termIDList);
				fw.write(String.format("[%s, [%s]]\n", id, termIDList));
			} catch (IOException e) {
				Logger.error("Problem writing to out file: " + outFile);
			}
		}
		
		try {
			fw.close();
		} catch (IOException e) {
			Logger.error("Problem closing: " + outFile);
		}
	}
}
