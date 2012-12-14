# -*- coding: utf-8 -*-
"""
Service for the SDM-SEGS system.

@author: Anže Vavpetič, 2011 <anze.vavpetic@ijs.si>
"""
import tempfile
import os
import StringIO
import cPickle
from os.path import normpath, exists
from sys import stdout
from subprocess import Popen, PIPE
from time import sleep
from ZSI import Fault

# Import the sdmsegs module
from sdmsegs import sdmsegs

# generate stubs and import them
# IMPORTANT: location of the WSDL files is relative to the call point
from webServices import processPool, stubImporter
from webServices.processPool import GenericWebServiceProcess, NonexistentJobException, UnfinishedJobException

stubs = stubImporter.importZSIstubsFromURI('sdmsegs.wsdl')
services, server, types, WSDL = stubs.client, stubs.server, stubs.types, stubs.WSDL

class sdmsegsProcess(GenericWebServiceProcess):
    """
    This class represents one SDM-SEGS process; instances are instantiated only by sdmsegsService objects.
    """
    def run(self):
        """
        Run and dump the results.
        """
        
        try:
            runner = sdmsegs()
            result = runner.run(self._kwargs[sdmsegs.PROGRESS_FNAME], 
                           self._kwargs[sdmsegs.INPUT_DATA],
                           self._kwargs[sdmsegs.INTERACTIONS],
                           self._kwargs[sdmsegs.MAPPING],
                           self._kwargs[sdmsegs.ONT1],
                           ont2 = self._kwargs[sdmsegs.ONT2],
                           ont3 = self._kwargs[sdmsegs.ONT3],
                           ont4 = self._kwargs[sdmsegs.ONT4],
                           generalTerms = self._kwargs[sdmsegs.GENERAL_TERMS],
                           legacy = self._kwargs[sdmsegs.LEGACY],
                           posClassVal = self._kwargs[sdmsegs.POS_CLASS_VAL], 
                           cutoff = self._kwargs[sdmsegs.CUTOFF], 
                           wracc_k = self._kwargs[sdmsegs.WRACC_K], 
                           minimalSetSize = self._kwargs[sdmsegs.MIN_SET_SIZE],
                           maxNumTerms = self._kwargs[sdmsegs.MAX_NUM_TERMS],
                           maxReported = self._kwargs[sdmsegs.MAX_REPORTED],
                           maximalPvalue = self._kwargs[sdmsegs.MAX_P_VALUE],
                           weightFisher = self._kwargs[sdmsegs.WEIGHT_FISHER],
                           weightGSEA = self._kwargs[sdmsegs.WEIGHT_GSEA],
                           weightPAGE = self._kwargs[sdmsegs.WEIGHT_PAGE],
                           summarizeDescriptions = self._kwargs[sdmsegs.SUMMARIZE],
                           randomSeed = self._kwargs[sdmsegs.RANDOM_SEED],
                           level_ont1 = self._kwargs[sdmsegs.LEVEL_ONT1],
                           level_ont2 = self._kwargs[sdmsegs.LEVEL_ONT2],
                           level_ont3 = self._kwargs[sdmsegs.LEVEL_ONT3],
                           level_ont4 = self._kwargs[sdmsegs.LEVEL_ONT4]
                           )
        except Exception, e:
            print e
            self.reportError(e)
        else:
            self.dumpResults(result)
            self.finalizeProgress()
        finally:
            del result
            del runner
    
    @staticmethod
    def buildRulesObjList(ruleObjConstructor, rulesDict, ontDict):
    
        rules = []
        for k in sorted(rulesDict.keys()):
            rule = rulesDict[k]
            score = rule[sdmsegs.SCORES][sdmsegs.WRACC_SCORE]
            
            if score == 0.0:
	      break
            
            ruleObj = ruleObjConstructor()
            ruleObj.set_element_wracc(score)
    
            ruleObj.set_element_coveredGenes([str(x) for x in rule[sdmsegs.ALL_GENES]])
            ruleObj.set_element_coveredTopGenes([str(x) for x in rule[sdmsegs.TOP_GENES]])
    
            ruleDescObj = ruleObj.new_description()
            STERMS = []
            INTTERMS = []
            for term in rule[sdmsegs.TERMS]:
                if not isinstance(term, list):
                    trm = ruleDescObj.new_terms()
                    trm.set_element_termID(term)
                    trm.set_element_name(ontDict[term])
                    trm.set_element_domain('')
                    STERMS.append(trm)
                else: #interacting terms
                    for intTerm in term:
                        itrm = ruleDescObj.new_interactingTerms()
                        itrm.set_element_termID(intTerm)
                        itrm.set_element_name(ontDict[intTerm])
                        itrm.set_element_domain('')
                        INTTERMS.append(itrm)
            ruleDescObj.set_element_terms(STERMS)
            ruleDescObj.set_element_interactingTerms(INTTERMS)
    
            ruleObj.set_element_description(ruleDescObj)
            rules.append(ruleObj)
    
        return rules
    
    @classmethod
    def fetchResults(klas, buildRulesObjListFunction, jobID, responseObjectConstructor):
        progressFname = normpath('%s/%s%s' % (klas.resultsDir, jobID, klas.PROGRESS_FNAME_ENDING))
        resultsFname = normpath('%s/%s%s' % (klas.resultsDir, jobID, klas.RESULTS_FNAME_ENDING))
        
        if not exists(progressFname):
            raise NonexistentJobException()

        fp = open(progressFname, 'r')
        p = int(round(float(fp.read().strip())))
        fp.close()
        if p != klas.PROGRESS_FINISH_INDICATOR:
            raise UnfinishedJobException()

        try:
            fp = open(resultsFname, 'r')
            sdmsegs_results = cPickle.load(fp)
        except Exception:
            raise InvalidResults('Panic: result of a finished can not be read/interpreted!')
        finally:
            fp.close()

        # read the results and build the response
        ontDict = sdmsegs_results['ontDict']
        result = responseObjectConstructor()
        
        rules_wracc = buildRulesObjListFunction(result.new_rules, sdmsegs_results[sdmsegs.OVEREXPRESSED][sdmsegs.WRACC], ontDict)
        result.set_element_rules(rules_wracc)
        
        return result
            
