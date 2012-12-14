# -*- coding: utf-8 -*-
"""
Service for the SDM-Aleph system.

@author: Anže Vavpetič, 2011 <anze.vavpetic@ijs.si>
"""
import tempfile
import sys
import random
import os
import StringIO
import cPickle
import re

from sys import stdout
from os.path import normpath, exists
from subprocess import Popen, PIPE
from time import sleep
from ZSI import Fault

# Aleph
from aleph import Aleph

# OWL2X
sys.path.append('..')
from owl2x import OWL2X

# O4WS imports
from webServices import processPool, stubImporter
from webServices.processPool import GenericWebServiceProcess, NonexistentJobException, UnfinishedJobException

stubs = stubImporter.importZSIstubsFromURI('sdmaleph.wsdl')
services, server, types, WSDL = stubs.client, stubs.server, stubs.types, stubs.WSDL

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

class sdmalephProcess(GenericWebServiceProcess):
    """
    The SDM-Aleph process
    """
    def run(self):
        """
        Run and dump the results.
        """
        try:
            keys = self._kwargs            
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
            
        except Exception, e:
            print e
            self.reportError(e)
        else:
            self.dumpResults(result)
            self.finalizeProgress()
        finally:
            del result
            del runner
    
    def __conv(self, rules, pos, neg):
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
    
    @staticmethod
    def buildRulesObjectList(rules, resultObjConstructor):
        result = resultObjConstructor()
        
        ruleList = []
        for r in sorted(rules, key = lambda x: x['wracc'], reverse=True):
            ruleObj = result.new_rules()
            
            ruleObj.set_element_coveredGenes([str(x) for x in r['covered']])
            ruleObj.set_element_coveredTopGenes([str(x) for x in r['posCovered']])
            ruleObj.set_element_wracc(r['wracc'])
            
            descrObj = ruleObj.new_description()
            
            # Parse the horn clause subgroup description.
            clause = r['clause']
            terms = map(lambda x: x.strip(), re.findall(r'([\w\'\s]+\([AB,]+\))', clause[clause.rfind(':-')+2:]))
            
            termsList = []
            for t in terms:
                termObj = descrObj.new_terms()
                termObj.set_element_termID(' ')
                termObj.set_element_name(t)
                termObj.set_element_domain(' ')
                termsList.append(termObj)
                
            descrObj.set_element_terms(termsList)
            ruleObj.set_element_description(descrObj)
            ruleList.append(ruleObj)
            
        return ruleList
        
