#include <stdio.h>
#include <stdlib.h>

#include <python2.7/Python.h>
#include "def_var.h"

extern IntArray IntArrayNew();
extern void SetAdd(IntArray, int);
extern IntArray SetUnion(IntArray, IntArray);
extern void IntArrayFree(IntArray);
extern int FindInt(IntArray, int);
extern void AddInt(IntArray, int);

FILE* open_file(char *fname)
{
	FILE *dat = fopen(fname, "r");
	if (dat == NULL)
	{
		printf("I can't open file: %s\n", fname);
		exit(1);
	}
	return dat;
}

void parse_config(char *config)
{
	FILE *dat;
	dat = open_file(config);
	fscanf(dat, "BaseName=%s\n", BaseName);
	fscanf(dat, "DB_dir=%s\n", DB_dir);
	fscanf(dat, "Project=%s\n", project_name);
	fscanf(dat, "Func=%d\n", &include_ont[0]);
	fscanf(dat, "Proc=%d\n", &include_ont[1]);
	fscanf(dat, "Comp=%d\n", &include_ont[2]);
	fscanf(dat, "KEGG=%d\n", &include_ont[3]);
	fscanf(dat, "MaxInterTerms=%d\n", &MaxInterTerms);
	fscanf(dat, "Summarization=%d\n", &Summarization);
	fscanf(dat, "Cutoff=%d\n", &Cutoff);
	fscanf(dat, "Min_Size_GS=%d\n", &Min_Size_GS);
	fscanf(dat, "MaxNumTerms=%d\n", &MaxNumTerms);
	fscanf(dat, "GSEA_Factor=%d\n", &GSEA_Factor);
	fscanf(dat, "NumberIterations=%d\n", &NumberIterations);
	fscanf(dat, "PrintTopGS=%d\n", &PrintTopGS);
	fscanf(dat, "P_Value=%lf\n", &P_Value);
	fscanf(dat, "W_fisher=%lf\n", &W_fisher);
	fscanf(dat, "W_gsea=%lf\n", &W_gsea);
	fscanf(dat, "W_page=%lf\n", &W_page);
	fscanf(dat, "RandSeed=%d\n", &randomSeed);
	fclose(dat);
}

void newTerm(struct TOnt *term, char type, char *name)
{
	term->type = type;
	term->general = 0;
	term->name = strdup(name);
	term->parent = IntArrayNew();
	term->child = IntArrayNew();
	term->gene = IntArrayNew();
	term->i_gene = IntArrayNew();
	term->more_general = NULL;
}



/*
 * This function was added by V.P.
 * It reads the input from a Python list instead from a text file.
 * WARNING: this function (and the original) assumes that all KEGG ontology is strictly
 *          AFTER GO ontology. Otherwise, KEGG integers will be overwritten by GO integers...
 *          (Sorry, nothing can be done about that, its the original author's fault)
 */
void parse_ONT1(PyObject *ontology)
{
	printf("Parsing ont ...");
  
	PyObject *iterator = PyObject_GetIter(ontology);
	PyObject *item, *ISA, *PARTOF;
	int ID, SUBID, i, prefixOffset, termOffset;
	char * branch, * name, * IDstring;

	while ((item = PyIter_Next(iterator))) {
		IDstring = PyString_AsString(PyList_GET_ITEM(item, (Py_ssize_t)0));
		branch = PyString_AsString(PyList_GetItem(PyList_GetItem(item, (Py_ssize_t)1), (Py_ssize_t)0));
		name = PyString_AsString(PyList_GetItem(PyList_GetItem(item, (Py_ssize_t)1), (Py_ssize_t)1));

		// make integer term id
		if (IDstring[0]=='G') {
			prefixOffset = GO_PREFIX_OFFSET;
			ID = atoi(IDstring + prefixOffset);
			lastGO = ID;
			termOffset = 0;
		}
		else {
			prefixOffset = KEGG_PREFIX_OFFSET;
			termOffset = lastGO + 1;
			ID = atoi(IDstring + prefixOffset) + termOffset;
		}

		// save term number and its name
		newTerm(&Ont[ID], ' ', name);
		//fprintf(stderr, "%d, %s\n", ID, name);

		ISA = PyList_GET_ITEM(PyList_GET_ITEM(item, (Py_ssize_t)1), (Py_ssize_t)2);
		PARTOF = PyList_GET_ITEM(PyList_GET_ITEM(item, (Py_ssize_t)1), (Py_ssize_t)3);

		// add all ISA terms
		for (i = 0; i < PyList_GET_SIZE(ISA); i++) {
			SUBID = atoi(PyString_AsString(PyList_GET_ITEM(ISA, (Py_ssize_t)i)) + prefixOffset) + termOffset;
			SetAdd(Ont[ID].parent, SUBID);
			//fprintf(stderr, "--> %d\n", SUBID);
		}
		// and all PARTOF terms
		for (i = 0; i < PyList_GET_SIZE(PARTOF); i++) {
			SUBID = atoi(PyString_AsString(PyList_GET_ITEM(PARTOF, (Py_ssize_t)i)) + prefixOffset) + termOffset;
			SetAdd(Ont[ID].parent, SUBID);
			//fprintf(stderr, "--> %d\n", SUBID);
		}

		// save ontolgy branch type
		if (branch[0] == 'm')
			Ont[ID].type = 'F';
		if (branch[0] == 'b')
			Ont[ID].type = 'P';
		if (branch[0] == 'c')
			Ont[ID].type = 'C';
		if (branch[0] == 'K')
			Ont[ID].type = 'K';

		Py_DECREF(item);
	}
	Py_DECREF(iterator);
	
	printf("Done!\n");
}



