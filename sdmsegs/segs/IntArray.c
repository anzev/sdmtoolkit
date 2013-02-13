#include<stdio.h>
#include<math.h>
#include<stdlib.h>

#include "def_var.h"


IntArray IntArrayNew(){
	IntArray x;
	x = (IntArray)malloc(sizeof(struct TIntArray));
	x->len = 0;
	x->allocated = InitLength;
	x->data = (int *)malloc(InitLength*sizeof(int));
	return x;
}

void IntArrayFree(IntArray x) {
	free(x->data);
	free(x);
}

void AddInt(IntArray x, int y) {
	if (x->len < x->allocated)
			x->data[x->len++] = y;
	else {
		int len = x->len*2;
		int *data = (int *)malloc(len*sizeof(int));
		for(int i=0;i<x->len;i++)
			data[i] = x->data[i];
		x->allocated = len;
		free(x->data);
		x->data = data;
		AddInt(x, y);
	}
}

int FindInt(IntArray x, int y) {
	int low = 0, high = x->len - 1, mid;
	while (low <= high) {
		mid = (low + high) >> 1;
		if (x->data[mid] > y)
			high = mid - 1;
		else
		{
			if (x->data[mid] < y)
				low = mid + 1;
			else
				return mid;
		}
	}
	return -1;
}

void AddIntSort(IntArray x, int y) {

	AddInt(x, y);

	int i = x->len - 1;
	while((i > 0) && (x->data[i-1] > y)) {
		x->data[i] = x->data[i-1];
		i--;
	}
	x->data[i] = y;
}

IntArray IntArrayMerge(IntArray list1, IntArray list2) {
	IntArray x = IntArrayNew();
	int i=0, j=0;
	while((i<list1->len) && (j<list2->len))
		if (list1->data[i] < list2->data[j])
			AddInt(x, list1->data[i++]);
		else
			AddInt(x, list2->data[j++]);
	while(i<list1->len) AddInt(x, list1->data[i++]);
	while(j<list2->len) AddInt(x, list2->data[j++]);

	return x;
}

void SetAdd(IntArray x, int y) {
	/*
	fprintf(stderr, "--%d [?%d]\n", x->len, y);
	if (x->len <= 10)
	{
		fprintf(stderr, "[");
		for (int i=0; i<x->len; i++)
			fprintf(stderr, "%d,", x->data[i]);
		fprintf(stderr, "]\n");
	}
	*/
	if(FindInt(x, y) != -1)
		return;
	AddIntSort(x, y);
}

IntArray SetIntsec(IntArray list1, IntArray list2) {
	IntArray out = IntArrayNew(), tmp;
	int i, j;
	i=j=0;

	if(list1->len > list2->len) {
		tmp = list1;
		list1 = list2;
		list2 = tmp;
	}

	if(list1->len * list1->len < 2*list2->len) {
		for(i = 0; i < list1->len; i++) {
			j = list1->data[i];
			if(FindInt(list2, j) != -1) AddInt(out, j);
		}
	}
	else
		while((i<list1->len) && (j<list2->len))
			if (list1->data[i] < list2->data[j]) i++; else
			if (list1->data[i] > list2->data[j]) j++; else {
				AddInt(out, list1->data[i]);
				i++; j++;
			}
	return out;
}


IntArray SetUnion(IntArray list1, IntArray list2) {
	IntArray out = IntArrayNew();
	int i=0, j=0;
	while((i<list1->len) && (j<list2->len))
		if (list1->data[i] < list2->data[j]) AddInt(out, list1->data[i++]); else
		if (list1->data[i] > list2->data[j]) AddInt(out, list2->data[j++]); else {
			AddInt(out, list1->data[i]);
			i++; j++;
		}
	while(i<list1->len) AddInt(out, list1->data[i++]);
	while(j<list2->len) AddInt(out, list2->data[j++]);

	return out;
}

int SetEqual(IntArray x, IntArray y) {
  if(x->len != y->len) return 0;
  for(int i = 0; i < x->len; i++)
    if(x->data[i] != y->data[i]) return 0;
  return 1;
}

IntArray IntArrayCopy(IntArray list) {
	IntArray x = (IntArray)malloc(sizeof(struct TIntArray));
	x->len = list->len;
	x->allocated = list->len;
	x->data = (int *)malloc(x->allocated*sizeof(int));
	for(int i = 0; i < x->len; i++)
		x->data[i] = list->data[i];
	return x;
}

void IntArrayPrint(IntArray list) {
	printf("Length = %d\n Data = [", list->len);
	for(int i = 0; i < list->len; i++)
		printf(" %d", list->data[i]);
	printf("]\n");
}

int SimilarSets(IntArray set1, IntArray set2) {
  int len1 = set1->len, len2 = set2->len, len_comm;
  double max = len1;
  if(len1 < len2) max = len2;

  if(abs(len1 - len2) / max > 0.1) return 0;

  IntArray common = SetIntsec(set1, set2);
  len_comm = common->len;
  IntArrayFree(common);

  if(len_comm / max < 0.9) return 0;

  return 1;
}
