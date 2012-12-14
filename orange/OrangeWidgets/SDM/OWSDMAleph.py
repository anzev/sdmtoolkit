# -*- coding: utf-8 -*-
"""
<name>SDM-Aleph</name>
<description>SDM-Aleph system interface.</description>
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

import ui_SDMAleph

from webServices.dataSerializer import tableFromString, reprServiceObject
from webServices.stubImporter import importOrangeModule, importZSIstubsFromURI
OWBaseWidget = importOrangeModule('OWBaseWidget', submodule='OWBaseWidget')
ProgressBar = importOrangeModule('OWGUI', submodule='ProgressBar')

class OWSDMAleph(OWBaseWidget):
    """
    SDM-Aleph widget.
    """
    settingsList = ['minSetSize', 'maxNumTerms', 'cutoff', 'serviceURI', 'lastdir']
    def __init__(self, parent=None, signalManager=None):
        OWBaseWidget.__init__(self, parent, signalManager, title="SDM-Aleph")
        self.inputs = [("ExampleList", list, self.receiveDataset), ("ExampleTable", orange.ExampleTable, self.receiveDataset), ("Ontologies", list, self.receiveOntologies),
                       ("Relations", list, self.receiveRelations), ("Mapping", str, self.receiveMapping)]
        self.outputs = [("Rules", list)]
        # Set up the user interface from Designer
        self.ui = ui_SDMAleph.Ui_Form()
        self.ui.setupUi(self)
        self.lastdir = None        
        
        self.dataset = None
        self.examples = []
        self.ontologies = []
        self.relations = []
        
        self.posClassVal = None
        self.mapping = None
        self.minSetSize = 15
        self.maxNumTerms = 4
        self.cutoff = 300
        
        self.serviceURI = 'http://localhost:8090/sdmaleph/?wsdl'
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
        self.ui.minSizeSGSpinBox.valueChanged[int].connect(self.minSetSizeChanged)
        self.ui.maxNumTermsSpinBox.valueChanged[int].connect(self.maxNumTermsChanged)
        self.ui.classValComboBox.activated[str].connect(self.posClassValChanged)
        self.ui.cutoffSpinBox.valueChanged[int].connect(self.cutoffChanged)
        self.ui.labelledRadioButton.toggled.connect(self.labelledToggle)
        self.ui.rankedRadioButton.toggled.connect(self.rankedToggle)
        
    def labelledToggle(self, checked):
        self.ui.cutoffSpinBox.setEnabled(False)
        self.ui.classValComboBox.setEnabled(True)
    
    def rankedToggle(self, checked):
        self.ui.cutoffSpinBox.setEnabled(True)
        self.ui.classValComboBox.setEnabled(False)
    
    def cutoffChanged(self, value):
        self.cutoff = int(value)

    def posClassValChanged(self, value):
        self.posClassVal = str(value)
        
    def modifyInterface(self):
        self.ui.serviceLineEdit.setText(self.serviceURI)
        self.ui.minSizeSGSpinBox.setValue(self.minSetSize)
        self.ui.maxNumTermsSpinBox.setValue(self.maxNumTerms)
        self.ui.cutoffSpinBox.setValue(self.cutoff)
        self.ui.okButton.setEnabled(True)
        
    def __fillClassVals(self):
        # Just put all the possible class values in the combo box.
        self.ui.classValComboBox.clear()
        self.ui.classValComboBox.addItems(self.classVals)
        self.ui.classValComboBox.setCurrentIndex(0)
        self.posClassVal = self.classVals[0]
        
    def __executionCheck(self):
        """
        Check if we have the needed information to run the service.
        """
        return self.__ontologySelected() and self.__datasetSelected()
    
    def __ontologySelected(self):
        #return any(self.ontologyFiles)
        return any(self.ontologies)
    
    def __datasetSelected(self):
        return self.dataset != None
        
    def minSetSizeChanged(self, value):
        self.minSetSize = int(value)
    
    def maxNumTermsChanged(self, value):
        self.maxNumTerms = int(value)
    
    def receiveOntologies(self, ontologiesList):
        self.ontologies = ontologiesList
        
    def receiveDataset(self, data):
        if not data:
            self.dataset = []
            return
        
        if not self.importServiceStubs():
            return
                
        tmp = self.services.induceRequest()
        sample = None
        self.classVals = []
        
        if isinstance(data, orange.ExampleTable):
            self.dataset = []
            sample = data[0][1]
            for i, ex in enumerate(data):
                pair = tmp.new_examples()
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
                    pair = tmp.new_examples()
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
        
    def receiveMapping(self, mapping):
        if not mapping:
            self.mapping = []
            return
        
        if not self.importServiceStubs():
            return
        
        # Parse legacy map file
        tmp = self.services.induceRequest()
        self.mapping = []
        for line in StringIO.StringIO(mapping):
            try:
                pyLine = eval(line)
                pair = tmp.new_mapping()
                pair.set_element_id(pyLine[0])
                pair.set_element_uri(pyLine[1])
                self.mapping.append(pair)
            except SyntaxError:
                pair = tmp.new_mapping()
                items = re.split('\s+', line)
                pair.set_element_id(int(items[0]))
                pair.set_element_uri(items[1:])
                self.mapping.append(pair)
            except:
                msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical, 'Error', 'Cannot parse mapping on line: %s\n' % line, QtGui.QMessageBox.Ok)
                msgBox.exec_()
                return                
    
    def receiveRelations(self, relationsList):
        if not self.importServiceStubs():
            return
        
        tmp = self.services.induceRequest()
        self.relations = []
        for rel in relationsList:
            relation = tmp.new_relation()
            rel_lines = rel.split('\n')
            name = rel_lines[0].strip()
            for line in re_lines[1:]:
                try:
                    pyLine = eval(line)
                    id1 = pyLine[0]
                    for id2 in pyLine[1]:
                        pair = tmp.new_extension()
                        pair.set_element_id1(int(id1))
                        pair.set_element_id2(int(id2))
                        relation.append(pair)
                except SyntaxError:
                    id1, id2 = re.match(r'(\d+)\s+(\d+)', line)
                    pair = tmp.new_extension()
                    pair.set_element_id1(int(id1))
                    pair.set_element_id2(int(id2))
                    relation.append(pair)
                    
            self.relations.append(relation)
                
    def startProcessing(self):
        if self.__executionCheck():
            self.close()
            self.execute()
        else:
            if not self.__ontologySelected():
                message = 'You need to select at least one ontology.'
            elif not self.__datasetSelected():
                message = 'You need to provide a dataset.'
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
        
        locator = self.services.sdmalephLocator()
        port = locator.getsdmaleph()
        
        # send a job to the service
        request = self.services.induceRequest()
        request.set_element_ontologies(self.ontologies)
        request.set_element_examples(self.dataset)
        request.set_element_relations(self.relations)
        request.set_element_mapping(self.mapping)
        if self.ui.rankedRadioButton.isChecked():
            request.set_element_cutoff(self.cutoff)
        else:
            request.set_element_posClassVal(self.posClassVal)
        request.set_element_minimalSetSize(self.minSetSize)
        request.set_element_maxNumTerms(self.maxNumTerms)
        
        try:
            response = port.induce(request)
        except Exception, e:
            self.error('SDM-Aleph service error:\n%s' % str(e))
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
                        self.warning('Internet connection problem.\nCannot get progress from SDM-Aleph service.\nTrying to reconnect...')
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
        result = port.getResult(request)
        self.progressBar.finish()

        self.send('Rules', result.get_element_rules())
        
if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    w = OWSDMAleph()
    w.show()
    a.exec_()
    w.saveSettings()
