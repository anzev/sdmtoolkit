#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<time.h>
#include<math.h>
#include<omp.h>


#define ALL_GENES_KEY "allGenes"
#define TOP_GENES_KEY "topGenes"
#define TERMS_KEY "terms"
#define CLASS_A "A"
#define CLASS_B "B"
#define FISHER_NAME "fisher"
#define GSEA_NAME "gsea"
#define PAGE_NAME "page"
#define ALL_NAME "all"
#define SCORES "scores"

#define FISHER_PVAL "fisher_p"
#define UNADJUSTED_PVAL "unadjusted_p"

#define GSEA_PVAL "gsea_p"
#define ENRICHMENT_SCORE "enrichment_score"

#define PAGE_PVAL "page_p"
#define Z_SCORE "z_score"

#define AGGREGATE_PVAL "aggregate_p"


// this is used to disable file output
#define WRITE_FILES 0


#define GO_PREFIX_OFFSET 3
#define KEGG_PREFIX_OFFSET 5
#define GO_TERM_NCIPHERS 7
#define KEGG_TERM_NCIPHERS 5


// g-SEGS mode
#define GSEGS  1


// CONSTANTS
#define MaxONTterms   2010000    // Maximum number of Ontological Terms
#define PrintInterval 100000    // Print interval when generating genesets
#define MAX_ITERATIONS 10000    // Maximum number of iterations
#define LINUX              1    // platform, LINUX 1, WINDOWS 0

#define InitLength 16


// Added by A.V.
#define UNDEF  0.0   // This is used in computing example weights for WRAcc; covered examples do not contribute.
#define TRUE   1
#define FALSE  0
#define WRACC_NAME  "WRAcc"
#define WRACC_SCORE "wracc"

struct TIntArray {
	int len, allocated;
	int *data;
};

typedef struct TIntArray *IntArray;


int lastGO;                     // largest ID of a GO term

struct TOnt {                   // ontological term
	char flag;                    // used for various needs
	char type; 				            // [F]unc, [P]rocess, [C]omponent, [K]egg path, [E]mpty
	char level;                   // on which level in the DAG is the node
	char general;                 // is the term to general
	char *name;                   // string
	IntArray parent, child;       // parent, child nodes
	IntArray gene, i_gene;        // genes annotated by this term, genes interacting with this term
	IntArray more_general;        // more general GO terms
};


struct TOnt Ont[MaxONTterms];	  // ontological term
IntArray gIds;                  // real gene ID's in ENTREZ
IntArray *g2g, *g2ont;          // gene to gene, and gene to ontology annotations

struct TInput {
	int n, file_n;			          // number of genes analyzed, and in the file
	IntArray gene;				        // genes translated ID's
	IntArray original;            // original list of genes
	IntArray sorted;              // sorted gene id's
	double *weight;				        // genes weights
	double mean, sd;              // mean and standard deviation of weight
};

struct TInput input;            // input to be analyzed
struct TInput input1;


int root_F, root_P;             // root ID's od the four ontologies
int root_C, root_K;
int root[4];

struct TGeneSet {   			      // gene set                |
	int term[4]; 	                // which terms             | if term[0] = 'binding' and inter[0] = 1 then
	int inter[4];                 // with interaction or not |      gene set = int(binding)

	IntArray top_gene;            // gene members above the cutoff
	IntArray gene;                // all gene members

	char flag;                    // flag used for various purposes

	double fisher;                // fisher exact test score
	double gsea;                  // gene set enrichment analysis
	double page;                  // parametric gene expression analysis

	// Added by A.V. 
	double wracc;		      // The wracc score of a "GS"
	int used;		      // Has the rule already been selected?

	double p_fisher;              // experimental p value by fisher test
	double p_gsea;                // experimental p value by gsea algorithm
	double p_page;                // experimental p value by page algorithm
	double p_agregate;
};
typedef struct TGeneSet *GeneSet;

struct TListGeneSet {           // dynamic list of gene sets
	int len, allocated;           // length and allocated gene set pointers
	GeneSet *set;                 // list of gene sets pointers
};
typedef struct TListGeneSet *PListGS;
//PListGS Results;

int Minimum;                    // All gene set candidates must have Minimum number of DE genes
int Cutoff;                     // The threshold (as position, or number of genes) for separating DE genes and the rest
int Min_Size_GS;                // Minimum size of a gene set
int MaxNumTerms;                // Maximum number of terms that define gene set
int MaxInterTerms;              // Maximum number of interacting terms
int GSEA_Factor;                // portion of genes used for calculating GSEA. The first (1/GSEA_factor) * N genes
int NumberIterations;           // Number of iterations for experimental p-values
int PrintTopGS;                 // Print Best PrintTop genesets

// Wracc parameters. Added by A.V.
int wracc_k;			// How many times can an example be covered

//int CurrNumTerms;               // global variable for controling num terms.
double P_Value;                 // threshold p_value
double W_fisher;                // weight of fisher test for combining the tests
double W_gsea;
double W_page;

char BaseName[1000];            // base file name of the input data
char DB_dir[1000];              // directory where ontologies and other files are located
char project_name[1000];        // Name of the user project
int  include_ont[4];            // bool variables for incluson of parts of ontology
int general_level[4];           // The level where the relevant concepts begin for each of the 4 ontologies
int Summarization;              // bool variable for choosing Summarization


int randomSeed;					// this variable holds the random seed (if set, else -1)