void parse_ONT()
{
	char str[10000], part[1000][1000];
	int i, len, plen, num_parts, offset, gokegg, ont_id;

	printf("Parsing g2ONT file ... ");

	FILE *dat;
	strcpy(str, DB_dir);
	strcat(str, "ont");
	dat = open_file(str);
	while (fgets(str, 10000, dat))
	{
		len = strlen(str);
		i = num_parts = 0;
		while (i < len)
		{
			if (str[i] == '\'')
			{
				i++;
				plen = 0;
				while (str[i] != '\'')
					part[num_parts][plen++] = str[i++];
				part[num_parts++][plen] = 0;
			}
			i++;
		}

		if (part[0][0] == 'G')
		{
			gokegg = 3;
			ont_id = atoi(part[0] + gokegg);
			lastGO = ont_id;
			offset = 0;
		}
		else
		{
			gokegg = 5;
			offset = lastGO + 1;
			ont_id = atoi(part[0] + gokegg) + offset;
		}

		newTerm(&Ont[ont_id], ' ', part[2]);
		//fprintf(stderr, "%d, %s\n", ont_id, part[2]);


		for (i = 3; i < num_parts; i++) {
			SetAdd(Ont[ont_id].parent, atoi(part[i] + gokegg) + offset);
			//fprintf(stderr, "--> %d\n", atoi(part[i] + gokegg) + offset);
		}

		if (part[1][0] == 'm')
			Ont[ont_id].type = 'F';
		if (part[1][0] == 'b')
			Ont[ont_id].type = 'P';
		if (part[1][0] == 'c')
			Ont[ont_id].type = 'C';
		if (part[1][0] == 'K')
			Ont[ont_id].type = 'K';
	}
	fclose(dat);

	printf("Done !\n");
}

int is_digit(char c)
{
	if ((c >= '0') && (c <= '9'))
		return 1;
	return 0;
}
int is_letter(char c)
{
	if ((c >= 'a') && (c <= 'z'))
		return 1;
	if ((c >= 'A') && (c <= 'Z'))
		return 1;
	return 0;
}



