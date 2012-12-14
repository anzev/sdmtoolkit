#
# Python interface to Aleph.
# 
# author: Anze Vavpetic <anze.vavpetic@ijs.si>
#
import os.path
import shutil
import logging
import re
import tempfile
from stat import *
from subprocess import Popen, PIPE

DEBUG = True

# Setup a logger
logger = logging.getLogger("Aleph [Python]")
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(name)s %(levelname)s: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

class Aleph(object):
    """
    Main class that handles all the settings and eventually creates a yap process and executes aleph.
    """
    # The aleph source file is presumed to be in the same dir as this file.
    THIS_DIR = os.path.dirname(__file__) if os.path.dirname(__file__) else '.'
    DIR = tempfile.mkdtemp()
    ALEPH_FN = 'aleph.pl'
    ALEPH = DIR + '/' + ALEPH_FN
    YAP = '/usr/local/bin/yap'
    RULES_SUFFIX = 'Rules'
    SCRIPT = 'run_aleph.pl'
    
    def __init__(self, verbosity=logging.NOTSET):
        """
        Creates an Aleph object.
        
        @param logging can be DEBUG, INFO or NOTSET (default). This controls the verbosity of the output.
        """
        self.postGoal = None
        self.postScript = None
        # Dictionary of non-default settings
        self.settings = dict()
        logger.setLevel(verbosity)
        
        shutil.copy("%s/%s" % (Aleph.THIS_DIR, Aleph.ALEPH_FN), Aleph.ALEPH)
        
    def set(self, name, value):
        """
        Sets the value of setting 'name' to 'value'.
        """
        self.settings[name] = value
    
    def settingsAsFacts(self, settings):
        """
        Parses a string of settings in the form set(name1, val1), set(name2, val2)...
        """
        pattern = re.compile('set\(([a-zA-Z0-9_]+),(\[a-zA-Z0-9_]+)\)')
        pairs = pattern.findall(settings)
        for name, val in pairs:
            self.set(name, val)
    
    def setPostScript(self, goal, script):
        """
        After learning call the given script using 'goal'.
        """
        self.postGoal = goal
        self.postScript = script
            
    def induce(self, mode, filestem, pos, neg, b):
        """
        Induce a theory in 'mode'.
        
        @param filestem The base name of this experiment.
        @param mode In which mode to induce rules.
        @param pos String of positive examples.
        @param neg String of negative examples.
        @param b String with background knowledge.
        """
        # Write the inputs to appropriate files.
        self.__prepare(filestem, pos, neg, b)

        # Make a script to run aleph (with appropriate settings, stack/heap sizes, ...).
        self.__script(mode, filestem)
    
        logger.info("Running aleph...")

        # Run the aleph script.
        p = Popen(['./' + Aleph.SCRIPT], cwd=Aleph.DIR, stdout=PIPE)
        stdout_str, stderr_str = p.communicate()
        
        logger.debug(stdout_str)
        logger.debug(stderr_str)
        
        logger.info("Done.")
        
        # Return the rules written in the output file.
        rules = open('%s/%s' % (Aleph.DIR, filestem + Aleph.RULES_SUFFIX)).read()

        #shutil.copy('%s/%s.py' % (Aleph.DIR, filestem), '/home/anzev/programiranje/sdm/results/')
        
        # Cleanup.
        self.__cleanup(filestem)
        
        return rules


    def __prepare(self, filestem, pos, neg, b):
        """
        Prepares the needed files.
        """
        posFile = open('%s/%s.f' % (Aleph.DIR, filestem), 'w')
        negFile = open('%s/%s.n' % (Aleph.DIR, filestem), 'w')
        bFile = open('%s/%s.b' % (Aleph.DIR, filestem), 'w')

        posFile.write(pos)
        negFile.write(neg)
        bFile.write(b)
        
        posFile.close()
        negFile.close()
        bFile.close()
        
    def __cleanup(self, filestem):
        """
        Cleans up all the temporary files.
        """
        try:
            os.remove('%s/%s.f' % (Aleph.DIR, filestem))
            os.remove('%s/%s.n' % (Aleph.DIR, filestem))
            os.remove('%s/%s.b' % (Aleph.DIR, filestem))
            os.remove('%s/%s' % (Aleph.DIR, filestem + Aleph.RULES_SUFFIX))
            os.remove('%s/%s' % (Aleph.DIR, Aleph.SCRIPT))
        except:
            logger.info('Problem removing temporary files. The files are probably in use.')
    
    def __script(self, mode, filestem):
        """
        Makes the script file to be run by yap.
        """
        scriptPath = '%s/%s' % (Aleph.DIR, Aleph.SCRIPT)
        script = open(scriptPath, 'w')
        
        #print scriptPath
        
        # Permit the owner to execute and read this script
        os.chmod(scriptPath, S_IREAD | S_IEXEC)
        
        cat = lambda x: script.write(x + '\n')
        cat("#!%s -L -s50000 -h200000" % Aleph.YAP)
        cat(":- initialization(run_aleph).")
        cat("run_aleph :- ")
        cat("consult(aleph),")
        cat("read_all('%s')," % filestem)
        # Cat all the non-default settings
        for setting, value in self.settings.items():
            cat("set(%s, %s)," % (setting, value))
        cat("%s," % mode)
        cat("write_rules('%s')%s" % (filestem + Aleph.RULES_SUFFIX, ',' if self.postScript else '.'))
        if self.postScript:
            cat(self.postGoal + ".")
            cat(self.postScript)
        script.close()
