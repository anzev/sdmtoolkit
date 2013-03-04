# -*- coding: utf-8 -*-
"""
RSD service.

@author: Anže Vavpetič, 2013 <anze.vavpetic@ijs.si>
"""
import sys
import json
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from BaseHTTPServer import HTTPServer

from rsd import RSD

def rsd_runner(
    examples, background_knowledge, pos_examples=None, neg_examples=None, settings=None, subgroups=False, 
    clauselength=RSD.ESSENTIAL_PARAMS['clauselength'], 
    depth=RSD.ESSENTIAL_PARAMS['depth'],
    negation=RSD.ESSENTIAL_PARAMS['negation'], 
    min_coverage=RSD.ESSENTIAL_PARAMS['min_coverage'],
    filtering=RSD.ESSENTIAL_PARAMS['filtering']
):
    rsd = RSD()
    if settings:
        rsd.settingsAsFacts(settings)
    rsd.set('clauselength', clauselength)
    rsd.set('depth', depth)
    rsd.set('negation', negation)
    rsd.set('min_coverage', min_coverage)
    rsd.set('filtering', filtering)
    features, arff, rules = rsd.induce(background_knowledge, examples=examples, pos=pos_examples, neg=neg_examples, cn2sd=subgroups)
    return {'arff' : arff, 'rules' : rules, 'features' : features}

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print 'Usage: python rsd_service.py <machine address>:<port>'
        sys.exit(1)
    location = sys.argv[1]
    if not location.startswith('http://'):
        location = 'http://' + location
    port = int(location.split(':')[2])
    
    dispatcher = SoapDispatcher(
        'rsd',
        location = location,
        action = location, # SOAPAction
        namespace = "http://www.example.com/rsd.wsdl", prefix="ns0",
        trace = True,
        ns = True)
    
    # register the user function
    dispatcher.register_function('rsd', rsd_runner,
        returns={'arff': str, 'rules' : str, 'features' : str}, 
        args={
            'examples' : str,
            'pos_examples' : str,
            'neg_examples' : str,
            'background_knowledge' : str,
            'settings' : str,
            'clauselength' : int,
            'depth' : int,
            'negation' : str,
            'min_coverage' : int,
            'filtering' : bool,
            'subgroups' : bool
        })
    
    print "Starting server at %s..." % dispatcher.location
    httpd = HTTPServer(("", port), SOAPHandler)
    httpd.dispatcher = dispatcher
    httpd.serve_forever()