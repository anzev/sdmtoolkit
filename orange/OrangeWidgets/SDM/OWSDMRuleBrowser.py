"""
<name>SDM Rule Browser</name>
<description>Displays rules in HTML format.</description>
<icon>icons/RuleBrowser.png</icon>
<contact>Anze Vavpetic (anze.vavpetic@ijs.si)</contact>
<priority>40</priority>
"""

import sys
from PyQt4 import QtGui

# Import the Biomine widget.
sys.path.append('../WS_Biomine/')
from pyHTable import PyHtmlTable as pht
from OWRuleBrowser import *

class OWSDMRuleBrowser(OWRuleBrowser):
    """
    This class just overrides the OWRuleBrowser's buildHTMLtable to achieve a more generic visualization.
    """
    def __init__(self, parent=None, signalManager=None, title='Rule browser'):
        OWRuleBrowser.__init__(self, parent, signalManager, title)
        self.fisher = False
        self.inputs = [('rules', list, self.receiveRules)]
        self.outputs = [('termList', list)]
    
    def execute(self):
        self.error()
        if not self.ruleObjectsList:
            # empty table
            table = []
            HTMLtable = self.buildHTMLtable(table, True)
            html = self.constructHTML(HTMLtable)
            self.showHTML(html)
            return

        if self.hClustering:
            idLabel = 'clusterID<br/>(|U|, |I|)'
            clusters = self.collectClusters(self.hClustering, self.hClustering.cutoff, [])
            ruleid2cluster = dict.fromkeys(range(len(clusters)))
            for i in range(len(clusters)):
                ruleid2cluster[i] = []
            #[0]: cluster number
            #[1]: union of genes
            #[2]: intersection of genes (list of all sets, intersection is computed at the end)
            clusterTable = [[[], set(), []] for x in range(len(clusters))]
        else:
            clusters = []
            idLabel = '#'
            ruleid2cluster = None
            clusterTable = None

        try:
            isAleph = True if 'get_element_aggregate_pval' not in dir(self.ruleObjectsList[0]) else False
            isCombined = False
            self.fisher = False           
            
            table = self.allocateTableList(len(self.ruleObjectsList), isCombined)

            for (row, rule) in enumerate(self.ruleObjectsList):
                # first column: indices (test numbers start with 1!) or cluster number
                clNum = self.findRuleCluster(row, clusters)
                table[row][0] = clNum  if clNum != None  else row+1
                if clNum != None:
                    table[row][0] = clNum
                    ruleid2cluster[clNum].append(row)
                else:
                    table[row][0] = row+1

                ruleDescription = rule.get_element_description()
                terms = ruleDescription.get_element_terms()

                # second column: rules (conjuncts)
                TERMids = [x.get_element_termID() for x in terms]
                TERMnames = [x.get_element_name() for x in terms]

                content = ''
                link = ''
                tooltip = ''
                for i in range(0, len(TERMnames)):
                    content += '%s %s' % (TERMnames[i], self.LBREAK)
                    link += "'%s'," % TERMids[i].replace(KEGG_PREFIX, BIOMINE_KEGG_PREFIX_HSA)
                    tooltip += '%s ' % TERMids[i]
                
                if not isAleph:
                    iterms = ruleDescription.get_element_interactingTerms()
                    INTids = [x.get_element_termID() for x in iterms]
                    INTnames = [x.get_element_name() for x in iterms]
                    if INTnames:
                        for i in range(0, len(INTnames)):
                            content += 'INTERACT: %s %s' % (INTnames[i], self.LBREAK)
                            link += "'%s'," % INTids[i].replace(KEGG_PREFIX, BIOMINE_KEGG_PREFIX_HSA)
                            tooltip += '%s ' % INTids[i]
                link = '[%s]' % link[:-1]
                tooltip = tooltip[:-1]
                table[row][1] = '<a title="%s" style="text-decoration: none" href=%s>%s</a>' % (tooltip, link, content)

                # third and fourth column: genes
                allGenes = ['%s%s' % (ENTREZ_PREFIX, x) for x in rule.get_element_coveredGenes()]
                topGenes = ['%s%s' % (ENTREZ_PREFIX, x) for x in rule.get_element_coveredTopGenes()]
                table[row][2] = '<a style="text-decoration: none" href=%s>%d</a>' % \
                     (str(allGenes).replace(' ', ''), len(allGenes))
                table[row][3] = '<a style="text-decoration: none" href=%s>%d</a>' % \
                                      (str(topGenes).replace(' ', ''), len(topGenes))

                # collect union and intersection of DE genes if there is a clustering
                if clusterTable:
                    clusterTable[clNum][0] = clNum
                    clusterTable[clNum][1].update(topGenes)
                    clusterTable[clNum][2].append(topGenes)

                table[row][4] = '%.3f' % round(rule.get_element_wracc(), 3)
            #endfor
        except Exception, e:
            self.error('Error while reading input rules:\n%s' % str(e))
        else:
            if ruleid2cluster != None:
                newTable = []
                for k in sorted(ruleid2cluster.keys()):
                    for i in ruleid2cluster[k]:
                        newTable.append(table[i])
                table = newTable

                # compute intersections of rules in each cluster
                for row in clusterTable:
                    isetGenes = set(row[2][0])
                    for elt in row[2][1:]:
                        isetGenes.intersection_update(elt)
                    row[2] = isetGenes

                # add sizes of union and intersection to the first column (without links)
                for i in range(len(table)):
                    cln = table[i][0]
                    table[i][0] = '<b>%s</b><br/>(%d,%d)' % (cln, len(clusterTable[cln][1]), len(clusterTable[cln][2]))

                # format cluster table (create links)
                for row in clusterTable:
                    row[1] = '<a style="text-decoration: none" href=%s>%d</a>' % \
                       (str(list(row[1])).replace(' ', ''), len(row[1]))
                    row[2] = '<a style="text-decoration: none" href=%s>%d</a>' % \
                       (str(list(row[2])).replace(' ', ''), len(row[2]))

            HTMLtable = self.buildHTMLtable(table, isCombined, idLabel=idLabel)
            HTMLclusterTable = self.buildHTMLclusterTable(clusterTable)  if  clusters  else None
            html = self.constructHTML(HTMLtable, HTMLclusterTable)
            self.showHTML(html)
            self.information('New data have arrived.\nDouble click on the widget to browse the results!')
    #end        
        
    def buildHTMLtable(self, tableData, isCombined, idLabel='#'):
        ncols = 5
        nrows = len(tableData)
        table = pht.PyHtmlTable(nrows+1, ncols, {'border':1, 'align':'center', 'cellpadding':5})
        table.setCellcontents(0, 0, idLabel)
        table.setCellcontents(0, 1, 'Description')
        table.setCellcontents(0, 2, 'Covered examples')
        table.setCellcontents(0, 3, 'Positive examples')
        table.setCellcontents(0, 4, 'WRAcc')
            
        for i in range(ncols):
            table.setCellattrs(0, i, {'bgcolor':'orange', 'align':'center'})

        for i in xrange(nrows):
            for j in xrange(ncols):
                table.setCellcontents(i+1, j, tableData[i][j])
                table.setCellattrs(i+1, j, {'align':'center'})
                table.setCellattrs(i+1, 1, {'align':'left'})

        return table
    #end
    

if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    w = OWRuleBrowser()
    w.show()
    a.exec_()
