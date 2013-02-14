#include <python2.7/Python.h>

#include "def_var.h"

extern IntArray IntArrayNew();
extern void IntArrayFree(IntArray);
extern void AddInt(IntArray, int);
extern int FindInt(IntArray, int);
extern void AddIntSort(IntArray, int);
extern IntArray IntArrayMerge(IntArray, IntArray);
extern void SetAdd(IntArray, int);
extern IntArray SetIntsec(IntArray, IntArray);
extern IntArray SetUnion(IntArray, IntArray);
extern int SetEqual(IntArray, IntArray);
extern IntArray IntArrayCopy(IntArray);
extern void IntArrayPrint(IntArray);
extern int SimilarSets(IntArray, IntArray);

extern IntArray remove_general_terms(IntArray);
extern double fisher(int, int, int, int);
extern double gsea(IntArray, int *, IntArray, double *, double *);
extern double page(IntArray, int *, IntArray, double *, double, double);
extern GeneSet best_wracc(double *, PListGS, int*);
extern double wracc(double *, GeneSet, int*);

extern void write_progress(int);
extern void increase_progress(float);


GeneSet newGeneSet(int *term, int *inter, IntArray top_gene, IntArray gene_set)
{
	GeneSet s = (GeneSet) malloc(sizeof(struct TGeneSet));
	for (int i = 0; i < 4; i++)
	{
		s->term[i] = term[i];
		s->inter[i] = inter[i];
	}
	s->top_gene = IntArrayCopy(top_gene);
	s->gene = IntArrayCopy(gene_set);
	return s;
}

PListGS ListGS_New()
{
	PListGS x;
	x = (PListGS) malloc(sizeof(struct TListGeneSet));
	x->len = 0;
	x->allocated = InitLength;
	x->set = (GeneSet *) malloc(InitLength * sizeof(GeneSet));
	return x;
}

void AddGeneSet(PListGS x, GeneSet y)
{
	GeneSet *set;
	if (x->len < x->allocated)
		x->set[x->len++] = y;
	else
	{
		int len = x->len * 2;
		set = (GeneSet *) malloc(len * sizeof(GeneSet));
		for (int i = 0; i < x->len; i++)
			set[i] = x->set[i];
		x->allocated = len;
		free(x->set);
		x->set = set;
		AddGeneSet(x, y);
	}
}

void GeneSetFree(PListGS x)
{
	for (int i = 0; i < x->len; i++)
	{
		IntArrayFree(x->set[i]->gene);
		free(x->set[i]);
	}
	free(x->set);
	free(x);
}

/******************  PRINTING PROCEDURES  **********************************/

void print_GeneSet(FILE *dat, GeneSet gs, int rank)
{
	char out[10000];
	char names[4][10] =
	{ "Func(", "Proc(", "Comp(", "Path(" };
	out[0] = 0;

	for (int i = 0; i < 4; i++)
		if (gs->term[i] != root[i])
		{
			if (gs->inter[i])
				strcat(out, "int(");
			strcat(out, names[i]);
			strcat(out, Ont[gs->term[i]].name);
			strcat(out, ")");
			if (gs->inter[i])
				strcat(out, ")");
			strcat(out, ",\n");
		}

	if (WRITE_FILES) {
		fprintf(
				dat,
				"GeneSet %d\ntopCover=%3d, size=%4d fisher=%.2e(%4.2f) gsea=%5.3f(%4.2f) page=%6.3f(%4.2f) agr=%5.3f\n%s\n",
				rank, gs->top_gene->len, gs->gene->len, gs->fisher, gs->p_fisher,
				gs->gsea, gs->p_gsea, gs->page, gs->p_page, gs->p_agregate, out);
	}
}

void Term_2_Web(FILE *dat, int term, int o, int inter)
{
	char names[4][10] =
	{ "Func", "Proc", "Comp", "Path" };
	char go1[1000], go2[1000];
	if (inter)
		fprintf(dat, "INTERACT[ ");
	fprintf(dat, "%s(", names[o]);

	if (o < 3)
	{
		sprintf(go1, "%d", term);
		while (strlen(go1) < 7)
		{
			strcpy(go2, "0");
			strcat(go2, go1);
			strcpy(go1, go2);
		}
		fprintf(
				dat,
				"<a href=\"http://www.ebi.ac.uk/ego/DisplayGoTerm?id=GO:%s\">%s</a>",
				go1, Ont[term].name);
	}
	else
	{
		/*
		 sprintf(go1, "%d", term - lastGO - 1);
		 while(strlen(go1) < 5) {
		 strcpy(go2, "0");
		 strcat(go2, go1);
		 strcpy(go1, go2);
		 }
		 */
		strcpy(go1, Ont[term].name);
		for (int i = 0; i < strlen(go1); i++)
			if (go1[i] == ' ')
				go1[i] = '+';
		fprintf(
				dat,
				"<a href=\"http://www.genome.jp/kegg-bin/get_htext?htext=ko00001.keg&query=%s&filedir=/kegg/brite/ko\">%s</a>",
				go1, Ont[term].name);
		//fprintf(dat, "<a href=\"http://www.genome.ad.jp/dbget-bin/www_bget?path:hsa%s\">%s</a>", go1, Ont[term].name);
	}

	if (inter)
		fprintf(dat, ") ],<br>");
	else
		fprintf(dat, "),<br>");
}


