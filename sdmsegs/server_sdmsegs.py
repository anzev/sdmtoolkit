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
    result = gsegs().run(**kwargs)
    return json.dumps(result) # Return as json dictionary

if __name__ == '__main__':
    if len(sys.argv) == 0:
        print 'Usage: python server_sdmsegs.py <port>'
        sys.exit(1)
    port = int(sys.argv[1])
    
    dispatcher = SoapDispatcher(
        'SDM-SEGS',
        location = "http://localhost:%d/" % port,
        action = 'http://localhost:%d/' % port, # SOAPAction
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
            #summarizeDescriptions = defaults[SUMMARIZE],
            #randomSeed = defaults[RANDOM_SEED],
            #level_ont1 = defaults[LEVEL_ONT1],
            #level_ont2 = defaults[LEVEL_ONT2],
            #level_ont3 = defaults[LEVEL_ONT3],
            #level_ont4 = defaults[LEVEL_ONT4],
              'dataFormat' : str
              })
    
    print "Starting server at %s..." % dispatcher.location
    httpd = HTTPServer(("", port), SOAPHandler)
    httpd.dispatcher = dispatcher
    httpd.serve_forever()

