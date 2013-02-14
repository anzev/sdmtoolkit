#include <stdio.h>
#include <python2.7/Python.h>

#include "def_var.h"


extern void parse_config(char *);
extern void init_app();
extern void parse_ONT();
extern void parse_ONT1(PyObject*);
extern void parse_gene_annotations();
extern void parse_gene_annotations1(PyObject*, PyObject*);
extern void parse_input_file1(PyObject*, PyObject*);
extern void parse_input_file();
extern void input_report();
extern void Calc_Child_Nodes_and_Roots();
extern void Calc_General_Terms(PyObject*);
extern void Fill_ONT_terms();
extern void Remove_Small_Terms_and_DAG();
extern void Analysis();
extern void done_app();

extern void write_progress();


static PyObject* runSEGS(PyObject *self, PyObject *args, PyObject *keywds)
{
	PyObject * result = PyDict_New();
	PyObject * inputData, * geneIDs, * geneRanks, * generalTerms, * ontology, * gene2gene, * gene2ont;

	//char * dbdir, * projname, *basename;
	char *basename;


	static char *kwlist[] = {"progressFname",
			"inputData", "generalTerms", "ontology", "g2g", "g2ont",
			"useMolFunctions", "useBioProcesses", "useCellComponents", "useKEGG", "useGeneInteractions",
			"summarize", "cutoff", "minSizeGS",
			"maxNumTerms", "GSEAfactor", "numIters", "PrintTopGS",
			"p_value", "weightFisher", "weightGSEA", "weightPAGE", "randomSeed", "wracc_k", "level_ont1", "level_ont2", "level_ont3", "level_ont4", NULL};
    
	 if (!PyArg_ParseTupleAndKeywords(args, keywds, "sO!O!O!O!O!iiiiiiiiiiiiddddiiiiii", kwlist,
			 &basename,
			 &PyList_Type, &inputData,
			 &PyList_Type, &generalTerms,
			 &PyList_Type, &ontology,
			 &PyList_Type, &gene2gene,
			 &PyList_Type, &gene2ont,
			 &include_ont[0], &include_ont[1], &include_ont[2], &include_ont[3], &MaxInterTerms,
			 &Summarization, &Cutoff, &Min_Size_GS,
			 &MaxNumTerms, &GSEA_Factor, &NumberIterations, &PrintTopGS,
			 &P_Value, &W_fisher, &W_gsea, &W_page, &randomSeed, &wracc_k,
             &general_level[0], &general_level[1], &general_level[2], &general_level[3])) {
		 return NULL;
    }
/*
		if (!PyArg_ParseTuple(args, "sssO!O!O!O!O!iiiiiiiiiiiiddddi", &basename, &dbdir, &projname,
				&PyList_Type, &inputData,
				&PyList_Type, &generalTerms,
				&PyList_Type, &ontology,
				&PyList_Type, &gene2gene,
				&PyList_Type, &gene2ont,
				&include_ont[0], &include_ont[1], &include_ont[2], &include_ont[3],
				&MaxInterTerms, &Summarization, &Cutoff, &Min_Size_GS,
				&MaxNumTerms, &GSEA_Factor, &NumberIterations, &PrintTopGS,
				&P_Value, &W_fisher, &W_gsea, &W_page, &randomSeed))
*/
	else
	{	
		// do a basic check of input from Python
		//Py_INCREF(inputData);

		if (PyList_GET_SIZE(inputData)!=(Py_ssize_t)2) {
			PyErr_SetString(PyExc_IndexError, "input data parameter must contains two lists (geneIDs and ranks)");
			return NULL;
		}
		geneIDs = PyList_GetItem(inputData, (Py_ssize_t)0);
		geneRanks = PyList_GetItem(inputData, (Py_ssize_t)1);

		if (PyList_GET_SIZE(geneIDs)!=PyList_GET_SIZE(geneRanks)) {
			PyErr_SetString(PyExc_IndexError, "both input data lists must be of the same size (geneIDs and ranks)");
			return NULL;
		}

		// hold on these objects
		// NO NEED since all references to arguments are borrowed
		/*
		Py_INCREF(geneIDs);
		Py_INCREF(geneRanks);
		Py_INCREF(generalTerms);
		Py_INCREF(ontology);
		Py_INCREF(gene2gene);
		Py_INCREF(gene2ont);
		 */
    	
		strcpy(BaseName, basename);

		fprintf(stdout, "basename: %s\n", BaseName);
		fprintf(stdout, "ont[0]: %d\n", include_ont[0]);
		fprintf(stdout, "ont[1]: %d\n", include_ont[1]);
		fprintf(stdout, "ont[2]: %d\n", include_ont[2]);
		fprintf(stdout, "ont[3]: %d\n", include_ont[3]);
		fprintf(stdout, "MaxInterTerms: %d\n", MaxInterTerms);
		fprintf(stdout, "Summarization: %d\n", Summarization);
		fprintf(stdout, "Cutoff: %d\n", Cutoff);
		fprintf(stdout, "Min_Size_GS: %d\n", Min_Size_GS);
		fprintf(stdout, "MaxNumTerms: %d\n", MaxNumTerms);
		fprintf(stdout, "GSEA_Factor: %d\n", GSEA_Factor);
		fprintf(stdout, "NumberIterations: %d\n", NumberIterations);
		fprintf(stdout, "P_Value: %f\n", P_Value);
		fprintf(stdout, "W_fisher: %f\n", W_fisher);
		fprintf(stdout, "W_gsea: %f\n", W_gsea);
		fprintf(stdout, "W_page: %f\n", W_page);
		fprintf(stdout, "randomSeed: %d\n", randomSeed);
		fprintf(stdout, "wracc_k: %d\n", wracc_k);
        fprintf(stdout, "level1: %d\n", general_level[0]);
        fprintf(stdout, "level2: %d\n", general_level[1]);
        fprintf(stdout, "level3: %d\n", general_level[2]);
        fprintf(stdout, "level4: %d\n", general_level[3]);

		// If we do not need repeatability, initialize generator with time.
		// Otherwise, alway use the same seed
		if (randomSeed == -1)
		{
			//randomSeed = time(&start_time);
			randomSeed = time(NULL);
			srand(randomSeed);
			printf("\n-- Random generator initialized with current time: %d\n", randomSeed);
		}
		else
		{
			srand(randomSeed);
			printf("\n-- Random generator initialized with pre-defined seed: %d\n", randomSeed);
		}


		//parse_config(fname);

		init_app();
		//parse_ONT();
		parse_ONT1(ontology);
		//parse_gene_annotations();
		parse_gene_annotations1(gene2gene, gene2ont);

		//parse_input_file();
		parse_input_file1(geneIDs, geneRanks);

		if (WRITE_FILES) {
			input_report();
		}

		/*****************************************/

		Calc_Child_Nodes_and_Roots();
		Calc_General_Terms(generalTerms);
		Fill_ONT_terms();
		Remove_Small_Terms_and_DAG();

		/*****************************************/

		Analysis(result);

		done_app();


		// release hold
		/*
		Py_DECREF(inputData);
		Py_DECREF(geneIDs);
		Py_DECREF(geneRanks);
		Py_DECREF(generalTerms);
		Py_DECREF(ontology);
		Py_DECREF(gene2gene);
		Py_DECREF(gene2ont);
		*/

		return result;
	}
}

// doc strings
static char segs_doc[] =
		"segs is a wrapper around the SEGS method, implemented in C";
static char runSEGS_doc[] = "runSEGS(...) runs the SEGS method on given data";


/*   The method table must always be present - it lists the
 functions that should be callable from Python */
static PyMethodDef segs_methods[] =
{
//structure:
		// name of function when called from Python
		// corresponding C function
		// METH_VARARGS / METH_NOARGS / METH_O / METH_KEYWORDS  (type of arguments)
		// docstring

		{ "runSEGS", (PyCFunction)runSEGS, METH_KEYWORDS, runSEGS_doc },
		{ NULL, NULL } // required ending of the method table
};

#if GSEGS
PyMODINIT_FUNC initsegs()
#else
PyMODINIT_FUNC initsegs_legacy()
#endif
{
	/* Assign the name of the module and the name of the
	 method table and (optionally) a module doc string: */
#if GSEGS
	Py_InitModule3("segs", segs_methods, segs_doc);
#else
	Py_InitModule3("segs_legacy", segs_methods, segs_doc);
#endif
}