/* This function was added by VP
 * It copies the name of the term into a given pointer to char array.
 * This name can be then matched against a database or a web service.
 */
void GetTermName(char *name, int term, int o, int inter)
{
	char go1[100], go2[100];
	char fullName[100];

	if (o < 3)
	{
		strcpy(fullName, "GO:");
		sprintf(go1, "%d", term);
		while (strlen(go1) < GO_TERM_NCIPHERS) {
			strcpy(go2, "0");
			strcat(go2, go1);
			strcpy(go1, go2);
		}
		strcat(fullName, go1);
		strcpy(name, fullName);
		//return fullGoName;
	}
	else
	{
		strcpy(fullName, "KEGG:");
		sprintf(go1, "%d", term - lastGO - 1);
		while(strlen(go1) < KEGG_TERM_NCIPHERS) {
			strcpy(go2, "0");
			strcat(go2, go1);
			strcpy(go1, go2);
		}
		strcat(fullName, go1);
		strcpy(name, fullName);
        /*
		// printf("----> %s  %d\n", Ont[term].name, term);
		strcpy(go1, Ont[term].name);
		for (int i = 0; i < strlen(go1); i++)
			if (go1[i] == ' ')
				go1[i] = '+';

		strcpy(name, go1);
		//return go1;
 	    */
	}
}




/* This function was modified by VP */

void Print_ListGS(PyObject * result, char * testName, char *fname, PListGS list, int up_down, int test_id)

