# -*- coding: utf-8 -*-
"""
SDM-Aleph server.

@author: Anže Vavpetič, 2011 <anze.vavpetic@ijs.si>
"""
#from webServices.serverBase import Server
#from webServices.common import cmdlServer
#
#import sdmaleph_service as sdm_aleph
#
#if __name__ == "__main__":
#    logFname, port = cmdlServer()
#
#    SERVICE_MODULES = [sdm_aleph]
#    SERVICE_LIST = [x.getService(newPort=port) for x in SERVICE_MODULES]
#    srv = Server(SERVICE_LIST, logFname, port)
#    srv.serveForever()

from aleph import Aleph

# Keyword defines
JOB_ID = 'jobID'
PROGRESS_FNAME = 'progressFname'
BK = 'bk'
POS = 'pos'
NEG = 'neg'
MIN_SET_SIZE = 'minimalSetSize'
MAX_NUM_TERMS = 'maxNumTerms'
MODE = 'mode'
CACHING = 'caching'
CLAUSE_LEN = 'clauselength'
LANG = 'language'
NOISE = 'noise'
SEARCH = 'search'
OPENLIST = 'openlist'
EVAL = 'eval'

# SDM-Aleph defaults
defaults = {
    MIN_SET_SIZE : 15,
    MAX_NUM_TERMS : 4,
}

# Fixed settings for SDM
aleph_settings = {
    MODE : 'induce_cover',
    CACHING : 'true',
    CLAUSE_LEN : 4,
    LANG : 1,
    NOISE : 15,
    SEARCH : 'heuristic',
    OPENLIST : 25,
    EVAL : 'wracc'    
}

def aleph_runner(dataset, ontologies, mapping, relations=[], cutoff=None, minSetSize=defaults[MIN_SET_SIZE]):
    posEx, negEx, b = OWL2X.get_aleph_input(keys['ontologies'], keys['mapping'], keys['relations'], keys['pos'], keys['neg'])        
    filestem = keys[JOB_ID]
    runner = Aleph()
    # Set parameters
    for setting, val in aleph_settings.items():
        runner.set(setting, val)
    # Set eval script
    runner.setPostScript("toPython('rulesdump.py')", open('topy.pl').read())
    str_rules = runner.induce(aleph_settings[MODE], filestem, posEx, negEx, b)
    
    # Read rules
    sys.path.append(Aleph.DIR)
    result = self.__conv(__import__('rulesdump').rules, keys['pos'], keys['neg'])
    sys.path.pop()