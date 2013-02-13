#include <math.h>

#include "def_var.h"


double fisher(int N, int M, int K, int x) {
	double sn11,sn1_,sn_1,sn,sprob;
	double sleft,sright,sless,slarg;

	double lngamm(double z) {
	  double x = 0;
	  x += 0.1659470187408462e-06/(z+7);
	  x += 0.9934937113930748e-05/(z+6);
	  x -= 0.1385710331296526    /(z+5);
	  x += 12.50734324009056     /(z+4);
	  x -= 176.6150291498386     /(z+3);
	  x += 771.3234287757674     /(z+2);
	  x -= 1259.139216722289     /(z+1);
	  x += 676.5203681218835     /(z);
	  x += 0.9999999999995183;
	  return log(x) - 5.58106146679532777 - z + (z - 0.5) * log(z + 6.5);
	}

	double lnfact(double n) {
	  if(n <= 1) return(0);
	  return lngamm(n+1);
	}

	double lnbico(double n, double k) {
	  return lnfact(n)-lnfact(k)-lnfact(n-k);
	}

	double hyper_323(int n11, int n1_, int n_1, int n) {
	  return exp( lnbico(n1_ , n11) + lnbico(n - n1_, n_1 - n11) - lnbico(n, n_1) );
	}

	double hyper(int n11i, int n1_i, int n_1i,int ni) {
		if(!(n1_i|n_1i|ni)) {
			if(!(n11i % 10 == 0)) {
				if(n11i==sn11+1) {
					sprob *= ((sn1_-sn11)/(n11i))*((sn_1-sn11)/(n11i+sn-sn1_-sn_1));
					sn11 = n11i;
					return sprob;
	      	}
		      if(n11i==sn11-1) {
		      	sprob *= ((sn11)/(sn1_-n11i))*((sn11+sn-sn1_-sn_1)/(sn_1-n11i));
		      	sn11 = n11i;
		      	return sprob;
		      }
	    	}
	    	sn11 = n11i;
	  } else {
	  		sn11 = n11i;
	    	sn1_=n1_i;
	    	sn_1=n_1i;
	    	sn=ni;
	  }
	  sprob = hyper_323(sn11,sn1_,sn_1,sn);
	  return sprob;
	}

	double fisher_exact_c(int n, int n1_, int n_1, int n11) {
		int i, j, max, min;
		double p, prob;
		max=n1_;


		//fprintf(stderr, "Fisher: %d, %d, %d, %d\n", n, n1_, n_1, n11);

		if(n_1 < max) max = n_1;

		min = n1_ + n_1 - n;
		if(min < 0) min = 0;

		if(min == max) {
			sless = 1;
			sright= 1;
			sleft = 1;
			slarg = 1;
			return 1;
		}

		prob = hyper(n11, n1_, n_1, n);
		sleft=0;
		p = hyper(min, 0, 0, 0);
		for(i=min+1; p<0.99999999*prob; i++) {
			sleft += p;
			p=hyper(i, 0, 0, 0);
		}
		i--;
		if(p < 1.00000001 * prob) sleft += p;
		else i--;
		sright = 0;
		p = hyper(max, 0, 0, 0);
		for(j = max - 1; p < 0.99999999*prob; j--) {
			sright += p;
			p = hyper(j, 0, 0, 0);
		}
		j++;
		if(p < 1.00000001 * prob) sright += p;
		else j++;
		if(fabs(i - n11) < fabs(j-n11)) {
			sless = sleft;
			slarg = 1 - sleft + prob;
		} else {
			sless = 1 - sright + prob;
			slarg = sright;
		}
		return slarg;
	}

	return fisher_exact_c(N, M, K, x);
}