{
	int printed_sets;
	char set_name[1000];

	PyObject * testsDict = PyDict_New();
	PyDict_SetItemString(result, testName, testsDict);


	printf("Enter print_gs: up_down=%d test_id=%d\n", up_down, test_id);

	FILE *dat, *dat_set;
	if (WRITE_FILES) {
		dat = fopen(fname, "w");
		sprintf(set_name, "%s.sets", BaseName);
		dat_set = fopen(set_name, "a");
	}

	for (int i = 0; i < list->len; i++)
		list->set[i]->flag = 1;

	if (WRITE_FILES) {
		fprintf(
				dat,
				"<html><head><STYLE TYPE=\"text/css\"><!-- TD{font-family: Arial; font-size: 11pt;} ---> </STYLE> </head> <body>");
		fprintf(dat, "<h2>Project: %s </h2>", project_name);

		if (up_down == 0)
			fprintf(dat, "<h2>Enriched genesets for class A</h2>");
		if (up_down == 1)
			fprintf(dat, "<h2>Enriched genesets for class B</h2>");

		if (test_id == 0)
			fprintf(dat, "<h3>found by Fisher exact test<h3>");
		if (test_id == 1)
			fprintf(dat, "<h3>found by GSEA method<h3>");
		if (test_id == 2)
			fprintf(dat, "<h3>found by PAGE algorithm<h3>");
		if (test_id == 3)
			fprintf(dat, "<h3>found by Combining p-values<h3>");

		fprintf(dat, "<TABLE border=\"1\" ALIGN=\"center\">");
		fprintf(
				dat,
				"<TR bgcolor=\"#9999CC\"><TD ALIGN=\"center\"><b>#<TD ALIGN=\"center\"><b>Description");
		fprintf(
				dat,
				"<TD ALIGN=\"center\"><b>&nbsp;Set size&nbsp;<TD ALIGN=\"center\"><b>&nbsp;#DE_Genes&nbsp;<TD ALIGN=\"center\">");
		fprintf(
				dat,
				"<b>Fisher p-value<br>&nbsp;(unadjusted p-value)&nbsp;<TD ALIGN=\"center\"><b>GSEA p-value<br>&nbsp;(Enricment score)&nbsp;");
		fprintf(dat,
				"<TD ALIGN=\"center\"><b>&nbsp;PAGE p-value&nbsp;<br>(Z-score)");
		if (test_id == 3)
			fprintf(dat,
					"<TD ALIGN=\"center\"><b>&nbsp;Agregate&nbsp;<br><i>p-value</i>");
	}

	printed_sets = 0;
	for (int i = 0; i < list->len; i++)
	{
		GeneSet gs = list->set[i];
		if (!gs->flag)
			continue;
		if (gs->p_agregate > P_Value)
			break;

		if (printed_sets++ == PrintTopGS)
			break;


		IntArray duplicate = IntArrayNew();
		AddInt(duplicate, i);
		for (int j = i + 1; j < list->len; j++)
		{
			GeneSet gs2 = list->set[j];

			if (!gs2->flag)
				continue;
			if (gs2->p_agregate > gs->p_agregate)
				break;

			if (!SetEqual(gs->gene, gs2->gene))
			{

				if (!Summarization)
					continue;

				if (!SimilarSets(gs->top_gene, gs2->top_gene))
					continue;
				if (!SimilarSets(gs->gene, gs2->gene))
					continue;

			}

			AddInt(duplicate, j);
			gs2->flag = 0;
		}

		if (WRITE_FILES) {
			if (printed_sets % 2)
				fprintf(
						dat,
						"<TR bgcolor=\"#CC9999\"><TD ALIGN=\"center\">&nbsp;%d&nbsp;",
						printed_sets);
			else
				fprintf(
						dat,
						"<TR bgcolor=\"#9999CC\"><TD ALIGN=\"center\">&nbsp;%d&nbsp;",
						printed_sets);
		}

		PyObject * termsList = PyList_New(0);

		if (WRITE_FILES) {
			fprintf(dat, "<TD ALIGN=\"center\">");
		}

		for (int t = 0; t < 4; t++)
		{

			// non interacting terms
			IntArray terms = IntArrayNew();
			for (int d = 0; d < duplicate->len; d++)
			{
				GeneSet gs = list->set[duplicate->data[d]];
				if ((gs->term[t] != root[t]) && !gs->inter[t])
					SetAdd(terms, gs->term[t]);
			}
			terms = remove_general_terms(terms);
			for (int tt = 0; tt < terms->len; tt++)
			{
				if (WRITE_FILES) {
					Term_2_Web(dat, terms->data[tt], t, 0);
				}

				char termName[100];
				GetTermName(termName, terms->data[tt], t, 0);
				PyObject * pyname = PyString_FromString(termName);

				PyList_Append(termsList, pyname);
				Py_DECREF(pyname);
			}

			//fprintf(dat, "%s(\'%s\'),<br>", names[t], Term_2_Web(terms->data[tt], 0));
			IntArrayFree(terms);
		}


		PyObject * interactList = PyList_New(0);
		for (int t = 0; t < 4; t++)
		{
			// interacting terms
			IntArray terms = IntArrayNew();
			for (int d = 0; d < duplicate->len; d++)
			{
				GeneSet gs = list->set[duplicate->data[d]];
				if ((gs->term[t] != root[t]) && gs->inter[t])
					SetAdd(terms, gs->term[t]);
			}
			terms = remove_general_terms(terms);
			for (int tt = 0; tt < terms->len; tt++)
			{
				if (WRITE_FILES) {
					Term_2_Web(dat, terms->data[tt], t, 1);
				}
				char termName[100];
				GetTermName(termName, terms->data[tt], t, 1);
				PyObject * pyname = PyString_FromString(termName);

				PyList_Append(interactList, pyname);
				Py_DECREF(pyname);

			}
			//fprintf(dat, "INTERACT[ %s(\'%s\') ],<br>", names[t], Ont[terms->data[tt]].name);
			IntArrayFree(terms);
		}
		PyList_Append(termsList, interactList);


		if (WRITE_FILES) {
			fprintf(
					dat,
					"<TD ALIGN=\"center\"><a href=\"../../tool.php?sets=%s&code=%d%d%d0\">%d</a>",
					BaseName, up_down, test_id, printed_sets, gs->gene->len);

			fprintf(
					dat,
					"<TD ALIGN=\"center\"><a href=\"../../tool.php?sets=%s&code=%d%d%d1\">%d</a>",
					BaseName, up_down, test_id, printed_sets, gs->top_gene->len);
		}


		/* added by V.P. 22.12.2009 */
		double fisher_p = gs->p_fisher, unadjusted_p = gs->fisher,
				gsea_p = gs->p_gsea, enrichment_score = gs->gsea,
				page_p = gs->p_page, z_score = gs->page;
		
		double aggregate_p;
		if (test_id == 3)
			aggregate_p = gs->p_agregate;
		else
			aggregate_p = -1;
		/* ----------------------- */


		if (WRITE_FILES) {
			if (test_id == 0)
				fprintf(dat,
						"<TD ALIGN=\"center\"><b> %5.3f<br>&nbsp;(%.2e)&nbsp;",
						gs->p_fisher, gs->fisher);
			else
				fprintf(dat,
						"<TD ALIGN=\"center\">    %5.3f<br>&nbsp;(%.2e)&nbsp;",
						gs->p_fisher, gs->fisher);

			if (test_id == 1)
				fprintf(dat,
						"<TD ALIGN=\"center\"><b> %5.3f<br>&nbsp;(%5.3f)&nbsp;",
						gs->p_gsea, gs->gsea);
			else
				fprintf(dat,
						"<TD ALIGN=\"center\">    %5.3f<br>&nbsp;(%5.3f)&nbsp;",
						gs->p_gsea, gs->gsea);

			if (test_id == 2)
				fprintf(dat,
						"<TD ALIGN=\"center\"><b> %5.3f<br>&nbsp;(%6.3f)&nbsp;",
						gs->p_page, gs->page);
			else
				fprintf(dat,
						"<TD ALIGN=\"center\">    %5.3f<br>&nbsp;(%6.3f)&nbsp;",
						gs->p_page, gs->page);

			if (test_id == 3)
				fprintf(dat, "<TD ALIGN=\"center\"><b> &nbsp;%5.3f&nbsp;",
						gs->p_agregate);
			fprintf(dat, "</TR>");
		}
		IntArrayFree(duplicate);


		PyObject * groupDataDict = PyDict_New();
		PyObject * scores = PyDict_New();

		PyObject * allGenesList = PyList_New((Py_ssize_t) gs->gene->len);
		PyObject * topGenesList = PyList_New((Py_ssize_t) gs->top_gene->len);


		PyDict_SetItemString(groupDataDict, ALL_GENES_KEY, allGenesList);
		PyDict_SetItemString(groupDataDict, TOP_GENES_KEY, topGenesList);
		PyDict_SetItemString(groupDataDict, TERMS_KEY, termsList);
		PyDict_SetItemString(groupDataDict, SCORES, scores);


		PyObject * temp;

		temp = PyFloat_FromDouble(fisher_p);
		PyDict_SetItemString(scores, FISHER_PVAL, temp);
		Py_DECREF(temp);

		temp = PyFloat_FromDouble(unadjusted_p);
		PyDict_SetItemString(scores, UNADJUSTED_PVAL, temp);
		Py_DECREF(temp);

		temp = PyFloat_FromDouble(gsea_p);
		PyDict_SetItemString(scores, GSEA_PVAL, temp);
		Py_DECREF(temp);

		temp = PyFloat_FromDouble(enrichment_score);
		PyDict_SetItemString(scores, ENRICHMENT_SCORE, temp);
		Py_DECREF(temp);

		temp = PyFloat_FromDouble(page_p);
		PyDict_SetItemString(scores, PAGE_PVAL, temp);
		Py_DECREF(temp);

		temp = PyFloat_FromDouble(z_score);
		PyDict_SetItemString(scores, Z_SCORE, temp);
		Py_DECREF(temp);
		
		
		/**
		 *  Added by A.V.
		 */
		temp = PyFloat_FromDouble(gs->wracc);
		PyDict_SetItemString(scores, WRACC_SCORE, temp);
		Py_DECREF(temp); 

		if (test_id == 3) {
			temp = PyFloat_FromDouble(aggregate_p);
			PyDict_SetItemString(scores, AGGREGATE_PVAL, temp);
			Py_DECREF(temp);
		}
		else
			PyDict_SetItemString(scores, AGGREGATE_PVAL, Py_None);


		if (WRITE_FILES) {
			fprintf(dat_set, "%d%d%d0\n", up_down, test_id, printed_sets);
		}
		for (int i = 0; i < gs->gene->len; i++)
		{
			if (WRITE_FILES) {
				fprintf(dat_set, "%d, ", gIds->data[gs->gene->data[i]]);
			}

			PyList_SET_ITEM(allGenesList, (Py_ssize_t)i, PyInt_FromLong((long) gIds->data[gs->gene->data[i]]));
			//temp = PyInt_FromLong((long) gIds->data[gs->gene->data[i]]);
			//PyDict_SetItem(allGenesDict, temp, Py_None); //PyBool_FromLong(1));
			//Py_DECREF(temp);
		}
		if (WRITE_FILES) {
			fprintf(dat_set, "\n");
			fprintf(dat_set, "%d%d%d1\n", up_down, test_id, printed_sets);
		}
		for (int i = 0; i < gs->top_gene->len; i++)
		{
			if (WRITE_FILES) {
				fprintf(dat_set, "%d, ", gIds->data[gs->top_gene->data[i]]);
			}
			PyList_SET_ITEM(topGenesList, (Py_ssize_t)i, PyInt_FromLong((long) gIds->data[gs->top_gene->data[i]]));
			//temp = PyInt_FromLong((long) gIds->data[gs->top_gene->data[i]]);
			//PyDict_SetItem(topGenesDict, temp, Py_None); //PyBool_FromLong(1));
			//Py_DECREF(temp);
		}
		if (WRITE_FILES) {
			fprintf(dat_set, "\n");
		}

		temp = PyInt_FromLong((long) printed_sets);
		PyDict_SetItem(testsDict, temp, groupDataDict);
		Py_DECREF(temp);


		Py_DECREF(groupDataDict);
		Py_DECREF(allGenesList);
		Py_DECREF(topGenesList);
		Py_DECREF(scores);

		Py_DECREF(termsList);
		Py_DECREF(interactList);
	}


	if (WRITE_FILES) {
		fprintf(dat, "</TABLE></body></html>");
		fclose(dat);
		fclose(dat_set);
	}

	Py_DECREF(testsDict);

	printf("DONE !\n");
}

