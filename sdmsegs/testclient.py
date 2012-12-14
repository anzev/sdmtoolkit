'''
Created on Mar 29, 2012

@author: anzev
'''
from pysimplesoap.client import SoapClient, SoapFault
import json
import cPickle

# create a simple consumer
client = SoapClient(
    location = "http://vihar.ijs.si:8081/",
    action = 'http://vihar.ijs.si:8081/', # SOAPAction
    namespace = "http://www.example.com/sdmsegs.wsdl", 
    soap_ns='soap',
    trace = True,
    ns = False)

response = client.sdmsegs(inputData=open('D:/data/bank/bank.tab').read(), 
                          mapping=open('D:/data/bank/bank_map.txt').read(), 
                          ont1=open('D:/data/bank/occupation.owl').read(), 
                          ont2=open('D:/data/bank/banking_services.owl').read(), 
                          ont3=open('D:/data/bank/geography.owl').read(), 
                          legacy=False,
                          dataFormat='tab',
                          posClassVal='Yes')

# extract and convert the returned value
#print response.results
dict = json.loads(str(response.results))
#print dict
#print dict.keys()

cPickle.dump(dict, open('results_example.pkl', 'w'))