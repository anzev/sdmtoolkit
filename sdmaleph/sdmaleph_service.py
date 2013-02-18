# -*- coding: utf-8 -*-
"""
SDM-Aleph server.

@author: Anže Vavpetič, 2013 <anze.vavpetic@ijs.si>
"""
import sys
import json
import uuid
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer

sys.path.append('..')
from owl2x import OWL2X
from utils import StructuredFormat
from aleph import Aleph

# Default settings for SDM
defaults = {
    'mode' : 'induce_cover',
    'clauselength' : 4,
    'minpos' : 1,
    'noise' : 1,
    'evalfn' : 'wracc'    
}

def sdmaleph_runner(examples, mapping, ontologies=[], posClassVal=None, cutoff=None, relations=[],
        minPos=defaults['minpos'], noise=defaults['noise'], clauseLen=defaults['clauselength'], dataFormat='tab'):
    """
    SDM-Aleph web service.
    
    Inputs:
        - examples: str, a .tab dataset or a list of pairs
        - mapping : str, a mapping between examples and ontological terms,
        - ontologies : a list of {'ontology' : str} dicts
        - relations : a list of {'relation' : str} dicts
        - posClassVal : str, if the data is class-labeled, this is the target class,
        - cutoff : int, if the data is ranked, this is the cutoff value for splitting it into two classes,
        - minPos : int >= 1, minimum number of true positives per rule
        - noise : int > 0, false positives allowed per rule
        - clauseLen : int >= 1, number of predicates per clause,
        - dataFormat : str, legal values are 'tab' or 'list'
    Output:
        - str, the induced theory.
    
    @author: Anze Vavpetic, 2011 <anze.vavpetic@ijs.si>
    """
    examples = StructuredFormat.parseInput(examples, dataFormat)
    mapping = StructuredFormat.parseMapping(mapping)
    relations = StructuredFormat.parseRelations(relations)
    pos, neg = [],[]
    if posClassVal:
        for id, val in examples:
            if val==posClassVal:
                pos.append((id, val))
            else:
                neg.append((id, val))
    elif cutoff:
        pos, neg = examples[:cutoff], examples[cutoff:]
    else:
        raise Exception('You must specify either the cutoff or the positive class value.')
    posEx, negEx, b = OWL2X.get_aleph_input([ont['ontology'] for ont in ontologies], mapping, [rel['relation'] for rel in relations], pos, neg)
    filestem = str(uuid.uuid4())
    runner = Aleph()
    # Set parameters
    for setting, val in defaults.items():
       runner.set(setting, val)
    if minPos >= 1:
       runner.set('minpos', minPos)
    else:
        raise Exception('minPos must be >= 1.')
    if noise >= 0:
       runner.set('noise', noise)
    else:
        raise Exception('noise must be >= 0.')
    if clauseLen >= 1:
        runner.set('clauselength', clauseLen)
    else:
        raise Exception('clauseLen must be >= 1.')
    # Set eval script
    #runner.setPostScript("toPython('rulesdump.py')", open('topy.pl').read())
    str_rules = runner.induce(defaults['mode'], posEx, negEx, b, filestem=filestem)
    # Read rules
    #sys.path.append(Aleph.DIR)
    #result = __conv(__import__('rulesdump').rules, pos, neg)
    #sys.path.pop()
    return str_rules

def __conv(rules, pos, neg):
    """
    Computes the covered positives examples for the given rules.
    """
    N, posEx = float(len(pos + neg)), len(pos)
    def wracc(r):
        return len(r['covered'])/N * (len(r['posCovered'])/float(len(r['covered'])) - posEx/N)         
    i = 0
    all_positives = set(map(lambda ex: int(ex[0]), pos))
    for r in rules:
        r['covered'] = map(lambda x: x['id'], r['covered'])
        r['posCovered'] = list(all_positives.intersection(r['covered']))
        r['wracc'] = wracc(r)
    return rules
