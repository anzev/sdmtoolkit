#include <stdio.h>

#include <python2.7/Python.h>
#include "def_var.h"

extern IntArray IntArrayNew();
extern void SetAdd(IntArray, int);
extern IntArray SetUnion(IntArray, IntArray);
extern void IntArrayFree(IntArray);
extern int FindInt(IntArray, int);
extern void AddInt(IntArray, int);

extern void newTerm(struct TOnt *, char, char *);
//extern void parse_general();
extern void parse_general1();

void init_app()
{

	printf("Init App ... ");

	for (int i = 0; i < MaxONTterms; i++)
	{
		Ont[i].type = 'E';
		Ont[i].general = 0;
	}

	printf("Done !\n");
}

void done_app()
{
	printf("Done App ... ");

	for (int i = 0; i < MaxONTterms; i++)
		if (Ont[i].type != 'E')
		{
			free(Ont[i].name);
			IntArrayFree(Ont[i].parent);
			IntArrayFree(Ont[i].child);
			IntArrayFree(Ont[i].gene);
			IntArrayFree(Ont[i].i_gene);
			IntArrayFree(Ont[i].more_general);
		}

	for (int i = 0; i < gIds->len; i++)
	{
		IntArrayFree(g2g[i]);
		IntArrayFree(g2ont[i]);
	}
	free(g2g);
	free(g2ont);

	IntArrayFree(input.gene);
	IntArrayFree(input.original);
	IntArrayFree(input.sorted);
	free(input.weight);

	printf("Done !\n");
}

IntArray remove_general_terms(IntArray terms)
{
	IntArray out = IntArrayNew();
	for (int i = 0; i < terms->len; i++)
	{
		int general = 0;
		for (int j = 0; j < terms->len; j++)
			if ((i != j) && (FindInt(Ont[terms->data[j]].more_general,
					terms->data[i]) != -1))
			{
				general = 1;
				break;
			}
		if (general)
			continue;
		SetAdd(out, terms->data[i]);
	}
	IntArrayFree(terms);
	return out;
}

void Calc_Child_Nodes_and_Roots()
{

	printf("Calc Child Nodes and Roots ... ");
	fflush(stdout);

	//find first empty place after the last term
	root_F = MaxONTterms - 1;
	while (Ont[root_F].type == 'E')
		root_F--;

	//first add root nodes for GO terms, to collect the nodes without fathers
	root_F++;
	newTerm(&Ont[root_F], 'F', "Root_F");
	root_P = root_F + 1;
	newTerm(&Ont[root_P], 'P', "Root_P");
	root_C = root_P + 1;
	newTerm(&Ont[root_C], 'C', "Root_C");

	//add all terms to the list of their fathers
	for (int i = 0; i < root_F; i++)
		if (Ont[i].type != 'E')
			for (int j = 0; j < Ont[i].parent->len; j++)
			{
				SetAdd(Ont[Ont[i].parent->data[j]].child, i);
			}

	//add all terms without parents to its appropriate root node
	for (int i = 0; i < root_F; i++)
	{
		if ((Ont[i].type == 'F') && (Ont[i].parent->len == 0))
		{
			SetAdd(Ont[root_F].child, i);
			SetAdd(Ont[i].parent, root_F);
		}
		if ((Ont[i].type == 'P') && (Ont[i].parent->len == 0))
		{
			SetAdd(Ont[root_P].child, i);
			SetAdd(Ont[i].parent, root_P);
		}
		if ((Ont[i].type == 'C') && (Ont[i].parent->len == 0))
		{
			SetAdd(Ont[root_C].child, i);
			SetAdd(Ont[i].parent, root_C);
		}
		if ((Ont[i].type == 'K') && !strcmp(Ont[i].name, "pathway"))
			root_K = i;
	}

	//root needed for generate procedure
	root[0] = root_F;
	root[1] = root_P;
	root[2] = root_C;
	root[3] = root_K;

	printf("Done !\n");
}