double gsea(IntArray all, int *pos_gene, IntArray set, double *w, double *wbl) {
    int i;
    double partial, ps1, ps2, max_diff;

    max_diff = -1000;

    ps1 = 1.0 / set->len;
    ps2 = 1.0 / (all->len - set->len);

    for(i = 0;i < all->len / GSEA_Factor; i++)
        wbl[i] = -ps2;//*fabs(w[i]);

    for(i = 0;i < set->len; i++)
        wbl[pos_gene[set->data[i]]] = ps1;//*fabs(w[pos_gene[set->data[i]]]);

    partial = 0;
    for(i = 0; i < all->len / GSEA_Factor; i++) {
        partial += wbl[i];
        if(partial > max_diff)
            max_diff = partial;
    }

    return max_diff;
}


//page(input_iter[iteration].gene, pos_gene, gs->gene, input_iter[iteration].weight, input_iter[iteration].mean, input.sd)

double page(IntArray all, int *pos_gene, IntArray set, double *w, double mean, double sd) {
    double sum = 0;
    int pos;
    for(int i = 0; i < set->len; i++) {
        pos = pos_gene[set->data[i]];
        sum += w[pos];
        //if(print) printf("%d ", pos);
    }
    //if(print) printf("\n");
    sum /= set->len;
    return ((sum - mean) * sqrt(set->len)) / sd;
}

/**
 * Calculates the wracc score for the given rule and the given example weights.
 */
double wracc(double *weight, GeneSet rule, int* pos_gene) 
{
    // Compute n(Y)/N; which is constant
    double prior = Cutoff / (double) input.n;
    
    // Compute N'
    double np = 0;
    for (int i = 0; i < input.n; i++)
	np += weight[i];
    
    // Compute n'(X)
    double npX = 0;
    for (int j = 0; j < rule->gene->len; j++) {
        if (rule->gene->data[j] > gIds->len)
 	  printf("N=%d, j=%d\n", gIds->len, rule->gene->data[j]);
	//npX += weight[rule->gene->data[j]];
       npX += weight[pos_gene[rule->gene->data[j]]];
    }
    
    // Compute n'(XY)
    double npXY = 0;
    for (int j = 0; j < rule->top_gene->len; j++) {
        if (rule->top_gene->data[j] > gIds->len)
          printf("N=%d, j=%d\n", gIds->len, rule->top_gene->data[j]);
      //if (rule->top_gene->data[j] > input.n)
	 //printf("N=%d, j=%d\n", input.n, rule->top_gene->data[j]);
	//npXY += weight[rule->top_gene->data[j]];
      npXY += weight[pos_gene[rule->top_gene->data[j]]];
    }
    
    double score = npX / np * (npXY / npX - prior);
    
    return score;
    //return 0;
}

/**
 * Main procedure for finding the currently best rule according to WRAcc.
 * 
 * Added by Anze Vavpetic, 2010 <anze.vavpetic@ijs.si>
 */
GeneSet best_wracc(double *weight, PListGS rules, int *pos_gene) 
{
    GeneSet best = NULL;
    double bestScore = 0;
    
    // Compute n(Y)/N; which is constant
//     double prior = Cutoff / (double) input.n;
//     
//     // Compute N'
//     double np = 0;
//     for (int i = 0; i < input.n; i++)
// 	np += weight[i];
    
    for (int i = 0; i < rules->len; i++)
    {
        GeneSet rule = rules->set[i];
	
	// Skip already used rules.
	if (rule->used == TRUE) 
	  continue;
	
	// Compute n'(X)
// 	double npX = 0;
// 	for (int j = 0; j < rule->gene->len; j++)
// 	    npX += weight[rule->gene->data[j]];
// 	
// 	// Compute n'(XY)
// 	double npXY = 0;
// 	for (int j = 0; j < rule->top_gene->len; j++)
// 	    npXY += weight[rule->top_gene->data[j]];
	
// 	double score = npX / np * (npXY / npX - prior);
	
	double score = wracc(weight, rule, pos_gene);
	
	//printf("score=%f, npX=%f, np=%f, npXY=%f\n", score, npX, np, npXY);
	
	if (score > bestScore) {
	    best = rule;
	    bestScore = score;
	}
    }
 
    if (best != NULL)
      best->wracc = bestScore;
    
    return best;
}
