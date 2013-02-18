#
# Wrapper for the OWL2X java application.
#
# Anze Vavpetic <anze.vavpetic@ijs.si>, April 2011
#
import tempfile
import subprocess
import logging
import sys
import cPickle
import os

DEBUG = True

# Setup a logger
logger = logging.getLogger("owl2x [Python]")
#logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(name)s %(levelname)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# OWL2X jar relative to this script
# FIXME: use jpype for calling java classes instead
OWL2X_PATH = '%s/%s' % (os.path.dirname(os.path.abspath(__file__)), 'OWL2X/')

# Target predicate.
TARGET_PRED = 'target'

# Main type.
MAIN_TYPE = 'instance'

#Isa predicate.
ISA_PRED = 'isa'

class OWL2X(object):
    @staticmethod
    def get_segs_input(ontologies, mapping):
        """
        Returns a tuple (g2ont, ont) suitable for segs.
        """
        tmpDir = tempfile.mkdtemp()
        
        ontologyFiles = []
        for ont in ontologies:
            if OWL2X.isURI(ont):
                ontologyFiles.append(ont)
            else:
                tmp = tempfile.NamedTemporaryFile()
                ontologyFiles.append(tmp)
                tmp.write(ont)
                tmp.flush()
            
        tmp = tempfile.NamedTemporaryFile()

        mappingStr = ''
        for pair in mapping:
            mappingStr += '%s ' % pair[0]
            uris = pair[1]
            for uri in uris:
                mappingStr += '%s ' % uri
            mappingStr += '\n'
        
        tmp.write(mappingStr)
        tmp.flush()
        
        mappingFile = tmp.name
        
        args = ['java', '-jar', '%s/owl2x.jar' % OWL2X_PATH, 'segs', 'short', tmpDir, mappingFile] + OWL2X.names(ontologyFiles)
        logger.debug(args)
        
        p = subprocess.Popen(args)
        stdout_str, stderr_str = p.communicate()
        
        logger.debug(stdout_str)
        logger.debug(stderr_str)
        
        for ontfile in ontologyFiles:
            ontfile.close()
            
        return ([eval(l) for l in open('%s/ont' % tmpDir)], [eval(l) for l in open('%s/g2ont' % tmpDir)])
    
    @staticmethod
    def get_aleph_input(ontologies, mapping, relations, posExamples, negExamples):
        """
        Returns a tuple (pos, neg, b).
        """        
        tmpDir = tempfile.mkdtemp()
        
        # Write ontologies to disk
        ontologyFiles = []
        for ont in ontologies:
            if OWL2X.isURI(ont):
                ontologyFiles.append(ont)
            else:
                tmp = tempfile.NamedTemporaryFile()
                ontologyFiles.append(tmp)
                tmp.write(ont)
                tmp.flush()
            
        tmp = tempfile.NamedTemporaryFile()
        
        mappingStr = ''
        for pair in mapping:
            mappingStr += '%s ' % pair[0]
            uris = pair[1]
            for uri in uris:
                mappingStr += '%s ' % uri
            mappingStr += '\n'
        
        tmp.write(mappingStr)
        tmp.flush()
        
        mappingFile = tmp.name
        
        # Convert the ontologies.
        args = ['java', '-jar', '%s/owl2x.jar' % OWL2X_PATH, 'prolog', 'short', tmpDir, mappingFile] + OWL2X.names(ontologyFiles)
        logger.debug(args)
        
        p = subprocess.Popen(args)
        stdout_str, stderr_str = p.communicate()
        
        logger.debug(stdout_str)
        logger.debug(stderr_str)
        
        for ontfile in ontologyFiles:
            if 'close' in dir(ontfile):
                ontfile.close()
    
        # Convert examples.
        pos, neg = "", ""
        
        # Assume posExamples and negExamples are lists of example IDs
        for ex in posExamples:
            pos += '%s(i%d).\n' % (TARGET_PRED, int(ex[0]))

        for ex in negExamples:
            neg += '%s(i%d).\n' % (TARGET_PRED, int(ex[0]))

        # Now add the custom relations.
        sys.path.append(tmpDir)
        import b
        
        # Assumes relations has the form: [[r_name1, [(a, b), ...]], [r_name2, [...]], ...]
        for relation in relations:
            r_name = relation[0]
            b.modes.append(":- modeb(1, %s(+%s, -%s))." % (r_name, MAIN_TYPE, MAIN_TYPE))
            b.table.append(":- table %s/2." % r_name)
            b.determinations.append(":- determination(%s/1, %s/2)." % (TARGET_PRED, r_name))
            for pair in relation[1]:
                b.definitions.append("%s(i%s, i%s)." % (r_name, pair[0], pair[1]))

        bk = ""
        bk += bappend(b.table)
        bk += bappend(b.modes)
        bk += bappend(b.determinations)
        bk += bappend(b.isa)
        bk += '%s(X,Y) :- %s(X,Z), %s(Z,Y).\n' % (ISA_PRED, ISA_PRED, ISA_PRED)

        bk += open('prune.pl').read() + "\n\n"
        
        bk += bappend(b.definitions)
        bk += bappend(b.instances)
        
        # Append original example rank / label
        for ex in posExamples:
            bk += "orig_label(i%d, '%s').\n" % (ex[0], str(ex[1]))
        for ex in negExamples:
            bk += "orig_label(i%d, '%s').\n" % (ex[0], str(ex[1]))
                
        return (pos, neg, bk)
    
    @staticmethod
    def isURI(text):
        # For example: http://www.berkeleybop.org/ontologies/owl/GO.owl
        return text.strip().startswith("http://")
    
    @staticmethod
    def names(fileList):
        new = []
        for f in fileList:
            if 'name' in dir(f):
                new.append(f.name)
            else:
                new.append(f)
        return new
    
def bappend(table):
    s = ""
    for e in table:
        s += e + '\n'
        
    return s