void Calc_General_Terms(PyObject * generalTerms)
{

	IntArray more_general(int term)
	{
		if (Ont[term].flag)
			return Ont[term].more_general;
		IntArray out = IntArrayNew();
		IntArray parent = Ont[term].parent;
		for (int i = 0; i < parent->len; i++)
		{
			IntArray new_out = SetUnion(out, more_general(parent->data[i]));
			SetAdd(new_out, parent->data[i]);
			IntArrayFree(out);
			out = new_out;
		}
		Ont[term].more_general = out;
		Ont[term].flag = 1;
		return out;
	}

	printf("Calc General Terms ... ");

	// calculate the level of ONT terms
	for (int i = 0; i < MaxONTterms; i++)
		Ont[i].level = 100;
	for (int i = 0; i < 4; i++)
		Ont[root[i]].level = 0;

	while (1)
	{
		int ok = 0;
		for (int i = 0; i < MaxONTterms; i++)
			if (Ont[i].type != 'E')
				for (int j = 0; j < Ont[i].parent->len; j++)
				{
					int p = Ont[i].parent->data[j];
					if (Ont[p].level + 1 < Ont[i].level)
					{
						Ont[i].level = Ont[p].level + 1;
						ok = 1;
					}
				}
		if (!ok)
			break;
	}

	// mark as general user defined terms
	//parse_general();
	parse_general1(generalTerms);

	// mark as general all nodes on first 2 levels
	
	/*
	 *  MODIFIED FOR g-SEGS by A.V.: 
	 *  since the ontologies are now arbitrary, we must let the user decide what is or isn't too general!
	 *  Hence we only set the root nodes to general.
     * 
     *  [F]unc, [P]rocess, [C]omponent, [K]egg path, [E]mpty
	 */
	for (int i = 0; i < MaxONTterms; i++)
		if (Ont[i].type != 'E')
		{
// #if GSEGS
//             if ((Ont[i].type != 'K') && (Ont[i].level < 1))
// #else
// 			if ((Ont[i].type != 'K') && (Ont[i].level < 3))
// #endif
// 				Ont[i].general = 1;
// #if GSEGS
//             if ((Ont[i].type == 'K') && (Ont[i].level < 1))
// #else
// 			if ((Ont[i].type == 'K') && (Ont[i].level < 2))
// #endif
// 				Ont[i].general = 1;

#if GSEGS
            if ((Ont[i].type == 'F') && (Ont[i].level < general_level[0])) {
                Ont[i].general = 1;
            }
            
            if ((Ont[i].type == 'P') && (Ont[i].level < general_level[1])) {
                Ont[i].general = 1;
            }
            
            if ((Ont[i].type == 'C') && (Ont[i].level < general_level[2])) {
                Ont[i].general = 1;
            }
            
            if ((Ont[i].type == 'K') && (Ont[i].level < general_level[3])) {
                Ont[i].general = 1;
            }
#else
            if ((Ont[i].type != 'K') && (Ont[i].level < 3)) {
                Ont[i].general = 1;
            }
            
            if ((Ont[i].type == 'K') && (Ont[i].level < 2)) {
                Ont[i].general = 1;
            }
#endif
		}

	// calculate all the ancestors of ONT terms
	for (int i = 0; i < MaxONTterms; i++)
		Ont[i].flag = 0;
	for (int i = 0; i < MaxONTterms; i++)
		if (Ont[i].type != 'E')
			Ont[i].more_general = more_general(i);

	// if a term is general, all its ancestors are general
	for (int i = 0; i < MaxONTterms; i++)
		if (Ont[i].type != 'E')
			if (Ont[i].general)
			{
				IntArray general = Ont[i].more_general;
				for (int j = 0; j < general->len; j++)
					Ont[general->data[j]].general = 1;
			}

	printf("Done !\n");
}

void Fill_ONT_terms()
{
	void make_ont2gene(int node)
	{

		//if the term collected its genes, return
		if (Ont[node].flag)
			return;
		
		//printf("Start: %s", Ont[node].name);
		
		//if not, first all its children collect their genes, then the term collect them.
		for (int c = 0; c < Ont[node].child->len; c++)
		{
			make_ont2gene(Ont[node].child->data[c]);
			if (Ont[Ont[node].child->data[c]].gene->len > 0)
			{
				IntArray tmpset = SetUnion(Ont[node].gene,
						Ont[Ont[node].child->data[c]].gene);
				IntArrayFree(Ont[node].gene);
				Ont[node].gene = tmpset;

				tmpset = SetUnion(Ont[node].i_gene,
						Ont[Ont[node].child->data[c]].i_gene);
				IntArrayFree(Ont[node].i_gene);
				Ont[node].i_gene = tmpset;
			}
		}
		Ont[node].flag = 1;
		
		//printf("End.\n");
	}

	printf("Generalize Annotations ... ");

	//add input genes to their ONT terms
	for (int i = 0; i < input.n; i++)
	{
		int g = input.gene->data[i];
		for (int o = 0; o < g2ont[g]->len; o++)
			if (Ont[g2ont[g]->data[o]].type != 'E')
				SetAdd(Ont[g2ont[g]->data[o]].gene, g);
	}


	//add interacting genes to ONT terms
	for (int o = 0; o < MaxONTterms; o++)
		if (Ont[o].type != 'E')
			for (int i = 0; i < Ont[o].gene->len; i++)
			{
				int g = Ont[o].gene->data[i];
				for (int gg = 0; gg < g2g[g]->len; gg++)
					SetAdd(Ont[o].i_gene, g2g[g]->data[gg]);
			}


	//fprintf(stderr, "---> %d, %d, %d, %d \n", root_F, root_P, root_C, root_K);

	//Collect the genes from the roots, TOP-DOWN recursively
	for (int i = 0; i < MaxONTterms; i++)
		Ont[i].flag = 0;
	
	for (int i = 0; i < 4; i++)
	{
		make_ont2gene(root[i]);
	}

	//add all genes to the top root terms
	for (int i = 0; i < 4; i++)
		for (int g = 0; g < input.n; g++)
		{
			SetAdd(Ont[root[i]].gene, input.gene->data[g]);
			SetAdd(Ont[root[i]].i_gene, input.gene->data[g]);
		}
		

	printf("Done !\n");
}