/*
 * This function was added by V.P.
 * It reads the input from Python lists instead from text files.
*/
void parse_gene_annotations1(PyObject * gene2gene, PyObject * gene2ont)
{
	PyObject * tmp, * current;
	int i, j, geneID, termOffset, prefixOffset, gene;
	char * term;
	IntArray set1 = IntArrayNew(), set2 = IntArrayNew();


	// read genes from g2ont list
	for(i=0; i<PyList_GET_SIZE(gene2ont); i++) {
		current = PyList_GET_ITEM(gene2ont, (Py_ssize_t)i);
		geneID = (int) PyInt_AS_LONG(PyList_GET_ITEM(current, (Py_ssize_t)0));
		SetAdd(set1, geneID);
		//fprintf(stderr, "%d. ", geneID);
	}

	// read genes from g2g list
	for(i=0; i<PyList_GET_SIZE(gene2gene); i++) {
		current = PyList_GET_ITEM(gene2gene, (Py_ssize_t)i);
		geneID = (int) PyInt_AS_LONG(PyList_GET_ITEM(current, (Py_ssize_t)0));
		SetAdd(set2, geneID);
		//fprintf(stderr, "%d: ", geneID);

		tmp = PyList_GET_ITEM(current, (Py_ssize_t)1);
		for(j=0; j<PyList_GET_SIZE(tmp); j++) {
			geneID = (int) PyInt_AS_LONG(PyList_GET_ITEM(tmp, (Py_ssize_t)j));
			SetAdd(set2, geneID);
			//fprintf(stderr, "%d ", geneID);
		}
		//fprintf(stderr, "\n");
	}

	//--- this part of code is the same
	gIds = SetUnion(set1, set2);
	IntArrayFree(set1);
	IntArrayFree(set2);

	g2g = (IntArray *) malloc(gIds->len * sizeof(IntArray));
	g2ont = (IntArray *) malloc(gIds->len * sizeof(IntArray));
	for (i=0; i<gIds->len; i++) {
		g2g[i] = IntArrayNew();
		g2ont[i] = IntArrayNew();
	}
	//----------------------------


	// read terms for genes from g2ont
	for(i=0; i<PyList_GET_SIZE(gene2ont); i++) {
		current = PyList_GET_ITEM(gene2ont, (Py_ssize_t)i);
		geneID = FindInt(gIds, (int) PyInt_AsLong(PyList_GET_ITEM(current, (Py_ssize_t)0)));

		// this is list of terms
		tmp = PyList_GET_ITEM(current, (Py_ssize_t)1);
		for(j=0; j<PyList_GET_SIZE(tmp); j++) {
			term = PyString_AsString(PyList_GET_ITEM(tmp, (Py_ssize_t)j));
			if (term[0] == 'G') {
				termOffset = 0;
				prefixOffset = GO_PREFIX_OFFSET;
			}
			else {
				termOffset = lastGO + 1;
				prefixOffset = KEGG_PREFIX_OFFSET;
			}
			SetAdd(g2ont[geneID], atoi(term+prefixOffset) + termOffset);
			//fprintf(stderr, "%d: %d\n",  geneID, atoi(term+prefixOffset) + termOffset);
		}
	}

	// read interacting genes from g2g
	for(i=0; i<PyList_GET_SIZE(gene2gene); i++) {
		current = PyList_GET_ITEM(gene2gene, (Py_ssize_t)i);
		geneID = FindInt(gIds, (int) PyInt_AsLong(PyList_GET_ITEM(current, (Py_ssize_t)0)));

		// this is a list of genes
		tmp = PyList_GET_ITEM(current, (Py_ssize_t)1);
		for(j=0; j<PyList_GET_SIZE(tmp); j++) {
			gene = FindInt(gIds, (int) PyInt_AS_LONG(PyList_GET_ITEM(tmp, (Py_ssize_t)j)));
			SetAdd(g2g[geneID], gene);
			//fprintf(stderr, "%d: %d", geneID, gene);
		}
	}
}



void parse_gene_annotations()
{
	char str[10000], s[100], part[1000][1000], *ptr;
	int i, j, len, gID, offset, num_parts, plen;
	IntArray set1 = IntArrayNew(), set2 = IntArrayNew();

	printf("Parsing g2g file ... ");

	FILE *dat;

	strcpy(str, DB_dir);
	strcat(str, "g2ont");
	dat = open_file(str);
	while (fgets(str, 10000, dat))
	{
		str[0] = ' ';
		i = 1;
		while (is_digit(str[i]))
			i++;
		str[i] = 0;
		SetAdd(set1, atoi(str));
		//fprintf(stderr, "%s, ", str);
	}


	strcpy(str, DB_dir);
	strcat(str, "g2g");
	dat = open_file(str);
	while (fgets(str, 10000, dat))
	{
		len = strlen(str);
		i = 0;
		while (i < len)
		{
			while (!is_digit(str[i]) && (i < len))
				i++;
			if (i == len)
				break;
			s[0] = str[j = i];
			i++;

			while (is_digit(str[i]))
			{
				s[i - j] = str[i];
				i++;
			}
			s[i - j] = 0;
			j = atoi(s);

			SetAdd(set2, j);
			//fprintf(stderr, "%d, ", j);
		}
	}

	gIds = SetUnion(set1, set2);
	IntArrayFree(set1);
	IntArrayFree(set2);

	g2g = (IntArray *) malloc(gIds->len * sizeof(IntArray));
	g2ont = (IntArray *) malloc(gIds->len * sizeof(IntArray));
	for (i = 0; i < gIds->len; i++)
	{
		g2g[i] = IntArrayNew();
		g2ont[i] = IntArrayNew();
	}

	strcpy(str, DB_dir);
	strcat(str, "g2ont");
	dat = open_file(str);
	while (fgets(str, 10000, dat))
	{
		len = strlen(str);
		str[0] = ' ';
		i = 1;
		while (is_digit(str[i]))
			i++;
		str[i] = 0;
		gID = FindInt(gIds, atoi(str));

		num_parts = 0;
		while (i < len)
		{
			if (str[i] == '\'')
			{
				i++;
				plen = 0;
				while (str[i] != '\'') {
					part[num_parts][plen++] = str[i++];
				}
				part[num_parts++][plen] = 0;
			}
			i++;
		}

		for (i = 0; i < num_parts; i++)
		{
			if (part[i][0] == 'G')
			{
				offset = 0;
				ptr = part[i] + 3;
			}
			else
			{
				offset = lastGO + 1;
				ptr = part[i] + 5;
			}
			//fprintf(stderr, "%d: %d\n",  gID, atoi(ptr) + offset);
			SetAdd(g2ont[gID], atoi(ptr) + offset);
		}
	}


	strcpy(str, DB_dir);
	strcat(str, "g2g");
	dat = open_file(str);
	while (fgets(str, 10000, dat))
	{
		len = strlen(str);
		i = 0;
		while (!is_digit(str[i]) && (i < len))
			i++;
		s[0] = str[j = i];
		while (is_digit(str[i]))
		{
			s[i - j] = str[i];
			i++;
		}
		s[i - j] = 0;
		gID = FindInt(gIds, atoi(s));

		while (i < len)
		{
			while (!is_digit(str[i]) && (i < len))
				i++;
			if (i == len)
				break;
			s[0] = str[j = i];
			i++;
			while (is_digit(str[i]))
			{
				s[i - j] = str[i];
				i++;
			}
			s[i - j] = 0;
			j = FindInt(gIds, atoi(s));
			SetAdd(g2g[gID], j);
			//fprintf(stderr, "%d: %d", gID, j);
		}
	}

	printf("Done !\n");
}



