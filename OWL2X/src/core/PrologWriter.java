package core;

import java.io.*;
import java.net.MalformedURLException;
import java.net.URL;
//import java.security.*;
import java.util.*;

import util.Logger;

import com.hp.hpl.jena.ontology.OntClass;
import com.hp.hpl.jena.ontology.OntDocumentManager;
import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.ontology.OntModelSpec;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.vocabulary.OWL;

public class PrologWriter 
{
	private OntModel model;
	private String mapping;
	
	// Map from ontology URI to prolog predicate
	private HashMap<String, String> termToProlog = new HashMap<String, String>();
	
	String mainPred = "target";
	String mainType = "instance";

	LinkedList<String> table = new LinkedList<String>();
	LinkedList<String> modes = new LinkedList<String>();
	LinkedList<String> determinations = new LinkedList<String>();
	LinkedList<String> isa = new LinkedList<String>();
	LinkedList<String> definitions = new LinkedList<String>();
	LinkedList<String> instances = new LinkedList<String>();
	
	HashSet<String> defSet = new HashSet<String>();
	
	// What can be loaded from the cache
	enum Cache {
		ONT_AND_MAP,
		ONT_ONLY,
		NOTHING
	};
	
	Cache loadStatus = Cache.NOTHING;
	
	// Computed hash-codes
	int ontHash;
	int mapHash;
	
	public PrologWriter(String ontology, String mapping)
	{
		ArrayList<String> tmp = new ArrayList<String>();
		tmp.add(ontology);
		
		init(tmp, mapping);
	}
	
	public PrologWriter(ArrayList<String> ontologies, String mapping)
	{	
		init(ontologies, mapping);
	}

	/**
	 * Inits the conversion procedure.
	 * 
	 * @param ontologies
	 * @param mapping
	 */
	private void init(ArrayList<String> ontologies, String mapping)
	{
		tryLoadFromCache(ontologies, mapping);

		OntDocumentManager mgr = new OntDocumentManager();
		OntModelSpec spec = new OntModelSpec(OntModelSpec.OWL_MEM);
		
		mgr.setCacheModels(true);
		spec.setDocumentManager(mgr);
	
		
		if (loadStatus == Cache.NOTHING) {
			this.model = ModelFactory.createOntologyModel(spec);
			
			for (String ontology : ontologies) {
				if (ontology.trim().startsWith("http://"))
					this.model.read(ontology);
				else 
					this.model.read(new File(ontology).toURI().toString());
			}
			
			this.mapping = mapping;
		}
	}
	
	/**
	 * 
	 * Checks if it can load the files from cache.
	 * 
	 */
	public void tryLoadFromCache(ArrayList<String> ontologies, String mapping)
	{
		StringBuffer onts = new StringBuffer();
		StringBuffer map = new StringBuffer();
		
		try {
			for (String ont : ontologies) {
				if (ont.trim().startsWith("http://"))
				{
					onts.append(readFile(new URL(ont)));
				} else {
					onts.append(readFile(ont.toString()));
				}
			}
			
			map.append(readFile(mapping));
			
		} catch (IOException e) {
			Logger.warning("Cannot read input ontology from cache.");
			
			this.loadStatus = Cache.NOTHING;
			return;
		}
		
		this.ontHash = onts.toString().hashCode();
		this.mapHash = map.toString().hashCode();
		
//		System.out.println(this.ontHash);
//		System.out.println(this.mapHash);
		
		// Try to open the ontology
		try {
			new FileInputStream("." + this.ontHash);
			this.loadStatus = Cache.ONT_ONLY;
		} catch(FileNotFoundException e) {
			this.loadStatus = Cache.NOTHING;
		}
		
		// If the ontology was cached, try also to load the map
		if (this.loadStatus != Cache.NOTHING) {
			try {
				new FileInputStream("." + this.mapHash);
				this.loadStatus = Cache.ONT_AND_MAP;
			} catch(FileNotFoundException e) {}
		}
	}
	
