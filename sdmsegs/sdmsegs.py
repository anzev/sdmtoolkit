#
# Python interface to gsegs.
# 
# author: Anze Vavpetic <anze.vavpetic@ijs.si>, April 2011
#

import sys
import StringIO
import segs

sys.path.append('..')
from owl2x import OWL2X
from utils import StructuredFormat, logger

f = open('progress.txt','w')
f.close()

class SDMSEGS(object):
    """
    Main wrapper class to be used within scripts.
    """  
    # Keyword definitions
    PROGRESS_FNAME = 'progressFname'
    INPUT_DATA = 'inputData'
    INTERACTIONS = 'interactions'
    MAPPING = 'mapping'
    ONT1 = 'ont1'
    ONT2 = 'ont2'
    ONT3 = 'ont3'
    ONT4 = 'ont4'
    GENERAL_TERMS = 'generalTerms'
    LEGACY = 'legacy'
    POS_CLASS_VAL = 'posClassVal'
    CUTOFF = 'cutoff'
    WRACC_K = 'wracc_k'
    MIN_SET_SIZE = 'minimalSetSize'
    MAX_NUM_TERMS = 'maxNumTerms'
    MAX_REPORTED = 'maxReported'
    MAX_P_VALUE = 'maximalPvalue'
    WEIGHT_FISHER = 'weightFisher'
    WEIGHT_GSEA = 'weightGSEA'
    WEIGHT_PAGE = 'weightPAGE'
    SUMMARIZE = 'summarizeDescriptions'
    GSEA_FACTOR = 'gseaFactor'
    RANDOM_SEED = 'randomSeed'
    PVAL_ITERS = 'pvalIters'
    
    # SEGS results keywords
    OVEREXPRESSED = 'A'
    UNDEREXPRESSED = 'B'
    ONT_TERMS = 'terms'
    ALL_GENES = 'allGenes'
    TOP_GENES = 'topGenes'
    TERMS = 'terms'
    FISHER = 'fisher'
    GSEA = 'gsea'
    PAGE = 'page'
    WRACC = 'WRAcc'
    COMBINED = 'all'
    SCORES = 'scores'
    FISHER_P = 'fisher_p'
    UNADJUSTED_P = 'unadjusted_p'
    PAGE_P = 'page_p'
    Z_SCORE = 'z_score'
    WRACC_SCORE = 'wracc'
    GSEA_P = 'gsea_p'
    ENRICHMENT = 'enrichment_score'
    AGGREGATE_P = 'aggregate_p'
    ONT_BRANCH = 'branch'
    ONT_NAME = 'name'
    LEVEL_ONT1 = 'level_ont1'
    LEVEL_ONT2 = 'level_ont2'
    LEVEL_ONT3 = 'level_ont3'
    LEVEL_ONT4 = 'level_ont4'
    
    # Optional settings
    defaults = {
        MIN_SET_SIZE : 5,
        MAX_NUM_TERMS : 3,
        MAX_REPORTED : 100,
        RANDOM_SEED : 10,
        WRACC_K : 5,
        SUMMARIZE : 0,
        MAX_P_VALUE : 0.05,
        WEIGHT_FISHER : 1.0,
        WEIGHT_GSEA : 0.0,
        WEIGHT_PAGE : 0.0,
        LEVEL_ONT1 : 1,
        LEVEL_ONT2 : 1,
        LEVEL_ONT3 : 1,
        LEVEL_ONT4 : 1
    }

    # Locked settings
    locked = {
        GSEA_FACTOR : 3,
        PVAL_ITERS : {0.1:10, 0.05:100, 0.01:200, 0.005:400}
    }
    
    def run(self, 
            inputData,           # List of the form [..., (id_i, rank_i or label_i), ...] or str.
            mapping,             # List of the form [..., (id_i, URI1, URI2, ...), ...] where id_i is annotated with with the listed URI's or str.
            ont1,                # OWL ontologies as strings 
            ont2 = None, 
            ont3 = None, 
            ont4 = None,
            interactions = [],        # List of the form [..., (id_i, id_j), ...] where id_i interacts with id_j or str.
            generalTerms = [],
            legacy = False,
            posClassVal = None, 
            cutoff = None, 
            wracc_k = defaults[WRACC_K], 
            minimalSetSize = defaults[MIN_SET_SIZE],
            maxNumTerms = defaults[MAX_NUM_TERMS],
            maxReported = defaults[MAX_REPORTED],
            maximalPvalue = defaults[MAX_P_VALUE],
            weightFisher = defaults[WEIGHT_FISHER],
            weightGSEA = defaults[WEIGHT_GSEA],
            weightPAGE = defaults[WEIGHT_PAGE],
            summarizeDescriptions = defaults[SUMMARIZE],
            randomSeed = defaults[RANDOM_SEED],
            level_ont1 = defaults[LEVEL_ONT1],
            level_ont2 = defaults[LEVEL_ONT2],
            level_ont3 = defaults[LEVEL_ONT3],
            level_ont4 = defaults[LEVEL_ONT4],
            dataFormat = StructuredFormat.FORMAT_TAB,
            progressFname = 'progress.txt',   
            ):

        logger.info("Starting SDM-SEGS.")
        
        # Check if we have properly structured inputs or strings
        if type(inputData) in [str, unicode]:
            inputData = StructuredFormat.parseInput(inputData, dataFormat)
        if type(interactions) in [str, unicode]:
            interactions = StructuredFormat.parseInteractions(interactions)
        if type(mapping) in [str, unicode]:
            mapping = StructuredFormat.parseMapping(mapping)
        if type(generalTerms) in [str, unicode]:
            generalTerms = StructuredFormat.parseGeneralTerms(generalTerms)
        if posClassVal:
            # Labelled data
            pos, neg = [], []
            # Assure pos class instances are listed first.
            for iid, label in inputData:
                if label == posClassVal:
                    pos.append((iid, label))
                else:
                    neg.append((iid, label))
            cutoff = len(pos)
            pos.extend(neg)
            data = [[], []]
            for iid, label in pos:
                data[0].append(int(iid))
                data[1].append(0.5)
        else:
            # Assume ranked data
            if not cutoff:
                raise MissingParameterException("Cutoff needs to be specified for ranked data by the user!")
            data = [[], []]
            for iid, rank in inputData:
                data[0].append(int(iid))
                data[1].append(rank)
        inputData = data
        # Parse interactions
        idToList = dict()
        for id1, id2 in interactions:
            if not idToList.has_key(id1):
                idToList[id1] = []
            idToList[id1].append(id2)
        g2g = []
        for iid, idList in sorted(idToList.items(), key=lambda p: p[0]):
            g2g.append([iid, idList])
        if not legacy:
            import segs
            ont, g2ont = OWL2X.get_segs_input(filter(None, [ont1, ont2, ont3, ont4]), mapping)
            numOfOnt = len(filter(None, [ont1, ont2, ont3, ont4]))
        else:
            import segs_legacy as segs
            # Legacy input of segs - we assume it is already properly formatted
            g2ont = []
            for entry in mapping:
                g2ont.append([entry[0], entry[1]])
            ont = []
            for entry in StringIO.StringIO(ont1):
                ont.append(eval(entry))
            numOfOnt = 4
        # Create a map from go terms to human-readable descriptions
        ontDict = dict()
        for entry in ont:
            goID = entry[0]
            name = entry[1][1]
            ontDict[goID] = name     
        logger.info("Running SEGS subsystem.")        
        result = segs.runSEGS(
            generalTerms = generalTerms,
            ontology = ont,
            g2g = g2g,
            g2ont = g2ont,
            progressFname = progressFname,
            inputData = inputData,
            useMolFunctions = True,
            useBioProcesses = numOfOnt > 1,
            useCellComponents = numOfOnt > 2,
            useKEGG = numOfOnt > 3,
            useGeneInteractions = 1 if interactions else 0,
            summarize = summarizeDescriptions,
            cutoff = cutoff,
            minSizeGS = minimalSetSize,
            maxNumTerms = maxNumTerms,
            GSEAfactor = SDMSEGS.locked[SDMSEGS.GSEA_FACTOR],
            numIters = 0,
            PrintTopGS = maxReported,
            p_value = maximalPvalue if legacy else 1,
            weightFisher = weightFisher,
            weightGSEA = weightGSEA,
            weightPAGE = weightPAGE,
            randomSeed = randomSeed,
            wracc_k = wracc_k,
            level_ont1 = level_ont1,
            level_ont2 = level_ont2,
            level_ont3 = level_ont3,
            level_ont4 = level_ont4)
        del segs
        result['ontDict'] = ontDict      
        logger.info("SDM-SEGS finished.")
        return result

class MissingParameterException(Exception):
    pass


if __name__ == '__main__':
    inputData = open('/home/anze/data/bank.tab').read()
    mapping = open('/home/anze/data/bank_map.txt').read()
    ont1 = open('/home/anze/data/occupation.owl').read()
    ont2 = open('/home/anze/data/banking_services.owl').read()
    ont3 = open('/home/anze/data/geography.owl').read()
    foo = open('foo.txt', 'w')
    foo.close()
    runner = SDMSEGS()
    runner.run(inputData, mapping, ont1, ont2, ont3, interactions=[], dataFormat=StructuredFormat.FORMAT_TAB, posClassVal='Yes', progressFname='foo.txt')
    