/*
 * This function was added by V.P.
 * It reads the input from a Python list instead from a text file.
 */
void parse_general1(PyObject * generalTerms)
{
	PyObject *iterator = PyObject_GetIter(generalTerms);
	PyObject *item;
	char * term;
	int i;
	short ok;

	while ((item = PyIter_Next(iterator))) {
		term = PyString_AsString(item);

		ok = 0;
		for (i = 0; i < MaxONTterms; i++)
			if (Ont[i].type != 'E')
			    //fprintf(stderr, "%s\n", Ont[i].name);
				if (!strcmp(Ont[i].name, term)) {
					Ont[i].general = 1;
					ok = 1;
					//fprintf(stderr, "GENERAL: %s\n", term);
				}
		if (!ok) {
			fprintf(stderr, "WARNING: general term \"%s\" is unknown (not in the ontology)\n", term);
		}
		Py_DECREF(item);
	}

	Py_DECREF(iterator);

}



void parse_general()
{
	int i;
	char ok, str[1000];
	FILE *dat;

	strcpy(str, DB_dir);
	strcat(str, "general_terms.txt");
	dat = open_file(str);
	while (fgets(str, 10000, dat))
	{
		if (str[0] == '#')
			continue;
		ok = 0;
		i = strlen(str) - 1;
		while (!is_letter(str[i]))
			i--;
		str[i + 1] = 0;
		for (i = 0; i < MaxONTterms; i++)
			if (Ont[i].type != 'E')
				if (!strcmp(Ont[i].name, str))
				{
					Ont[i].general = 1;
					ok = 1;
					fprintf(stdout, "GENERAL: %s\n", str);
				}

		if (!ok)
		{
			printf("%s NOT FOUND\n", str);
			exit(0);
		}
	}
}

void print_ONT_raw(char type, int id)
{
	int offset = 0, i;
	if (type == 'K')
		offset = lastGO + 1;
	printf("%c %6d %s [", Ont[id].type, id - offset, Ont[id].name);
	for (i = 0; i < Ont[id].parent->len; i++)
		printf("%d ", Ont[id].parent->data[i]);
	printf("]\n");
}

void print_ONT(int id)
{
	int i;
	printf("ONT[%d].name =%s\n", id, Ont[id].name);
	for (i = 0; i < Ont[id].parent->len; i++)
		printf("Parent[%6d].name =%s\n", Ont[id].parent->data[i],
				Ont[Ont[id].parent->data[i]].name);
	for (i = 0; i < Ont[id].child->len; i++)
		printf(" Child[%6d].name =%s\n", Ont[id].child->data[i],
				Ont[Ont[id].child->data[i]].name);
}

void print_G2ONT(int gRaw)
{
	int i, id = FindInt(gIds, gRaw);
	if (id == -1)
	{
		printf("id=%d, not found !", gRaw);
		exit(1);
	}
	printf("Info for gID_RAW = %d\n", gRaw);
	for (i = 0; i < g2ont[id]->len; i++)
	{
		if (g2ont[id]->data[i] < lastGO)
			printf("G%d\n", g2ont[id]->data[i]);
		else
			printf("K%d\n", g2ont[id]->data[i] - lastGO);
	}
}

