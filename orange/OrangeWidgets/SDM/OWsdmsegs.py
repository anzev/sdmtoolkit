# -*- coding: utf-8 -*-
"""
<name>SDM-SEGS</name>
<description>SDM-SEGS system interface.</description>
<icon>icons/WebService.png</icon>
<contact>Anže Vavpetič <anze.vavpetic@ijs.si></contact>
<priority>10</priority>
"""

import sys
import os
import StringIO
import re
from tempfile import NamedTemporaryFile
from time import sleep

from PyQt4 import QtGui
import orange

import ui_gsegs

from webServices.dataSerializer import tableFromString, reprServiceObject
from webServices.stubImporter import importOrangeModule, importZSIstubsFromURI
OWBaseWidget = importOrangeModule('OWBaseWidget', submodule='OWBaseWidget')
ProgressBar = importOrangeModule('OWGUI', submodule='ProgressBar')

class OWsdmsegs(OWBaseWidget):
    settingsList = ['minSizeSG', 'maxNumTerms', 'maxNumSG', 'randomSeed', 'wracc_k', 'legacy', 'maximalPvalue', 'weightFisher', 
                    'weightGSEA', 'weightPAGE', 'summarize', 'cutoff', 'serviceURI', 'lastdir', 'legacy',
                    'level_ont1', 'level_ont2', 'level_ont3', 'level_ont4']
    """
    The SDM-SEGS service widget.
    """
    def __init__(self, parent=None, signalManager=None):
        OWBaseWidget.__init__(self, parent, signalManager, title="SDM-SEGS")
        self.inputs = [("ExampleList", list, self.receiveDataset), ("ExampleTable", orange.ExampleTable, self.receiveDataset), ("Ontology 1", str, self.receiveOnt1), ("Ontology 2", str, self.receiveOnt2), 
                       ("Ontology 3", str, self.receiveOnt3), ("Ontology 4", str, self.receiveOnt4), ("General Terms", str, self.receiveGenTerms),
                       ("InteractionsList", list, self.receiveInteractions), ("InteractionsFile", str, self.receiveInteractionsFile), ("Mapping", str, self.receiveMapping)]
        
        self.outputs = [('Rules', list), ('jobID', str), ('resultsAsXML', str)]
        
        # Set up the user interface from Designer
        self.ui = ui_gsegs.Ui_Form()
        self.ui.setupUi(self)
        self.lastdir = None

        self.ont1 = None
        self.ont2 = None
        self.ont3 = None
        self.ont4 = None
        self.ontologies = [self.ont1, self.ont2, self.ont3, self.ont4]
        self.posClassVal = None
        self.genTerms = []
        self.dataset = None
        self.inputList = None
        self.interactions = None
        self.mapping = None
        self.minSizeSG = 5
        self.maxNumTerms = 3
        self.maxNumSG = 100
        self.randomSeed = 10
        self.wracc_k = 5
        self.legacy = False
        self.maximalPvalue = 0.05
        self.weightFisher = 0
        self.weightGSEA = 1
        self.weightPAGE = 1
        self.summarize = False
        self.cutoff = 300
        self.level_ont1 = 1
        self.level_ont2 = 1
        self.level_ont3 = 1
        self.level_ont4 = 1
        
        self.serviceURI = 'http://vihar.ijs.si:8091/sdmsegs?wsdl'
        self.services = None
        self.server = None
        self.types = None
        self.WSDL = None
        
        # Load the previously defined settings.
        self.loadSettings()

        self.connectSignals()
        self.modifyInterface()

        # center the window
        ch = self.frameGeometry().height()
        cw = self.frameGeometry().width()
        desktop = QtGui.QApplication.instance().desktop()
        w = desktop.screenGeometry(desktop.screenNumber(self)).width()
        h = desktop.screenGeometry(desktop.screenNumber(self)).height()
        self.setGeometry((w-cw)/2, (h-ch)/2, cw, ch)
    
    def connectSignals(self):
        self.ui.okButton.clicked.connect(self.startProcessing) #self.debug)
        self.ui.checkServiceButton.clicked.connect(self.checkService)
        self.ui.minSizeSGSpinBox.valueChanged[int].connect(self.minSizeSGChanged)
        self.ui.maxNumTermsSpinBox.valueChanged[int].connect(self.maxNumTermsChanged)
        self.ui.maxNumSGSpinBox.valueChanged[int].connect(self.maxNumSGChanged)
        self.ui.randomSeedSpinBox.valueChanged[int].connect(self.randomSeedChanged)
        self.ui.kSpinBox.valueChanged[int].connect(self.wracc_kChanged)
        self.ui.classValComboBox.activated[str].connect(self.posClassValChanged)
        self.ui.cutoffSpinBox.valueChanged[int].connect(self.cutoffChanged)
        self.ui.summarizeCheckBox.stateChanged.connect(self.summarizeChanged)
        self.ui.legacyCheckBox.stateChanged.connect(self.legacyChanged)
        self.ui.pValueComboBox.activated[str].connect(self.maximalPvalueChanged)
        self.ui.fisherSpinBox.valueChanged[float].connect(self.weightFisherChanged)
        self.ui.gseaSpinBox.valueChanged[float].connect(self.weightGSEAChanged)
        self.ui.pageSpinBox.valueChanged[float].connect(self.weightPAGEChanged)
        self.ui.labelledRadioButton.toggled.connect(self.labelledToggle)
        self.ui.rankedRadioButton.toggled.connect(self.rankedToggle)
        self.ui.level_ont1SpinBox.valueChanged[int].connect(self.level_ont1Changed)
        self.ui.level_ont2SpinBox.valueChanged[int].connect(self.level_ont2Changed)
        self.ui.level_ont3SpinBox.valueChanged[int].connect(self.level_ont3Changed)
        self.ui.level_ont4SpinBox.valueChanged[int].connect(self.level_ont4Changed)
    
    def labelledToggle(self, checked):
        self.ui.cutoffSpinBox.setEnabled(False)
        self.ui.classValComboBox.setEnabled(True)
    
    def rankedToggle(self, checked):
        self.ui.cutoffSpinBox.setEnabled(True)
        self.ui.classValComboBox.setEnabled(False)
    
    def cutoffChanged(self, value):
        self.cutoff = int(value)
    
    def summarizeChanged(self, value):
        self.summarize = bool(value)
    
    def legacyChanged(self, value):
        self.legacy = bool(value)
        
        self.__toggleLegacy()
    
    def maximalPvalueChanged(self, value):
        self.maximalPvalue = float(value)
    
    def weightFisherChanged(self, value):
        self.weightFisher = float(value)
    
    def weightGSEAChanged(self, value):
        self.weightGSEA = float(value)
    
    def weightPAGEChanged(self, value):
        self.weightPAGE = float(value)
        
    def level_ont1Changed(self, value):
        self.level_ont1 = int(value)
        
    def level_ont2Changed(self, value):
        self.level_ont1 = int(value)
        
    def level_ont3Changed(self, value):
        self.level_ont1 = int(value)
        
    def level_ont4Changed(self, value):
        self.level_ont1 = int(value)
    
    def modifyInterface(self):
        self.ui.serviceLineEdit.setText(self.serviceURI)
        self.ui.minSizeSGSpinBox.setValue(self.minSizeSG)
        self.ui.maxNumTermsSpinBox.setValue(self.maxNumTerms)
        self.ui.maxNumSGSpinBox.setValue(self.maxNumSG)
        self.ui.randomSeedSpinBox.setValue(self.randomSeed)
        self.ui.kSpinBox.setValue(self.wracc_k)
        self.ui.okButton.setEnabled(True)
        
        self.ui.cutoffSpinBox.setValue(self.cutoff)
        self.ui.summarizeCheckBox.setChecked(self.summarize)
        self.ui.legacyCheckBox.setChecked(self.legacy)
        self.ui.pValueComboBox.addItems(['0.05', '0.01', '0.005'])
        self.ui.pValueComboBox.setCurrentIndex(0)
        self.ui.fisherSpinBox.setValue(self.weightFisher)
        self.ui.gseaSpinBox.setValue(self.weightGSEA)
        self.ui.pageSpinBox.setValue(self.weightPAGE)
        
        self.ui.legacyCheckBox.setChecked(self.legacy)

        self.ui.fisherSpinBox.setEnabled(self.legacy)
        self.ui.gseaSpinBox.setEnabled(self.legacy)
        self.ui.pageSpinBox.setEnabled(self.legacy)
        self.ui.pValueComboBox.setEnabled(self.legacy)
        
        self.ui.level_ont1SpinBox.setValue(self.level_ont1)
        self.ui.level_ont2SpinBox.setValue(self.level_ont2)
        self.ui.level_ont3SpinBox.setValue(self.level_ont3)
        self.ui.level_ont4SpinBox.setValue(self.level_ont4)
        
        self.__toggleLegacy()
        
        #if self.exampleTable:        
        #self.__fillClassVals()
        
    def __toggleLegacy(self):
        self.ui.fisherSpinBox.setEnabled(self.legacy)
        self.ui.gseaSpinBox.setEnabled(self.legacy)
        self.ui.pageSpinBox.setEnabled(self.legacy)
        self.ui.pValueComboBox.setEnabled(self.legacy)
    
    def __fillClassVals(self):
        # Just put all the possible class values in the combo box.
        #vals = list(self.exampleTable.domain.classVar.values)
        #vals = set([p[1] for p in self.inputList])
        self.ui.classValComboBox.clear()
        self.ui.classValComboBox.addItems(self.classVals)
        self.ui.classValComboBox.setCurrentIndex(0)
        self.posClassVal = self.classVals[0]
            
    def __executionCheck(self):
        """
        Check if we have the needed information to run the service.
        """
        return self.__ontologySelected() and self.__datasetSelected() and self.__mappingSelected()
    
    def __ontologySelected(self):
        #return any(self.ontologyFiles)
        return any(self.ontologies)
    
    def __datasetSelected(self):
        return self.dataset != None
        
    def __mappingSelected(self):
	return self.mapping != None
        
    def minSizeSGChanged(self, value):
        self.minSizeSG = int(value)
    
    def maxNumTermsChanged(self, value):
        self.maxNumTerms = int(value)
    
    def maxNumSGChanged(self, value):
        self.maxNumSG = int(value)
    
    def randomSeedChanged(self, value):
        self.randomSeed = int(value)
    
    def posClassValChanged(self, value):
        self.posClassVal = str(value)
        
    def wracc_kChanged(self, value):
        self.wracc_k = int(value)

    def receiveGenTerms(self, genTerms):
        if genTerms:            
            self.genTerms = [gt.strip() for gt in genTerms.split('\n')]
        else:
            self.genTerms = []
            
    def selectFile(self, lineEdit, selText='Text file (*.txt *.*)'):
        sd = os.getcwd()  if  not self.lastdir  else  self.lastdir
        fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Select file', sd, selText))
        if fname:
            self.filename = fname
            self.lastdir = os.path.split(self.filename)[0]
            lineEdit.setText(self.filename)
    
    def receiveOnt1(self, ont):
        self.ont1 = ont
        self.ontologies[0] = ont
    
    def receiveOnt2(self, ont):
        self.ont2 = ont
        self.ontologies[1] = ont
    
    def receiveOnt3(self, ont):
        self.ont3 = ont
        self.ontologies[2] = ont
    
    def receiveOnt4(self, ont):
        self.ont4 = ont
        self.ontologies[3] = ont
            
    def receiveDataset(self, data):
        if not data:
            self.dataset = []
            return
        
        if not self.importServiceStubs():
            return
                
        tmp = self.services.runsdmsegsRequest()
        sample = None
        self.classVals = []
        
        if isinstance(data, orange.ExampleTable):
            self.dataset = []
            sample = data[0][1]
            for i, ex in enumerate(data):
                pair = tmp.new_inputData()
                pair.set_element_id(i)
                pair.set_element_rank_or_label(ex[data.domain.classVar].value)
                self.dataset.append(pair)
                
            self.classVals = list(data.domain.classVar.values)
        else:
            # data is a list [..., (id_i, v_i), ...], v_i is either a rank or a label
            self.dataset = []
            sample = data[0][1]
            for e in data:
                try:
                    pair = tmp.new_inputData()
                    pair.set_element_id(int(e[0]))
                    pair.set_element_rank_or_label(str(e[1]))
                    self.dataset.append(pair)
                except:
                    msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Cannot parse input: %s' % str(e), QtGui.QMessageBox.Ok)
                    msgBox.exec_()
                    return
            
            self.classVals = set([p[1] for p in data])
        
        # Try to detect if we have ranked or labelled data
        #sample = self.dataset[0].get_element_rank_or_label()
        if isinstance(sample, float) or isinstance(sample, int):
            self.ui.rankedRadioButton.setChecked(True)            
            self.ui.classValComboBox.setEnabled(False)
        else:
            self.ui.labelledRadioButton.setChecked(True)
            self.__fillClassVals()
            
        self.information('New data have arrived.\nDouble click on the widget to configure and run!')
    
    def receiveInteractions(self, data):
        if not data:
            self.interactions = []
            return
        
        if not self.importServiceStubs():
            return
        
        tmp = self.services.runsdmsegsRequest()
        self.interactions = []
        for e in data:            
            try:
                pair = tmp.new_interactions()
                pair.set_element_id1(e[0])
                pair.set_element_id2(e[1])
                self.interactions.append(pair)
            except:
                msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Cannot parse interaction on line: %s\n If you wish to use legacy SEGS files select the legacy checkbox!' % line, QtGui.QMessageBox.Ok)
                msgBox.exec_()
                return
        
    def receiveInteractionsFile(self, data):
        if not data:
            self.interactions = []
            return
        
        if not self.importServiceStubs():
            return
        
        if self.ui.legacyCheckBox.isChecked():
            # Parse the segs legacy interactions data
            tmp = self.services.runsdmsegsRequest()
            self.interactions = []
            for line in StringIO.StringIO(data):
                try:
                    pyLine = eval(line)
                    id1 = pyLine[0]
                    for id2 in pyLine[1]:
                        pair = tmp.new_interactions()
                        pair.set_element_id1(int(id1))
                        pair.set_element_id2(int(id2))
                        self.interactions.append(pair)
                except:
                    msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Cannot parse interaction on line: %s' % line, QtGui.QMessageBox.Ok)
                    msgBox.exec_()
                    return
        else:
            tmp = self.services.runsdmsegsRequest()
            self.interactions = []
            for line in StringIO.StringIO(data):
                try:
                    id1, id2 = re.match(r'(\d+)\s+(\d+)', line)
                    pair = tmp.new_interactions()
                    pair.set_element_id1(int(id1))
                    pair.set_element_id2(int(id2))
                    self.interactions.append(pair)
                except:
                    msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Cannot parse interaction on line: %s\n If you wish to use legacy SEGS files select the legacy checkbox!' % line, QtGui.QMessageBox.Ok)
                    msgBox.exec_()
                    return
    
    def receiveMapping(self, mapping):
        if not mapping:
            self.mapping = []
            return
        
        if not self.importServiceStubs():
            return
        
        if self.ui.legacyCheckBox.isChecked():
            # Parse legacy map file
            tmp = self.services.runsdmsegsRequest()
            self.mapping = []
            for line in StringIO.StringIO(mapping):
                pyLine = eval(line)
                pair = tmp.new_mapping()
                pair.set_element_id(pyLine[0])
                pair.set_element_uri(pyLine[1])
                self.mapping.append(pair)
        else:
            tmp = self.services.runsdmsegsRequest()
            self.mapping = []
            for line in StringIO.StringIO(mapping):
                try:
                    pair = tmp.new_mapping()
                    items = re.split('\s+', line)
                    pair.set_element_id(int(items[0]))
                    pair.set_element_uri(items[1:])
                    self.mapping.append(pair)
                except:
                    msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Cannot parse mapping on line: %s\n If you wish to use legacy SEGS files select the legacy checkbox!' % line, QtGui.QMessageBox.Ok)
                    msgBox.exec_()
                    return
            
    def startProcessing(self):
        if self.__executionCheck():
            self.close()
            self.execute()
        else:
            if not self.__ontologySelected():
                message = 'You need to select at least one ontology.'
            elif not self.__datasetSelected():
                message = 'You need to provide a dataset.'
            elif not self.__mappingSelected():
                message = 'You need to provide a mapping.'
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Information', message)
            msgBox.exec_()
        
    def importServiceStubs(self):
        from ZSI.wstools.Utility import HTTPResponse
        try:
            self.serviceURI = str(self.ui.serviceLineEdit.text())
            stubs = importZSIstubsFromURI(self.serviceURI)
            self.services, self.server, self.types, self.WSDL = stubs.client, stubs.server, stubs.types, stubs.WSDL
        except BaseException, e:
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Service address error:\n%s' % str(e), QtGui.QMessageBox.Ok)
            msgBox.exec_()
            return False
        except HTTPResponse, e:
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Service address error:\n%s' % str(e.reason), QtGui.QMessageBox.Ok)
            msgBox.exec_()
            return False
        else:
            return True

    def checkService(self):
        from ZSI.wstools.Utility import HTTPResponse
        try:
            self.serviceURI = str(self.ui.serviceLineEdit.text())
            stubs = importZSIstubsFromURI(self.serviceURI)
        except BaseException, e:
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Service address error:\n%s' % str(e), QtGui.QMessageBox.Ok)
            msgBox.exec_()
        except HTTPResponse, e:
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Service address error:\n%s' % str(e.reason), QtGui.QMessageBox.Ok)
            msgBox.exec_()
        else:
            msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Information, 'Info', 'Service is ok.', QtGui.QMessageBox.Ok)
            msgBox.exec_()
    
    def execute(self):
        self.progressBar = ProgressBar(self, iterations=100)
        
        locator = self.services.sdmsegsLocator()
        port = locator.getsdmsegs()

        segsInput = self.ui.legacyCheckBox.isChecked()
        
        if segsInput:
            if len(filter(lambda x: x != None, self.ontologies)) > 1:
                self.error('You have selected SEGS ontology format, but more than 1 ontology is on the input signals. Put the SEGS ontology on ont1 signal.')
                return
            if len(self.ontologies) == 1 and self.ont1 == None:
                # Move the non-empty ontology to ont1
                for ont in ontologies:
                    if ont != None:
                        self.ont1 = ont
                        self.ont2, self.ont3, self.ont4 = None, None, None
                        break
        
        # send a job to the service
        request = self.services.runsdmsegsRequest()
        request.set_element_ont1(self.ont1)
        if self.ont2:
            request.set_element_ont2(self.ont2)
        if self.ont3:
            request.set_element_ont3(self.ont3)
        if self.ont4:
            request.set_element_ont4(self.ont4)
        
        request.set_element_inputData(self.dataset)
        request.set_element_generalTerms(self.genTerms)        
        request.set_element_interactions(self.interactions)
        request.set_element_mapping(self.mapping)
        request.set_element_cutoff(self.cutoff)
        request.set_element_posClassVal(self.posClassVal)
        request.set_element_minimalSetSize(self.minSizeSG)
        request.set_element_maxNumTerms(self.maxNumTerms)
        request.set_element_maxReported(self.maxNumSG)
        request.set_element_wracc_k(self.wracc_k)
        request.set_element_maximalPvalue(self.maximalPvalue)
        request.set_element_weightFisher(self.weightFisher)
        request.set_element_weightGSEA(self.weightGSEA)
        request.set_element_weightPAGE(self.weightPAGE)
        request.set_element_summarizeDescriptions(self.summarize)
        request.set_element_randomSeed(self.randomSeed)
        request.set_element_legacy(segsInput)
        request.set_element_level_ont1(self.level_ont1)
        request.set_element_level_ont2(self.level_ont2)
        request.set_element_level_ont3(self.level_ont3)
        request.set_element_level_ont4(self.level_ont4)
        
        try:
            response = port.runsdmsegs(request)
        except Exception, e:
            self.error('SDM-SEGS service error:\n%s' % str(e))
            return
        jobid = response.get_element_jobID()
        QtGui.qApp.restoreOverrideCursor()

        # query the progress of the job
        request = self.services.getProgressRequest()
        request.set_element_jobID(jobid)
        cnt = 0
        errCnt = 0
        while True:
            if cnt >= 100:
                cnt = 0
                try:
                    newProgress = port.getProgress(request).get_element_progress()
                except IOError, e:
                    errCnt += 1
                    if errCnt >= 24:  #24 * 5s == 2 minutes
                        self.progressBar.finish()
                        self.warning()
                        self.error('Connection lost for more than two minutes.\nJobID: %s' % jobid)
                        return
                    else:
                        self.warning('Internet connection problem.\nCannot get progress from SDM-SEGS service.\nTrying to reconnect...')
                else:
                    errCnt = 0
                    self.warning()

                self.progressBar.count = newProgress-1 #this is because ProgressBar increases it
                self.progressBar.advance()
                if newProgress >= 100:
                    break
            else:
                cnt += 1
                QtGui.qApp.processEvents()
                sleep(0.05)

        request = self.services.getResultRequest()
        request.set_element_jobID(jobid)
        gsegsResult = port.getResult(request)
        self.progressBar.finish()

        self.send('Rules', gsegsResult.get_element_rules())
        self.send('jobID', jobid)
        self.send('resultsAsXML', reprServiceObject(gsegsResult))
        
if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    w = OWsdmsegs()
    w.show()
    a.exec_()
    w.saveSettings()
