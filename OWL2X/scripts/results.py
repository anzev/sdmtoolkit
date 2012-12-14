# -*- coding: utf-8 -*-
"""
Script to convert the SEGS results file into a generic results file.

@author Anže Vavpetič, 2010 <anze.vavpetic@ijs.si>
"""
import sys
import os.path
import re
from OWL2XLogger import logger
from dataInfo import ontMap, posClass

# Original chunk and its translation.
chunks = {
  '<h2>Enriched genesets for class A</h2>' : '<h2>Rules for class: %s.</h2>' % posClass,
  'Proc' : ontMap.get('biological_process', None),
  'Comp' : ontMap.get('cellular_component', None),
  'Func' : ontMap.get('molecular_function', None),
  'Path' : ontMap.get('KEGG_pathway', None),
  '#DE_Genes' : '# of pos',
  '<TD ALIGN="center"><b>GSEA p-value<br>\&nbsp\;\(Enricment score\)&nbsp\;<TD ALIGN="center"><b>\&nbsp\;PAGE p-value\&nbsp\;<br>\(Z-score\)' : ' ',
  r'<a href="http\:\/\/www\.ebi\.ac\.uk\/ego\/DisplayGoTerm\?id\=GO\:[0-9]+">' : '<a href="">',
  r'<a href="\.\.\/tool\.php\?sets\=work\_dir\/bank\&code\=[0-9]+">' : '<a href="">',
  r'<TD ALIGN\=\"center\">    [0-9\.\-]+<br>\&nbsp\;\([\-0-9\.]+\)\&nbsp\;<TD ALIGN\=\"center\">    [0-9\.]+<br>\&nbsp\;\(  -nan\)\&nbsp\;<\/TR>' :'</TR>'
}

def main():
    if len(sys.argv) < 3:
        logger.error("Too few arguments. Usage: python results.py <out_dir> <input>.html")
        
    outDir = sys.argv[1]
    inFile = sys.argv[2]
    try:
        results = open(inFile, 'r')
    except:
        logger.error('Unable to open the input file.')

    # For now just replace some strings.
    html_chunk = results.read()
    
    for chunk in chunks.keys():
        transl = chunks[chunk]
        if transl:
            html_chunk = re.sub(chunk, transl, html_chunk)
    
    try:
        out = open(os.path.normpath('%s/%s' % (outDir, os.path.basename(inFile))), 'w')
    except:
        logger.error('Unable to create output file.')
    
    out.write(html_chunk)

def beautify(inFile, outFile):
    if len(sys.argv) < 3:
        logger.error("Too few arguments. Usage: python results.py <out_dir> <input>.html")
        
    #outDir = sys.argv[1]
    #inFile = sys.argv[2]
    try:
        results = open(inFile, 'r')
    except:
        logger.error('Unable to open the input file.')

    # For now just replace some strings.
    html_chunk = results.read()
    
    for chunk in chunks.keys():
        transl = chunks[chunk]
        if transl:
            html_chunk = re.sub(chunk, transl, html_chunk)
    
    try:
        out = open(outFile, 'w')
    except:
        logger.error('Unable to create output file.')
    
    out.write(html_chunk)
    
if __name__ == '__main__':
    main()