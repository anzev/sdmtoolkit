CC = gcc
FLAGS = -O3 -Wall -std=gnu99 -fPIC -fopenmp
SHARED = -shared
LINKS = -lm -lgomp
DELETE = rm -f
COPY = cp
PYTHON = python

INCLUDEPYTHON = -I/usr/include/python2.6
#INSTALLDIR = /usr/lib/python2.5/site-packages

MOD_LIB = segs.so
HEADER = def_var.h
ALL_OBJECTS = run.o enrichment.o geneset.o parse.o procs.o IntArray.o

TESTING_DIR = ../testing


all: clean segs
new: clean segs install

segs: 	$(ALL_OBJECTS)
	$(CC) $(LINKS) $(SHARED) $(ALL_OBJECTS) -o $(MOD_LIB) 

run.o:	run.c $(HEADER)
	$(CC) $(FLAGS) -c run.c
	
enrichment.o:	enrichment.c $(HEADER)
	$(CC) $(FLAGS) -c enrichment.c

geneset.o:	geneset.c $(HEADER)
	$(CC) $(FLAGS) -c geneset.c

parse.o:	parse.c $(HEADER)
	$(CC) $(FLAGS) -c parse.c
	
procs.o:	procs.c $(HEADER)
	$(CC) $(FLAGS) -c procs.c
	
IntArray.o:	IntArray.c $(HEADER)
	$(CC) $(FLAGS) -c IntArray.c


install:
	$(COPY) $(MOD_LIB) /home/anzev/programiranje/ws/WebServices/gSEGS_service_v2/
	#$(COPY) $(MOD_LIB) ../testing
	#$(COPY) $(MOD_LIB) ../testing_plants
	
#remove:
#	$(DELETE) $(INSTALLDIR)/$(MOD_LIB)	

clean:
	$(DELETE) $(MOD_LIB) $(ALL_OBJECTS)
	$(DELETE) ../testing/$(MOD_LIB)
	$(DELETE) -r ../testing/results/*
#$(DELETE) work_dir/*.genelist work_dir/*.html work_dir/*.progress work_dir/*.sets work_dir/*.input

	
test:	all install
	$(DELETE) -r ../testing/results/*
	cd ../testing; \
	$(PYTHON) pySEGS.py	
	
	
plantTest:	all install
	$(DELETE) -r ../testing_plants/results/*
	cd ../testing_plants; \
	$(PYTHON) pySEGS.py	

	
	
	
	