	/**
	 * Converts the given ontologies to prolog.
	 * 
	 * @param outFile
	 * @param shortURI
	 */
	@SuppressWarnings("unchecked")
	public void convertOntologies(String outFile, boolean shortURI) 
	{	
		switch (this.loadStatus) 
		{
		
		//
		// Loads both from cache.
		//
		case ONT_AND_MAP:
		
			Logger.info("Loading ontology and map from cache.");
			
			FileWriter fw = null;
			
			try {
				fw = new FileWriter(outFile);
				
				fw.write(readFile("." + this.ontHash)+"\n");
				fw.write(readFile("." + this.mapHash));

				fw.close();
			} catch (IOException e1) {
				Logger.error("Can't write to: " + outFile);
			}
			
			break;
		
		//
		// Loads only the termToProlog map and convert the mapping.
		//
		case ONT_ONLY:
			
			Logger.info("Loading ontology from cache.");
			
			FileInputStream fis = null;
			ObjectInputStream ois = null;
			
			try {
				fis = new FileInputStream(new File("."+this.ontHash+"_termToProlog"));
				ois = new ObjectInputStream(fis);
				this.termToProlog = (HashMap<String, String>) ois.readObject();
			} catch (Exception e) {
				Logger.error("Cannot read termToProlog map from cache");
				e.printStackTrace();
			}
			
			convertMapping();
			
			fw = null;
			FileWriter cache_map = null;
			
			try {
				fw = new FileWriter(outFile);
				cache_map = new FileWriter("." + this.mapHash);
				
				String mapB = listToPy("instances", instances);
				
				fw.write(readFile("." + this.ontHash));
				fw.write(mapB);
				
				// Cache map
				cache_map.write(mapB);
				
				fw.close();
				cache_map.close();
			} catch (IOException e1) {
				Logger.error("Can't write to: " + outFile);
			}
			
			break;
			
		//
		// Convert all from scratch and save to cache.
		//
		case NOTHING:
			
			Logger.info("Nothing found in cache - converting from scratch.");
			
			// Retrieve the root class
			modes.add(String.format(":- modeh(1, %s(+%s)).", mainPred, mainType));
			
			//OntClass cl = model.getOntResource(OWL.Thing).asClass();
			LinkedList<OntClass> roots = findRoots(model);
			
			for (OntClass cl : roots) 
			{
				String predicate = label(cl);
				table.add(String.format(":- table %s/1.", predicate));
				modes.add(String.format(":- modeb(1, %s(+%s)).", predicate, mainType));
				determinations.add(String.format(":- determination(%s/1, %s/1).", mainPred, predicate));
				termToProlog.put(cl.getURI(), predicate);
				
				print(cl, 0);
			}

			convertMapping();
			
			// Write the background file
			fw = null;
			FileWriter cache_ont = null;
			cache_map = null;
			FileOutputStream cache_termToProlog = null;
			
			try {
				fw = new FileWriter(outFile);
				cache_ont = new FileWriter("." + this.ontHash);
				cache_map = new FileWriter("." + this.mapHash);
				cache_termToProlog = new FileOutputStream(new File("."+this.ontHash+"_termToProlog"));
				
				StringBuffer ontB = new StringBuffer();
				ontB.append(listToPy("table", table));
				ontB.append(listToPy("modes", modes));
				ontB.append(listToPy("determinations", determinations));
				ontB.append(listToPy("isa", isa));
				ontB.append(listToPy("definitions", definitions));
				
				StringBuffer mapB = new StringBuffer(listToPy("instances", instances));
				
				fw.write(ontB.toString());
				fw.write(mapB.toString());
				
				// Write to cache
				cache_ont.write(ontB.toString());
				cache_map.write(mapB.toString());
				ObjectOutputStream oos = new ObjectOutputStream(cache_termToProlog);
				oos.writeObject(this.termToProlog);
				oos.close();
				
				fw.close();
				cache_ont.close();
				cache_map.close();
			} catch (IOException e1) {
				Logger.error("Can't write to: " + outFile);
			}
			
			break;
		}
	}
	
	private String readFile(URL url) throws IOException
	{
		return new Scanner(url.openStream()).useDelimiter("\\Z").next();
	}
	
	/**
	 * Reads the whole file at once.
	 * 
	 * @param fn
	 * @return
	 * @throws FileNotFoundException
	 */
	private String readFile(String fn) throws FileNotFoundException
	{
		return new Scanner(new File(fn)).useDelimiter("\\Z").next();
	}
	
	/**
	 * Collects all the 'roots' of the ontology. 
	 * 
	 * @param model
	 * @return
	 */
	private LinkedList<OntClass> findRoots(OntModel model)
	{
		OntClass cl = model.getOntResource(OWL.Thing).asClass();
		LinkedList<OntClass> roots = new LinkedList<OntClass>();
		
		if (numOfSubClasses(cl) == 0)  // No common root
		{
			Iterator<OntClass> it = model.listHierarchyRootClasses();
			while (it.hasNext())
			{
				cl = it.next();
				String label = label(cl);
				if (!label.equalsIgnoreCase("'null'")) {
					roots.add(cl);
				}
			}
		} else { // Common root 'Thing'
			roots.add(cl);
		}
		
		return roots;
	}
	