/****** RECURSIVE PROCEDURE FOR GENERATING GENE SETS THAT SATISFY THE CONSTRAINT ****/

void generate(PListGS Results, int CurrNumTerms, int level, int *term, int *inter, IntArray cut_genes, IntArray set_genes, int int_terms)
{
	IntArray new_cut, new_set;
	int _term = term[level], i;
	int _inter = inter[level];

	if (_term == root[level])
	{
		if (level < 3)
		{
			term[level + 1] = root[level + 1];
			generate(Results, CurrNumTerms, level + 1, term, inter, cut_genes, set_genes, int_terms);
		}
		else if (CurrNumTerms)
			AddGeneSet(Results, newGeneSet(term, inter, cut_genes, set_genes));

		if ((CurrNumTerms == MaxNumTerms) || !include_ont[level])
			return;
		CurrNumTerms++;

		inter[level] = 0;
		for (i = 0; i < Ont[_term].child->len; i++)
		{
			term[level] = Ont[_term].child->data[i];
			generate(Results, CurrNumTerms, level, term, inter, cut_genes, set_genes, int_terms);
		}
		if (int_terms < MaxInterTerms)
		{
			inter[level] = 1;
			for (i = 0; i < Ont[_term].child->len; i++)
			{
				term[level] = Ont[_term].child->data[i];
				generate(Results, CurrNumTerms, level, term, inter, cut_genes, set_genes, int_terms + 1);
			}
		}

		CurrNumTerms--;

	}
	else
	{

		if (!_inter && (Ont[_term].gene->len < Min_Size_GS))
			return;
		if (_inter && (Ont[_term].i_gene->len < Min_Size_GS))
			return;

		if (_inter)
			new_cut = SetIntsec(cut_genes, Ont[_term].i_gene);
		else
			new_cut = SetIntsec(cut_genes, Ont[_term].gene);

		if (new_cut->len < Minimum)
		{
			IntArrayFree(new_cut);
			return;
		}

		if (_inter)
			new_set = SetIntsec(set_genes, Ont[_term].i_gene);
		else
			new_set = SetIntsec(set_genes, Ont[_term].gene);

		if (new_set->len < Min_Size_GS)
		{
			IntArrayFree(new_cut);
			IntArrayFree(new_set);
			return;
		}

		if (!Ont[_term].general)
		{
			if (level < 3)
			{
				term[level + 1] = root[level + 1];
				generate(Results, CurrNumTerms, level + 1, term, inter, new_cut, new_set, int_terms);
			}
			else
				AddGeneSet(Results, newGeneSet(term, inter, new_cut, new_set));
		}

		for (i = 0; i < Ont[_term].child->len; i++)
		{
			term[level] = Ont[_term].child->data[i];
			generate(Results, CurrNumTerms, level, term, inter, new_cut, new_set, int_terms);
		}

		IntArrayFree(new_cut);
		IntArrayFree(new_set);
	}

}

