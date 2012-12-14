# -*- coding: utf-8 -*-
"""
Script to convert the given data set to a list of SEGS examples.

@author Anže Vavpetič, 2010 <anze.vavpetic@ijs.si>
"""
import sys
import os.path
from orange import ExampleTable
from OWL2XLogger import logger

# Import the generated dictionary
from segsDump import segsMap

# Reported terms (so we don't spam on stdout)
reported = set()
map_available = True


# ID generator.
def getID():
    i = 0
    while True:
        i = i + 1
        yield i

idGen = getID()

def main():
    global map_available    
    
    if len(sys.argv) < 4:
        logger.error("Too few arguments. Usage: python ex2segs.py <dataset>.tab <outFile> <positiveClass> <map, yes or no>")
    
    # Get the dataset's path
    try:
        logger.debug("Data set: % s" % sys.argv[1])
        data = ExampleTable(sys.argv[1])
    except:
        logger.error("Couldn't read the data set!")
    
    # Get the output file name.
    try:
        logger.debug("Out file: % s" % sys.argv[2])
        out = open(sys.argv[2], 'w')
    except:
        logger.error("Couldn't create the out file: %s" % sys.argv[2])
    
    # Get the positive class name.
    logger.debug("Positive class: % s" % sys.argv[3])
    posClass = sys.argv[3]
    if posClass not in data.domain.classVar.values:
        logger.error("The specified value for the positive class is undefined.")
    
    map_available = sys.argv[4].lower() == "yes"
        
    basename = os.path.basename(sys.argv[1]).split('.')[0]
    outDir = os.path.dirname(sys.argv[2])
    
    # Create the csv file.
    csv = open(os.path.normpath('%s/%s.csv') % (outDir,basename), 'w')
    logger.debug('csv path: %s' % os.path.normpath('%s/%s.csv') % (outDir,basename))
    
    # Sort by class values.
    data.sort(data.domain.classVar)
    
    # Convert to SEGS file.
    # First write the positive examples.
    pos = data.filter({data.domain.classVar : posClass})
    neg = data.filter({data.domain.classVar : posClass}, negate=1)
    ratio = 0.5
    
    for ex in pos:
        writeExample(data, out, csv, ex, ratio)
    # Then write all other examples.
    for ex in neg:
        writeExample(data, out, csv, ex, ratio)
    # Tidy up.
    out.flush()
    out.close()
    csv.flush()
    csv.close()
    
    out = open(sys.argv[2], 'r')
    out2 = open('g2ont', 'w')
    
    out2.write(out.read())
    out2.close()
    out.close()
    
    logger.debug(open(os.path.normpath('%s/%s.csv') % (outDir,basename), 'r').read())
    
    # Remember some info about the data set. This can be later used for processing the SEGS results.
    # Deprecated! This isn't used anymore.
    dataInfo = open('scripts/dataInfo.py', 'a')
    dataInfo.write('posClass = "%s=%s"\n' % (data.domain.classVar.name, posClass))
    dataInfo.close()
    
def writeExample(data, out, csv, ex, ratio):
    """
    Writes an example to the file.
    """
    global reported
    global idGen
    
    #out.write("[%d, [" % ex['id'])
    
    exID = idGen.next()
    out.write("[%d, [" % exID)
    first = True
    for att in ex.domain:
        # Skip class.
        if att == data.domain.classVar:
            continue
        # Retrieve GO code for the attribute value.
        if map_available:
            goCode = segsMap.get(ex[att].value, None)
        elif ex[att].value != 'No':    # Otherwise use the att value
            goCode = ex[att].value 
            #print "map not available using goCode = %s" % goCode
        else:
            goCode = None
            
        if goCode:
            if not first:
                out.write(", ")
            first = False
            out.write("'%s'" % goCode)
        else:
            term = str(ex[att])
            if term not in reported:
                logger.warning('No definition for term "%s" could be found, skipping.' % term)
                reported.add(term)
    out.write("]]\n")
    
    #csv.write('%d, %f\n' % (ex['id'], ratio))
    csv.write('%d, %f\n' % (exID, ratio))

if __name__ == '__main__':
    main()