class sdmsegsService(server.sdmsegs):
    """
    This class handles all requests and responses for the SDM-SEGS service.
    """
    def __init__(self, **kwargs):
        self.procPool = processPool.ProcesPool()
        self.procPool.start()
        server.sdmsegs.__init__(self)

    def __del__(self):
        n = self.procPool.getNjobs()
        if n > 0:
            stdout.write('Terminating %d running job(s)\n' % n)
            self.procPool.prepareForTermination()
            stdout.write('Please wait (max. %d seconds) while all processes are terminated...\n' % processPool.ProcesPool.MONITOR_THREAD_SLEEPTIME)
            self.procPool.join()
        else:
            #stdout.write('No active jobs, instant termination.\n')
            pass

    def soap_runsdmsegs(self, ps):
        request = ps.Parse(services.runsdmsegsRequest.typecode)
        response = services.runsdmsegsResponse()
        
        # Ontologies
        ont1 = request.get_element_ont1()
        ont2 = request.get_element_ont2()
        ont3 = request.get_element_ont3()
        ont4 = request.get_element_ont4()
        
        # Input data
        posClassVal = request.get_element_posClassVal()
        inputData_tmp = request.get_element_inputData()
        interactions_tmp = request.get_element_interactions()   
        mapping_tmp = request.get_element_mapping()
        
        # Convert to list of tuples
        inputData = []
        for e in inputData_tmp:
            ex_id = e.get_element_id()
            ex_rank_or_label = e.get_element_rank_or_label() if posClassVal else float(e.get_element_rank_or_label())
            inputData.append((ex_id, ex_rank_or_label))
        
        interactions = []
        for e in interactions_tmp:
            id1 = e.get_element_id1()
            id2 = e.get_element_id2()
            interactions.append((id1, id2))
            
        mapping = []
        for e in mapping_tmp:
            ex_id = e.get_element_id()
            uris = e.get_element_uri()
            mapping.append((ex_id, uris))
        
        #
        # Read all other parameters. If a specific parameter is omitted use the default values defined by the sdmsegs module.
        #
        genTerms = request.get_element_generalTerms() if request.get_element_generalTerms() else []
        cutoff = request.get_element_cutoff()
        minSetSize = request.get_element_minimalSetSize() if request.get_element_minimalSetSize() else sdmsegs.defaults[sdmsegs.MIN_SET_SIZE]
        maxNumTerms = request.get_element_maxNumTerms() if request.get_element_maxNumTerms() else sdmsegs.defaults[sdmsegs.MAX_NUM_TERMS]
        maxReported = request.get_element_maxReported() if request.get_element_maxReported() else sdmsegs.defaults[sdmsegs.MAX_REPORTED]
        wracc_k = request.get_element_wracc_k() if request.get_element_wracc_k() else sdmsegs.defaults[sdmsegs.WRACC_K]
        maximalPvalue = request.get_element_maximalPvalue() if request.get_element_maximalPvalue() else sdmsegs.defaults[sdmsegs.MAX_P_VALUE]
        weightFisher = request.get_element_weightFisher() if request.get_element_weightFisher() else sdmsegs.defaults[sdmsegs.WEIGHT_FISHER]
        weightGSEA = request.get_element_weightGSEA() if request.get_element_weightGSEA() else sdmsegs.defaults[sdmsegs.WEIGHT_GSEA]
        weightPAGE = request.get_element_weightPAGE() if request.get_element_weightPAGE() else sdmsegs.defaults[sdmsegs.WEIGHT_PAGE]
        summarize = request.get_element_summarizeDescriptions() if request.get_element_summarizeDescriptions() != None else sdmsegs.defaults[sdmsegs.SUMMARIZE]
        randomSeed = request.get_element_randomSeed() if request.get_element_randomSeed() else sdmsegs.defaults[sdmsegs.RANDOM_SEED]
        legacy = request.get_element_legacy()
        level_ont1 = request.get_element_level_ont1() if request.get_element_level_ont1() else sdmsegs.defaults[sdmsegs.LEVEL_ONT1]
        level_ont2 = request.get_element_level_ont2() if request.get_element_level_ont2() else sdmsegs.defaults[sdmsegs.LEVEL_ONT2]
        level_ont3 = request.get_element_level_ont3() if request.get_element_level_ont3() else sdmsegs.defaults[sdmsegs.LEVEL_ONT3]
        level_ont4 = request.get_element_level_ont4() if request.get_element_level_ont4() else sdmsegs.defaults[sdmsegs.LEVEL_ONT4]
        
        jobID = processPool.generateID()
        progressFname = normpath('%s/%s%s' % (sdmsegsProcess.resultsDir, jobID, sdmsegsProcess.PROGRESS_FNAME_ENDING))        
        
        # Create a dict of parameter:value pairs and instantiate a SDM-SEGS process.
        args = {
                'jobID' : jobID,
                sdmsegs.PROGRESS_FNAME : progressFname,
                sdmsegs.INPUT_DATA : inputData,
                sdmsegs.INTERACTIONS : interactions,
                sdmsegs.MAPPING : mapping,
                sdmsegs.ONT1 : ont1,
                sdmsegs.ONT2 : ont2,
                sdmsegs.ONT3 : ont3,
                sdmsegs.ONT4 : ont4,
                sdmsegs.GENERAL_TERMS : genTerms,
                sdmsegs.LEGACY : legacy,
                sdmsegs.POS_CLASS_VAL : posClassVal,
                sdmsegs.CUTOFF : cutoff,
                sdmsegs.WRACC_K : wracc_k,
                sdmsegs.MIN_SET_SIZE : minSetSize,
                sdmsegs.MAX_NUM_TERMS : maxNumTerms,
                sdmsegs.MAX_REPORTED : maxReported,
                sdmsegs.MAX_P_VALUE : maximalPvalue,
                sdmsegs.WEIGHT_FISHER : weightFisher,
                sdmsegs.WEIGHT_GSEA : weightGSEA,
                sdmsegs.WEIGHT_PAGE : weightPAGE,
                sdmsegs.SUMMARIZE : summarize,
                sdmsegs.RANDOM_SEED : randomSeed,
                sdmsegs.LEVEL_ONT1 : level_ont1,
                sdmsegs.LEVEL_ONT2 : level_ont2,
                sdmsegs.LEVEL_ONT3 : level_ont3,
                sdmsegs.LEVEL_ONT4 : level_ont4
        }
        proc = sdmsegsProcess(kwargs=args)
        proc.start()
        try:
            self.procPool.addProcess(proc, jobid=jobID)
        except Exception, e:
            raise Fault(Fault.Server, 'Internal error: %s' % str(e))
        
        response.set_element_jobID(jobID)
        return request, response
    

    def soap_getResult(self, ps):
        request = ps.Parse(services.getResultRequest.typecode)
        
        jobID = request.get_element_jobID()
        try:
            response = sdmsegsProcess.fetchResults(sdmsegsProcess.buildRulesObjList, jobID, services.getResultResponse)
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

    def soap_getProgress(self, ps):
        request = ps.Parse(services.getProgressRequest.typecode)
        response = services.getProgressResponse()

        jobID = request.get_element_jobID()
        try:
            progress = sdmsegsProcess.getProgress(jobID)
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
    address = services.sdmsegsLocator().getsdmsegsAddress()
    stubImporter.fixServiceAddress(services.sdmsegsLocator, sdmsegsService, address, WSDL, port=newPort, ip=ip)

    return sdmsegsService()