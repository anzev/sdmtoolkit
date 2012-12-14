# -*- coding: utf-8 -*-
"""
Script to convert the given data set to a list of Prolog facts compatible with RSD.

@author Anže Vavpetič, 2010 <anze.vavpetic@ijs.si>
"""
import sys
from orange import ExampleTable
from OWL2XLogger import logger

def main():
    if len(sys.argv) < 2:
        logger.error("Too few arguments. Usage: python ex2rsd.py <dataset>.tab <outFile>.pl")
    
    # Get the dataset's path
    try:
        logger.debug("Data set: % s" % sys.argv[1])
        data = ExampleTable(sys.argv[1])
    except:
        logger.error("Couldn't read the data set!")
    
    # Get the output file name.
    try:
        logger.debug("Out file: % s" % sys.argv[2])
        out = open("%s" % sys.argv[2], 'w')
    except:
        logger.error("Couldn't create the out file: %s" % sys.argv[2])
    
    clVar = data.domain.classVar.name
    for ex in data:
        first = True   # Just for proper comma handling.
        terms = ""
        for attrVal in filter(lambda x: x.variable.name != clVar, ex):
            #terms = terms + "%s\"%s\"" % ("" if first else ", ", attrVal.value)
            terms = terms + "%s%s" % ("" if first else ", ", attrVal.value.lower())
            if first:
                first = False
        #print "individual(%s, [%s])." % (ex.getclass().value.lower(), terms)
        out.write("individual(%s, [%s]).\n" % (ex.getclass().value.lower(), terms))
    
    out.close()
        
if __name__ == '__main__':
    main()