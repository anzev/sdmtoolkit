# -*- coding: utf-8 -*-
"""
SDM-SEGS server.

@author: Anže Vavpetič, 2012 <anze.vavpetic@ijs.si>
"""
import sys
import json
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer

from sdmsegs import gsegs

def sdmsegs_runner(**kwargs):
    """
    SDM-SEGS web service.
    
    Inputs:
        - inputData: str, a .tab dataset or a (pythonish) list of pairs
        - interactions: str, list of interacting examples,
        - mapping : str, a mapping between examples and ontological terms,
        - ont1-4 : str, ontologies in OWL (legacy=false), or in SEGS's format (legacy=true)
        - generalTerms : str, terms that are too general (each in new line),
        - legacy : bool, turns on SEGS mode,
        - posClassVal : str, if the data is class-labeled, this is the target class,
        - cutoff : int, if the data is ranked, this is the cutoff value for splitting it into two classes,
        - wracc_k : int, number of times an example can be covered when selecting with WRAcc,
        - minimalSetSize : int, minimum number of covered examples,
        - maxNumTerms : int, maximum number of conjunctions in one rule,
        - maxReported : int, number of returned rules,
        - maximalPvalue : float, maximum p-value of a returned rule,
        - weightFisher, weightGSEA, weightPAGE : float, weights for corresponding score functions; makes sense only if legacy = false,
        - dataFormat : str, legal values are 'tab' or 'list'
    Output:
        - json dictionary encoding the discovered rules.
        
    Note: See http://kt.ijs.si/software/SEGS/ for legacy format specification.
    
    @author: Anze Vavpetic, 2011 <anze.vavpetic@ijs.si>
    """
    result = gsegs().run(**kwargs)
    return json.dumps(result) # Return as json dictionary

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print 'Usage: python server_sdmsegs.py <machine address>:<port>'
        sys.exit(1)
    location = sys.argv[1]
    if not location.startswith('http://'):
        location = 'http://' + location
    port = int(location.split(':')[2])
    
    dispatcher = SoapDispatcher(
        'sdmsegs',
        location = location,
        action = location, # SOAPAction
        namespace = "http://www.example.com/sdmsegs.wsdl", prefix="ns0",
        trace = True,
        ns = True)
    
    # register the user function
    dispatcher.register_function('sdmsegs', sdmsegs_runner,
        returns={'results': str}, 
        args={'inputData': str, 
              'interactions': str, 
              'mapping' : str,
              'ont1' : str, 
              'ont2' : str, 
              'ont3' : str, 
              'ont4' : str,
              'generalTerms' : str,
              'legacy' : bool,
              'posClassVal' : str, 
              'cutoff' : int, 
              'wracc_k' : int, 
              'minimalSetSize' : int,
              'maxNumTerms' : int,
              'maxReported' : int,
              'maximalPvalue' : float,
              'weightFisher' : float,
              'weightGSEA' : float,
              'weightPAGE' : float,
              'dataFormat' : str
              })
    
    print "Starting server at %s..." % dispatcher.location
    httpd = HTTPServer(("", port), SOAPHandler)
    httpd.dispatcher = dispatcher
    httpd.serve_forever()

