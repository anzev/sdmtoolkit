# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SDMAleph.ui'
#
# Created: Mon Aug 22 15:29:23 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(340, 388)
        self.okButton = QtGui.QPushButton(Form)
        self.okButton.setGeometry(QtCore.QRect(230, 350, 93, 27))
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 321, 61))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.serviceLineEdit = QtGui.QLineEdit(self.groupBox)
        self.serviceLineEdit.setGeometry(QtCore.QRect(10, 20, 271, 27))
        self.serviceLineEdit.setObjectName(_fromUtf8("serviceLineEdit"))
        self.checkServiceButton = QtGui.QPushButton(self.groupBox)
        self.checkServiceButton.setGeometry(QtCore.QRect(290, 20, 21, 27))
        self.checkServiceButton.setObjectName(_fromUtf8("checkServiceButton"))
        self.groupBox_3 = QtGui.QGroupBox(Form)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 70, 321, 91))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.classValComboBox = QtGui.QComboBox(self.groupBox_3)
        self.classValComboBox.setGeometry(QtCore.QRect(170, 50, 121, 31))
        self.classValComboBox.setObjectName(_fromUtf8("classValComboBox"))
        self.label_2 = QtGui.QLabel(self.groupBox_3)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 121, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.rankedRadioButton = QtGui.QRadioButton(self.groupBox_3)
        self.rankedRadioButton.setGeometry(QtCore.QRect(160, 20, 101, 21))
        self.rankedRadioButton.setObjectName(_fromUtf8("rankedRadioButton"))
        self.labelledRadioButton = QtGui.QRadioButton(self.groupBox_3)
        self.labelledRadioButton.setGeometry(QtCore.QRect(40, 20, 101, 21))
        self.labelledRadioButton.setObjectName(_fromUtf8("labelledRadioButton"))
        self.groupBox_4 = QtGui.QGroupBox(Form)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 170, 321, 171))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.label_10 = QtGui.QLabel(self.groupBox_4)
        self.label_10.setGeometry(QtCore.QRect(20, 40, 121, 17))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(self.groupBox_4)
        self.label_11.setGeometry(QtCore.QRect(20, 70, 141, 17))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.minSizeSGSpinBox = QtGui.QSpinBox(self.groupBox_4)
        self.minSizeSGSpinBox.setGeometry(QtCore.QRect(240, 40, 55, 27))
        self.minSizeSGSpinBox.setMinimum(1)
        self.minSizeSGSpinBox.setObjectName(_fromUtf8("minSizeSGSpinBox"))
        self.maxNumTermsSpinBox = QtGui.QSpinBox(self.groupBox_4)
        self.maxNumTermsSpinBox.setGeometry(QtCore.QRect(240, 70, 55, 27))
        self.maxNumTermsSpinBox.setMinimum(1)
        self.maxNumTermsSpinBox.setObjectName(_fromUtf8("maxNumTermsSpinBox"))
        self.label_3 = QtGui.QLabel(self.groupBox_4)
        self.label_3.setGeometry(QtCore.QRect(20, 100, 48, 14))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.cutoffSpinBox = QtGui.QSpinBox(self.groupBox_4)
        self.cutoffSpinBox.setGeometry(QtCore.QRect(240, 100, 55, 27))
        self.cutoffSpinBox.setMinimum(1)
        self.cutoffSpinBox.setMaximum(999)
        self.cutoffSpinBox.setSingleStep(1)
        self.cutoffSpinBox.setProperty(_fromUtf8("value"), 300)
        self.cutoffSpinBox.setObjectName(_fromUtf8("cutoffSpinBox"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "SDM-Aleph", None, QtGui.QApplication.UnicodeUTF8))
        self.okButton.setText(QtGui.QApplication.translate("Form", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Service", None, QtGui.QApplication.UnicodeUTF8))
        self.checkServiceButton.setText(QtGui.QApplication.translate("Form", "?", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Form", "Task", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Target attribute value:", None, QtGui.QApplication.UnicodeUTF8))
        self.rankedRadioButton.setText(QtGui.QApplication.translate("Form", "Ranked data", None, QtGui.QApplication.UnicodeUTF8))
        self.labelledRadioButton.setText(QtGui.QApplication.translate("Form", "Labelled data", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("Form", "Search constraints", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Form", "Min subgroup size", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Form", "Max number of terms", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Cutoff", None, QtGui.QApplication.UnicodeUTF8))