/********   FUNCTIONS USED FOR SORTING GENE SETS BY THEIR SCORES   **********/

int CompareFISHER(const void *p1, const void *p2)
{
	GeneSet *s1 = (GeneSet*) p1, *s2 = (GeneSet*) p2;
	if ((*s1)->fisher > (*s2)->fisher)
		return 1;
	else
		return 0;
}

int CompareGSEA(const void *p1, const void *p2)
{
	GeneSet *s1 = (GeneSet*) p1, *s2 = (GeneSet*) p2;
	if ((*s2)->gsea > (*s1)->gsea)
		return 1;
	else
		return 0;
}

int ComparePAGE(const void *p1, const void *p2)
{
	GeneSet *s1 = (GeneSet*) p1, *s2 = (GeneSet*) p2;
	if ((*s2)->page > (*s1)->page)
		return 1;
	else
		return 0;
}

int CompareAgregate(const void *p1, const void *p2)
{
	GeneSet *s1 = (GeneSet*) p1, *s2 = (GeneSet*) p2;
	if ((*s1)->p_agregate > (*s2)->p_agregate)
		return 1;
	else
		return 0;
}

/**
 * 
 * For sorting by wracc values.
 * 
 * Added by Anze Vavpetic <anze.vavpetic@ijs.si>. 
 * 
 */