void Remove_Small_Terms_and_DAG()
{

	printf("Remove Small Terms and DAG ... ");

	for (int i = 0; i < MaxONTterms; i++)
		Ont[i].flag = 0;

	for (int i = 0; i < MaxONTterms; i++)
		if (Ont[i].type != 'E')
		{
			IntArray children = IntArrayNew();
			for (int j = 0; j < Ont[i].child->len; j++)
			{
				int c = Ont[i].child->data[j];
				if (Ont[c].flag || ((Ont[c].gene->len < Min_Size_GS)
						&& (Ont[c].i_gene->len < Min_Size_GS)))
				{
					Ont[c].flag = 1;
					continue;
				}
				SetAdd(children, c);
				Ont[c].flag = 1;
			}
			IntArrayFree(Ont[i].child);
			Ont[i].child = children;
		}

	printf("Done !\n");
}


void write_progress(int number)
{
	//char fname[1000];
	//strcpy(fname, BaseName);
	//strcat(fname, ".progress");
	FILE *dat = fopen(BaseName, "w");
	fprintf(dat, "%d", number);
	fclose(dat);
}


void increase_progress(float incr)
{
	float p;
	FILE * dat;

	dat = fopen(BaseName, "r");
	fscanf(dat, "%f", &p);
	fclose(dat);

	dat = fopen(BaseName, "w");
	fprintf(dat, "%f", p+incr);
	//fprintf(stderr, "-->%f  ", p+incr);
	fclose(dat);
}


void input_report()
{
	char fname[1000];
	FILE *report;

	sprintf(fname, "%s.input", BaseName);
	report = fopen(fname, "w");

	fprintf(report, "Project: %s\n\n", project_name);

	//fprintf(report, "BaseName=%s\n", BaseName);
	//fprintf(report, "DB_dir=%s\n", DB_dir);
	//fprintf(report, "Project=%s\n", project_name);
	fprintf(report, "Func=%d\n", include_ont[0]);
	fprintf(report, "Proc=%d\n", include_ont[1]);
	fprintf(report, "Comp=%d\n", include_ont[2]);
	fprintf(report, "KEGG=%d\n", include_ont[3]);
	fprintf(report, "Interactions=%d\n", MaxInterTerms);
	fprintf(report, "DE genes=%d\n", Cutoff);
	fprintf(report, "Min_Size_GS=%d\n", Min_Size_GS);
	//fprintf(report, "MaxNumTerms=%d\n", MaxNumTerms);
	//fprintf(report, "GSEA_Factor=%d\n", GSEA_Factor);
	//fprintf(report, "NumberIterations=%d\n", NumberIterations);
	fprintf(report, "PrintTopGS=%d\n", PrintTopGS);
	fprintf(report, "P_Value=%lf\n", P_Value);
	fprintf(report, "W_fisher=%lf\n", W_fisher);
	fprintf(report, "W_gsea=%lf\n", W_gsea);
	fprintf(report, "W_page=%lf\n", W_page);
	//fprintf(report, "randomize=%d\n\n", randomizeRandGen);
	fprintf(report, "RandSeed=%d\n\n", randomSeed);

	fprintf(report, "Number of genes in the input file =%d\n", input.file_n);
	fprintf(report, "Number of genes found in ENTREZ   =%d\n", input.n);

	printf("\nBaseName=%s\n", BaseName);
	printf("DB_dir=%s\n", DB_dir);
	printf("Project=%s\n", project_name);
	printf("Func=%d\n", include_ont[0]);
	printf("Proc=%d\n", include_ont[1]);
	printf("Comp=%d\n", include_ont[2]);
	printf("KEGG=%d\n", include_ont[3]);
	printf("MaxInterTerms=%d\n", MaxInterTerms);
	printf("Summarization=%d\n", Summarization);
	printf("Minimum=%d\n", Minimum);
	printf("Cutoff=%d\n", Cutoff);
	printf("Min_Size_GS=%d\n", Min_Size_GS);
	printf("MaxNumTerms=%d\n", MaxNumTerms);
	printf("GSEA_Factor=%d\n", GSEA_Factor);
	printf("NumberIterations=%d\n", NumberIterations);
	printf("PrintTopGS=%d\n", PrintTopGS);
	printf("P_Value=%lf\n", P_Value);
	printf("W_fisher=%lf\n", W_fisher);
	printf("W_gsea=%lf\n", W_gsea);
	printf("W_page=%lf\n", W_page);
	//printf("randomize=%d\n\n", randomizeRandGen);
	printf("RandSeed=%d\n\n", randomSeed);


	if (input.gene->len != input.sorted->len)
	{
		fprintf(report, "\nERROR: Input gene list has duplicate genes !!!\n");
		fclose(report);
		exit(1);
	}

	if (include_ont[0] + include_ont[1] + include_ont[2] + include_ont[3] < 1)
	{
		fprintf(report, "\nERROR: Please select at least one ontology !!!\n");
		fclose(report);
		exit(1);
	}

	fclose(report);
}