	/**
	 * Returns the number of subclasses of cl.
	 * 
	 * @param cl
	 * @return
	 */
	private int numOfSubClasses(OntClass cl)
	{
		return cl.listSubClasses(true).toSet().size();
	}
	
	
	/**
	 * Converts list l to python list as string.
	 * 
	 * @param var Variable name
	 * @param l
	 * @return
	 */
	private String listToPy(String var, List<String> l) 
	{
		StringBuffer pyList = new StringBuffer(String.format("%s = [", var));
		for (int i = 0; i < l.size()-1; i++) {
			pyList.append(String.format("\"%s\", ", l.get(i)));
		}
		pyList.append(String.format("\"%s\"", l.get(l.size()-1)));
		pyList.append("]\n");
		
		return pyList.toString();
	}

	/**
	 * Prints the hierarchy bellow class base.
	 * 
	 * @param base
	 * @param d
	 */
	private void print(OntClass base, int d)
	{	
		Iterator<OntClass> it = base.listSubClasses(true);
		
		while (it.hasNext()) {
			OntClass cl = it.next();

			String predicate = label(cl);
			String parentPred = termToProlog.get(base.getURI());
			
			if (termToProlog.get(cl.getURI()) == null) {
				table.add(String.format(":- table %s/1.", predicate));
				modes.add(String.format(":- modeb(1, %s(+%s)).", predicate, mainType));
				determinations.add(String.format(":- determination(%s/1, %s/1).", mainPred, predicate));
			}
			
			if (!defSet.contains(predicate+","+parentPred)) {
				isa.add(String.format("isa(%s, %s).", predicate, parentPred));
				definitions.add(String.format("%s(A) :- %s(A).", parentPred, predicate));
				
				defSet.add(predicate+","+parentPred);
			}
			
			termToProlog.put(cl.getURI(), predicate);
			
			// Recursively print the subclasses of this class
			print(cl, d+1);
		}
	}
	
	/**
	 * Returns the human-readable name of cl.
	 * 
	 * @param cl
	 * @return
	 */
	private String label(OntClass cl)
	{
		String label = cl.getLabel(null);
		
		if (label == null) {
			label = cl.getLocalName();
		}
		
		if (label != null) {
			
			// We enclose the predicate names in Prolog with apostrophes, so remove all existing ones
			label = label.replaceAll("['\"]", "");
		}
		
		return "'" + label + "'";
	}
	
	/**
	 * Converts the mapping file to prolog.
	 */
	public void convertMapping()
	{
		// File with a python dictionary, which maps URIs to predicate names
		String outFile = "uriToPredicate.py";
		FileWriter fw = null;
		try {
			fw = new FileWriter(outFile);
			fw.write("uriToPredicate = dict()\n");
		} catch (IOException e1) {
			Logger.error("Can't write to: " + outFile);
		}
		
		Scanner s = null;
		try {
			s = new Scanner(new File(this.mapping));
		} catch (FileNotFoundException e) {
			Logger.error("Mapping file not found: " + this.mapping);
		}
		
		for (String uri : termToProlog.keySet()) {
			Logger.debug(String.format("%s --> %s\n", uri, termToProlog.get(uri)));
			//System.out.printf("%s --> %s\n", uri, termToProlog.get(uri));
			try {
				fw.write(String.format("uriToPredicate['%s'] = \"%s\"\n", uri, termToProlog.get(uri)));
			} catch (IOException e) {
				Logger.error("Can't write to: " + outFile + "\n Message: "+ e.getMessage());
			}
		}
		try {
			fw.close();
		} catch (IOException e) {
			Logger.error("Can't close stream.");
		}
		
		while (s.hasNextLine())
		{
			String line = s.nextLine();
			String[] tokens = line.trim().split("\\s+");  // The tokens are separated with whitespace
			String id = tokens[0];
			//String instance = "";
			
			//instance += String.format("%s(i%s).\n", mainType, id);
			this.instances.add(String.format("%s(i%s).", mainType, id));

			for (int i = 1; i < tokens.length; i++) 
			{
				String uri = tokens[i];
				String predicate = "";
				if (termToProlog.containsKey(uri)) {
					predicate = termToProlog.get(uri);
				} else {
					Logger.warning("URI not found in the given ontologies: " + uri);
					continue;
				}
				
				//instance += String.format("%s(i%s).\n", predicate, id);
				this.instances.add(String.format("%s(i%s).", predicate, id));
			}
			
			//this.instances.add(instance);
		}
	}
	
	public static void main(String[] args) 
	{
		ArrayList<String> ontologies = new ArrayList<String>();
//		ontologies.add("/home/anzev/programiranje/diploma/banking_services.owl");
//		ontologies.add("/home/anzev/programiranje/diploma/geography.owl");
//		ontologies.add("/home/anzev/programiranje/diploma/occupation.owl");
		ontologies.add("");
		String mapping = "/home/anzev/programiranje/diploma/map_bank.txt";
		PrologWriter writer = new PrologWriter(ontologies, mapping);
		writer.convertOntologies("ont.b", true);
		
		
	}
}