int CompareWRAcc(const void *p1, const void *p2)
{
	GeneSet *s1 = (GeneSet*) p1, *s2 = (GeneSet*) p2;
	if ((*s1)->wracc < (*s2)->wracc)
		return 1;
	else
		return 0;
}

void SortPListGS(PListGS TrueResults)
{
	for (int i = 0; i < TrueResults->len - 1; i++)
	{
		for (int j = i + 1; j < TrueResults->len; j++)
			if (TrueResults->set[i]->p_agregate
					> TrueResults->set[j]->p_agregate)
			{
				GeneSet tmp = TrueResults->set[i];
				TrueResults->set[i] = TrueResults->set[j];
				TrueResults->set[j] = tmp;
			}
	}
}

/** 
  * 
  * Compute wracc scores. 
  * 
  * Added by Anze Vavpetic <anze.vavpetic@ijs.si>. 
  *
  **/
void compute_wracc(PListGS ruleset)
{
	printf("WRAcc computation ...");
	
	//wracc_k = 5;
	int examplesLeft = input.n;
	int rulesLeft = ruleset->len;
	int *timesCovered = (int*) malloc(input.n * sizeof(int));
	double *weight = (double*) malloc(input.n * sizeof(double));
	
	int *pos_gene = (int*) malloc(gIds->len*sizeof(int));
	
	//printf("gIds->len %d", gIds->len);
	   
	for(int i = 0; i < input.n; i++) {
	    pos_gene[input.gene->data[i]] = i;
	}
	
	// Init some structures.
	for (int i = 0; i < input.n; i++) {
	    timesCovered[i] = 0;
	    weight[i] = 1;
	}
	for (int i = 0; i < ruleset->len; i++) {
	    ruleset->set[i]->wracc = UNDEF; 
	}
	
	// Main loop.
	while (examplesLeft > 0 && rulesLeft > 0) 
	{  
	    GeneSet best = best_wracc(weight, ruleset, pos_gene);
	    
	    // Finish if no non-zero wracc score.
	    if (best == NULL)
	      break;
	    
	    best->used = TRUE;
	    rulesLeft--;
	    
	    // Decrease weights of covered examples.
	    for (int i = 0; i < best->gene->len; i++) {
		int idx = pos_gene[best->gene->data[i]];
		
		// Skip already covered examples.
		if (weight[idx] == UNDEF) 
		  continue;

		int k = ++timesCovered[idx];
		if (k > wracc_k) {
		    weight[idx] = UNDEF;		// Remove example.
		    examplesLeft--;
		} else {
		    weight[idx] = 1 / (double) k;
		}
	    }
	}
	
	/* 
	 * Re-calculate WRAcc of the selected rules in order to reflect the 
	 * interestingness of each rule independently of each other.
	 */
	
	// Reset the weights.
	for (int i = 0; i < input.n; i++) {
	    weight[i] = 1;
	}
	
	// Recalculate the scores with example weights 1 for each selected rule.
	for (int i = 0; i < ruleset->len; i++) {
	    if (ruleset->set[i]->wracc != UNDEF) {
	        double new_wracc = wracc(weight, ruleset->set[i], pos_gene);
		ruleset->set[i]->wracc = new_wracc;
	    }
	}
	
	// Cleanup.
	free(timesCovered);
	free(weight);
	free(pos_gene);
	
	printf("Done!\n");
}

/*********** MAIN PART OF THE ANALYSIS   *************************/