void print_G2G(int gRaw)
{
	int i, id = FindInt(gIds, gRaw);
	printf("Info for gID_RAW = %d\n", gRaw);
	for (i = 0; i < g2g[id]->len; i++)
	{
		printf("%d\n", gIds->data[g2g[id]->data[i]]);
	}
}


/*
 * This function was added by V.P.
 * It reads the input from two Python lists instead from a text file.
 */
void parse_input_file1(PyObject *geneIDs, PyObject *geneRanks)
{
	int ID, nGenes, *g;
	double weight, *w;

	// allocate arrays for ENTREZ indices of all input genes (g) and their weights (w)
	nGenes = PyList_GET_SIZE(geneIDs);
	g = (int *) malloc(nGenes * sizeof(int));
	w = (double *) malloc(nGenes * sizeof(double));

	input.n = 0;
	input.file_n = nGenes;
	for (Py_ssize_t i=0; i<nGenes; i++) {
		ID = (int) PyInt_AS_LONG(PyList_GET_ITEM(geneIDs, i));
		weight = PyFloat_AS_DOUBLE(PyList_GET_ITEM(geneRanks, i));

		g[input.n] = FindInt(gIds, ID);
		if (g[input.n] == -1)
		{
			//printf("New gene ID = %d\n", atoi(str));
			continue;
		}
		w[input.n] = weight;
		input.n++;
	}

	// the rest of the code here is the same as in the original function
	input.gene = IntArrayNew();
	input.original = IntArrayNew();
	input.sorted = IntArrayNew();
	input.weight = (double *) malloc(input.n * sizeof(double));
	for (int i = 0; i < input.n; i++)
	{
		AddInt(input.gene, g[i]);
		AddInt(input.original, g[i]);
		SetAdd(input.sorted, g[i]);
		input.weight[i] = w[i];
	}

	Minimum = (int) (sqrt(Cutoff) - 9);
	if (Minimum < 2)
		Minimum = 2;
	if (Minimum > 15)
		Minimum = 15;

	input.mean = 0;
	for (int i = 0; i < input.n; i++)
		input.mean += w[i];
	input.mean /= input.n;

	input.sd = 0;
	for (int i = 0; i < input.n; i++)
		input.sd += (w[i] - input.mean) * (w[i] - input.mean);
	input.sd = sqrt(input.sd / input.n);

	printf("mean = %f\nstd = %f\nmax = %f\nmin = %f\n", input.mean, input.sd,
			input.weight[0], input.weight[input.n - 1]);

	printf("Done !\n\n");
}


void parse_input_file()
{
	FILE *dat;
	char str[100], *ptr;
	char fname[100];
	int g[100000];
	double w[100000];

	printf("Parsing input file ... \n");

	strcpy(fname, BaseName);
	/* strcat(fname, ".csv"); */
	dat = open_file(fname);
	input.n = 0;
	input.file_n = 0;
	while (fgets(str, 10000, dat))
	{
		int i = 0;
		while (str[i] != ',')
			i++;
		str[i] = 0;
		g[input.n] = FindInt(gIds, atoi(str));
		input.file_n++;
		if (g[input.n] == -1)
		{
			//printf("New gene ID = %d\n", atoi(str));
			continue;
		}
		ptr = str + i + 1;
		w[input.n] = atof(ptr);
		input.n++;
	}
	input.gene = IntArrayNew();
	input.original = IntArrayNew();
	input.sorted = IntArrayNew();
	input.weight = (double *) malloc(input.n * sizeof(double));
	for (int i = 0; i < input.n; i++)
	{
		AddInt(input.gene, g[i]);
		AddInt(input.original, g[i]);
		SetAdd(input.sorted, g[i]);
		input.weight[i] = w[i];
	}

	Minimum = (int) (sqrt(Cutoff) - 9);
	if (Minimum < 2)
		Minimum = 2;
	if (Minimum > 15)
		Minimum = 15;

	input.mean = 0;
	for (int i = 0; i < input.n; i++)
		input.mean += w[i];
	input.mean /= input.n;

	input.sd = 0;
	for (int i = 0; i < input.n; i++)
		input.sd += (w[i] - input.mean) * (w[i] - input.mean);
	input.sd = sqrt(input.sd / input.n);

	printf("mean = %f\nstd = %f\nmax = %f\nmin = %f\n", input.mean, input.sd,
			input.weight[0], input.weight[input.n - 1]);

	printf("Done !\n\n");
}
