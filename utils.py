'''
Module for various utilities.

@author: Anze Vavpetic, 2012
'''
import logging
import tempfile
import orange
import StringIO
import json

DEBUG = False

# Setup a logger
logger = logging.getLogger("sdmtoolkit [Python]")
#logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(name)s %(levelname)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

class StructuredFormat:
    '''
    Parse various formats to structured python objects.
    '''
    # Possible formats of input data
    FORMAT_LIST = 'list'
    FORMAT_TAB = 'tab'
    
    @staticmethod
    def parseInput(inputData, format):
        '''
        Parse input data to a structured, list format.
        '''
        inputFile = StructuredFormat.tempName(inputData, suf='.tab')
        dataAsList = []
        if format == StructuredFormat.FORMAT_TAB:
            data = orange.ExampleTable(inputFile)
            for i, ex in enumerate(data):
                dataAsList.append((i, ex[data.domain.classVar].value))
        elif format == StructuredFormat.FORMAT_LIST: # List of pairs
            dataAsList = json.loads(inputData)  
        else:
            logger.error('Unspecified input data format.')
        return dataAsList
        
    @staticmethod
    def parseInteractions(interactions):
        interactionsAsList = []
        for line in StringIO.StringIO(interactions):
            pyLine = json.loads(line)
            id1 = pyLine[0]
            for id2 in pyLine[1]:
                interactionsAsList.append((int(id1), int(id2)))
        return interactionsAsList
    
    @staticmethod
    def parseRelations(relations):
        relations_list = []
        for relation in relations:
            relation_list = []
            for line in StringIO.StringIO(relation):
                pyLine = json.loads(line)
                id1 = pyLine[0]
                for id2 in pyLine[1]:
                    relation_list.append((int(id1), int(id2)))
            relations_list.append(relation_list)
        return relations_list


    @staticmethod
    def parseMapping(mapping):
        mappingAsList = []
        for line in StringIO.StringIO(mapping):
            pyLine = json.loads(line)
            mappingAsList.append((pyLine[0], pyLine[1]))
        return mappingAsList
    
    @staticmethod
    def parseGeneralTerms(gt):
        gtAsList = []
        for line in StringIO.StringIO(gt):
            gtAsList.append(line)
        return gtAsList
    
    @staticmethod
    def tempName(text, suf=''):
        '''
        Writes the text to a temporary named file and returns its full path.
        '''
        f = tempfile.NamedTemporaryFile(suffix=suf,delete=False)
        f.write(text)
        f.flush()
        name = f.name
        return name