void Analysis(PyObject * result)
{
	char fname[1000];
	int  *pos_gene; //term[4], inter[4];
	double *wbl, result_test[MAX_ITERATIONS + 2][3];
	PListGS TrueResults_UP = NULL, TrueResults_DOWN = NULL;
	time_t start_time, end_time;

	pos_gene = (int*) malloc(gIds->len * sizeof(int));
	wbl = (double*) malloc(input.n * sizeof(double));

	void Evaluate_List_GeneSet(PyObject * resultDict, PListGS TrueResults, int up_down)
	{

		// calculate experimental fisher, gsea and page p-value
		for (int i = 0; i < TrueResults->len; i++)
		{
			GeneSet gs = TrueResults->set[i];

			int better = 0;
			for (int j = 1; j < NumberIterations + 1; j++)
				if (gs->fisher > result_test[j][0])
					better++;
			gs->p_fisher = (1.0 * better) / NumberIterations;

			better = 0;
			for (int j = 1; j < NumberIterations + 1; j++)
				if (gs->gsea < result_test[j][1])
					better++;
			gs->p_gsea = (1.0 * better) / NumberIterations;

			better = 0;
			for (int j = 1; j < NumberIterations + 1; j++)
				if (gs->page < result_test[j][2])
					better++;
			gs->p_page = (1.0 * better) / NumberIterations;

			gs->p_agregate = (W_fisher * gs->p_fisher + W_gsea * gs->p_gsea
					+ W_page * gs->p_page) / (W_fisher + W_gsea + W_page);
		}

		if (LINUX)
			qsort(TrueResults->set, TrueResults->len, sizeof(GeneSet),
					CompareAgregate);
		else
			SortPListGS(TrueResults);
		sprintf(fname, "%s.%d.all.html", BaseName, up_down);
		Print_ListGS(resultDict, ALL_NAME, fname, TrueResults, up_down, 3);
		//write_progress(100 + 4* up_down + 0);

		for (int i = 0; i < TrueResults->len; i++)
			TrueResults->set[i]->p_agregate = TrueResults->set[i]->p_fisher;
		if (LINUX)
			qsort(TrueResults->set, TrueResults->len, sizeof(GeneSet),
					CompareFISHER);
		else
		{
			SortPListGS(TrueResults);
		}
		sprintf(fname, "%s.%d.fisher.html", BaseName, up_down);
		Print_ListGS(resultDict, FISHER_NAME, fname, TrueResults, up_down, 0);
		//write_progress(100 + 4* up_down + 1);

		for (int i = 0; i < TrueResults->len; i++)
			TrueResults->set[i]->p_agregate = TrueResults->set[i]->p_gsea;
		if (LINUX)
			qsort(TrueResults->set, TrueResults->len, sizeof(GeneSet),
					CompareGSEA);
		else
		{
			SortPListGS(TrueResults);
		}
		sprintf(fname, "%s.%d.gsea.html", BaseName, up_down);
		Print_ListGS(resultDict, GSEA_NAME, fname, TrueResults, up_down, 1);
		//write_progress(100 + 4* up_down + 2);

		for (int i = 0; i < TrueResults->len; i++)
			TrueResults->set[i]->p_agregate = TrueResults->set[i]->p_page;
		if (LINUX)
			qsort(TrueResults->set, TrueResults->len, sizeof(GeneSet),
					ComparePAGE);
		else
		{
			SortPListGS(TrueResults);
		}
		sprintf(fname, "%s.%d.page.html", BaseName, up_down);
		Print_ListGS(resultDict, PAGE_NAME, fname, TrueResults, up_down, 2);
		//write_progress(100 + 4* up_down + 3);

		
		/**
		 * 
		 * Added by A.V. for WRAcc.
		 * 
		 */
		for (int i = 0; i < TrueResults->len; i++)
			TrueResults->set[i]->p_agregate = TrueResults->set[i]->wracc;
		if (LINUX)
			qsort(TrueResults->set, TrueResults->len, sizeof(GeneSet),
					CompareWRAcc);
		else
		{
			SortPListGS(TrueResults);
		}
		sprintf(fname, "%s.%d.wracc.html", BaseName, up_down);
		Print_ListGS(resultDict, WRACC_NAME, fname, TrueResults, up_down, 4);
		
	}
	/*****************************/


	  //--------calculate the input to independent iterations

	  struct TInput input_iter[1002];

	  for(int iteration = 0; iteration < NumberIterations + 2; iteration++) {

	    // for the first iteration
	    if (iteration == 0) {
	      input_iter[0].gene   = input.gene;
	      input_iter[0].weight = input.weight;
	      input_iter[0].mean   = input.mean;
	      continue;
	    }

	    // for the permuation testing
	    if(iteration < NumberIterations + 1) {
	      input_iter[iteration].mean   = input.mean;
	      input_iter[iteration].weight = input.weight;

	      input_iter[iteration].gene   = IntArrayNew();
	      for(int i = 0; i < input.n; i++)
	        AddInt(input_iter[iteration].gene, input_iter[iteration-1].gene->data[i]);
	      // Permutate
	      for(int i = 0; i < input.n; i++) {
	        int j = rand()%(input.n - i);
	        int tmp = input_iter[iteration].gene->data[input.n - 1 - i];
	        input_iter[iteration].gene->data[input.n - 1 - i] = input_iter[iteration].gene->data[j];
	        input_iter[iteration].gene->data[j] = tmp;
	      }
	      continue;
	    }
	    // for the last iteration
	    input_iter[iteration].mean   = -input.mean;
	    input_iter[iteration].weight = (double *)malloc(input.n*sizeof(double));
	    for(int i = 0; i < input.n; i++)
	      input_iter[iteration].weight[i] = -input.weight[input.n - i - 1];
	    input_iter[iteration].gene   = IntArrayNew();
	    for(int i = 0; i < input.n; i++)
	      AddInt(input_iter[iteration].gene, input.gene->data[input.n - i - 1]);

	  }
	//---------------------------


	printf("\nStart the analysis ... \n");
	time(&start_time);

	// Make NumIterations interations for calculation of experimental p-values
	// first iteration is for UP regulated, last for DOWN regulated gene sets
	int uproc, nproc = omp_get_num_procs();
	uproc = (nproc > 2) ? (nproc-1) : 2;
	fprintf(stdout, "processors available: %d; segs will use: %d\n\n", nproc, uproc);
	
	float incr = 100.0/(NumberIterations+2);

	omp_set_num_threads(uproc);
	#pragma omp parallel for schedule(dynamic, 1)
	for (int iteration = 0; iteration < NumberIterations + 2; iteration++)
	{
	    int term[4], inter[4], *pos_gene, CurrNumTerms;
	    pos_gene = (int*)malloc(gIds->len*sizeof(int));
	    double *wbl = (double*)malloc(input.n*sizeof(double));

	    PListGS Results = ListGS_New();
	    IntArray cutSet = IntArrayNew();

	    for(int i = 0; i < Cutoff ; i++) SetAdd(cutSet, input_iter[iteration].gene->data[i]);
	    for(int i = 0; i < input.n; i++) pos_gene[input_iter[iteration].gene->data[i]] = i;

	    // Generate the gene sets
	    term[0] = root_F; CurrNumTerms = 0;
	    generate(Results, CurrNumTerms, 0, term, inter, cutSet, input.sorted, 0);

	    IntArrayFree(cutSet);

	    // Evaluate the gene sets
	    for(int i = 0; i < Results->len; i++) {
	      GeneSet gs = Results->set[i];
	     	gs->fisher = fisher(input.n, gs->gene->len, Cutoff, gs->top_gene->len);
	     	gs->gsea   = gsea(input_iter[iteration].gene, pos_gene, gs->gene, input_iter[iteration].weight, wbl);
	     	gs->page   = page(input_iter[iteration].gene, pos_gene, gs->gene, input_iter[iteration].weight,
	                        input_iter[iteration].mean, input.sd);
	    }

	    // Find the best fisher value
	    double best_fisher = 2;
	    for(int i = 0; i < Results->len; i++)
	      if(best_fisher > Results->set[i]->fisher)
	        best_fisher = Results->set[i]->fisher;
	    result_test[iteration][0] = best_fisher;

	    // Fint the best gsea value
	    double best_gsea = -100;
	    for(int i = 0; i < Results->len; i++)
	      if(best_gsea < Results->set[i]->gsea)
	        best_gsea = Results->set[i]->gsea;
	    result_test[iteration][1] = best_gsea;

	    // Find the best page value
	    double best_page = -100;
	    for(int i = 0; i < Results->len; i++)
	      if(best_page < Results->set[i]->page)
	        best_page = Results->set[i]->page;
	    result_test[iteration][2] = best_page;

	    // Print the best values
	    printf("Iteration %2d: fisher = %.3e gsea = %6.3f page = %6.3f sets = %6d\n",
	                     iteration, best_fisher, best_gsea, best_page, Results->len);


	    // In Iteration = 0, we generate overexpressed genesets
	    if(iteration == 0)
	    	TrueResults_UP = Results;
	    else {
	    	// In the last Iteration, we generate underexpressed genesets
	    	if	(iteration == NumberIterations + 1)
	    		TrueResults_DOWN = Results;
 	    	else  // in other iterations we generate enriched genesets on permutated data
 	    		GeneSetFree(Results);
	    }

		#pragma omp critical
	    //write_progress((int)((100.00 * (iteration + 1)) / (NumberIterations + 2)));
	   increase_progress(incr);

	   free(pos_gene);
	   free(wbl);
	}
	
	// Compute wracc scores.
	compute_wracc(TrueResults_UP);

	time(&end_time);
	printf("End of the analysis !\n");
	printf("Time for Analysis = %.2fsec\n", difftime(end_time, start_time));


	PyObject * classAdict = PyDict_New();
	PyObject * classBdict = PyDict_New();

	Evaluate_List_GeneSet(classAdict, TrueResults_UP, 0);
	Evaluate_List_GeneSet(classBdict, TrueResults_DOWN, 1);

	PyDict_SetItemString(result, CLASS_A, classAdict);
	PyDict_SetItemString(result, CLASS_B, classBdict);
	Py_DECREF(classAdict);
	Py_DECREF(classBdict);

	GeneSetFree(TrueResults_UP);
 	GeneSetFree(TrueResults_DOWN);

	printf("Finished printing the results!\n");
}