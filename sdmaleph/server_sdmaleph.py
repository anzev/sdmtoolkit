# -*- coding: utf-8 -*-
"""
SDM-Aleph server.

@author: Anže Vavpetič, 2012 <anze.vavpetic@ijs.si>
"""
import sys
import json
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer

from sdmaleph_service import sdmaleph_runner

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print 'Usage: python server_sdmaleph.py <machine address>:<port>'
        sys.exit(1)
    location = sys.argv[1]
    if not location.startswith('http://'):
        location = 'http://' + location
    port = int(location.split(':')[2])
    
    dispatcher = SoapDispatcher(
        'sdmaleph',
        location = location,
        action = location, # SOAPAction
        namespace = "http://www.example.com/sdmaleph.wsdl", prefix="ns0",
        trace = True,
        ns = True)
    
    # register the user function
    dispatcher.register_function('sdmaleph', sdmaleph_runner,
        returns={'theory': str}, 
        args={
            'examples' : str,
            'mapping' : str,
            'ontologies' : [{'ontology' : str}],
            'relations' : [{'relation' : str}],
            'posClassVal' : str,
            'cutoff' : int,
            'minPos' : int,
            'noise' : int,
            'clauseLen' : int,
            'dataFormat' : str,
        })
    
    print "Starting server at %s..." % dispatcher.location
    httpd = HTTPServer(("", port), SOAPHandler)
    httpd.dispatcher = dispatcher
    httpd.serve_forever()