class sdmalephService(server.sdmaleph):
    """
    This class implements the SDM-Aleph web service.
    """
    def __init__(self, **kwargs):
        self.procPool = processPool.ProcesPool()
        self.procPool.start()
        server.sdmaleph.__init__(self)
        
    def __del__(self):
        n = self.procPool.getNjobs()
        if n > 0:
            stdout.write('Terminating %d running job(s)\n' % n)
            self.procPool.prepareForTermination()
            stdout.write('Please wait (max. %d seconds) while all processes are terminated...\n' % processPool.ProcesPool.MONITOR_THREAD_SLEEPTIME)
            self.procPool.join()
        else:
            pass
        
    def soap_induce(self, ps):
        request = ps.Parse(services.induceRequest.typecode)
        response = services.induceResponse()
        
        examples_tmp = request.get_element_examples()
        relations_tmp = request.get_element_relations()
        mapping_tmp = request.get_element_mapping()
        ontologies = request.get_element_ontologies()
        posClassVal = request.get_element_posClassVal()
        cutoff = request.get_element_cutoff() if request.get_element_cutoff() else len(examples_tmp)/2
        minSetSize = request.get_element_minimalSetSize() if request.get_element_minimalSetSize() else defaults['minimalSetSize']
        maxNumTerms = request.get_element_maxNumTerms() if request.get_element_maxNumTerms() else defaults['maxNumTerms']
        
        examples = []
        for e in examples_tmp:
            ex_id = e.get_element_id()
            ex_rank_or_label = e.get_element_rank_or_label() if posClassVal else float(e.get_element_rank_or_label())
            examples.append((ex_id, ex_rank_or_label))
        
        relations = []
        for rel in relations_tmp:
            r_name = rel.get_element_name()
            ext = rel.get_element_extension()
            pairs = []
            for pair in ext:
                pairs.append((pair[0], pair[1]))
            relations.append([r_name, pairs])
            
        mapping = []
        for e in mapping_tmp:
            ex_id = e.get_element_id()
            uris = e.get_element_uri()
            mapping.append((ex_id, uris))
            
        # Convert inputs to prolog.
        pos = []
        neg = []
        if posClassVal:
            for ex in examples:
                if ex[1] == posClassVal:
                    pos.append(ex)
                else:
                    neg.append(ex)
        else:
            if cutoff > len(examples):
                raise Fault(Fault.Server, 'The cutoff is set too high: cutoff = %d, number of examples = %d' % (cutoff, len(examples)))
            
            pos = filter(lambda ex: ex[1] >= cutoff, examples)
            if len(examples) - cutoff > 0:
                neg = random.sample(filter(lambda ex: ex[1] < cutoff, examples), cutoff)
            else:
                neg = filter(lambda ex: ex[1] < cutoff, examples)
        
        jobID = processPool.generateID()
        progressFname = normpath('%s/%s%s' % (sdmalephProcess.resultsDir, jobID, sdmalephProcess.PROGRESS_FNAME_ENDING))         
        
        args = {
            JOB_ID : jobID,
            PROGRESS_FNAME : progressFname,
            'ontologies' : ontologies,
            'mapping' : mapping,
            'relations' : relations,
            'pos' : pos,
            'neg' : neg,
            'examples' : examples
        }

        proc = sdmalephProcess(kwargs=args)
        proc.start()
        
        try:
            self.procPool.addProcess(proc, jobid=jobID)
        except Exception, e:
            raise Fault(Fault.Server, 'Internal error: %s' % str(e))
        
        response.set_element_jobID(jobID)
        return request, response
    
    def soap_getResult(self, ps):
        request = ps.Parse(services.getResultRequest.typecode)
        response = services.getResultResponse()
        
        jobID = request.get_element_jobID()
        try:
            rules = sdmalephProcess.fetchResults(jobID)
            ruleList = sdmalephProcess.buildRulesObjectList(rules, services.getResultResponse)
            response.set_element_rules(ruleList)
        except processPool.NonexistentJobException:
            if self.procPool.exists(jobID):
                raise Fault(Fault.Server, 'Job with ID %s is not yet scheduled' % str(jobID))
            else:
                raise Fault(Fault.Server, 'Job with ID %s does not exist' % str(jobID))
        except processPool.UnfinishedJobException:
            raise Fault(Fault.Server, 'Job with ID %s is not yet finished' % str(jobID))
        except Exception, e:
            raise Fault(Fault.Server, 'Internal error: %s' % str(e))
        
        return request, response
    
    #
    # TODO: 
    # 
    def soap_getProgress(self, ps):
        request = ps.Parse(services.getProgressRequest.typecode)
        response = services.getProgressResponse()

        jobID = request.get_element_jobID()
        try:
            progress = sdmalephProcess.getProgress(jobID)
        except NonexistentJobException:
            if self.procPool.exists(jobID):
                raise Fault(Fault.Server, 'Job with ID %s is not yet scheduled' % str(jobID))
            else:
                raise Fault(Fault.Server, 'Job with ID %s does not exists' % str(jobID))
        except Exception, e:
            raise Fault(Fault.Server, 'Internal error: %s' % str(e))

        response.set_element_progress(progress)
        return request, response
    
    
def getService(newPort=None, ip=None):
    address = services.sdmalephLocator().getsdmalephAddress()
    stubImporter.fixServiceAddress(services.sdmalephLocator, sdmalephService, address, WSDL, port=newPort, ip=ip)

    return sdmalephService()