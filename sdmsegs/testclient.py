'''
Created on Mar 29, 2012

@author: anzev
'''
from pysimplesoap.client import SoapClient, SoapFault
import json
import cPickle

# create a simple consumer
client = SoapClient(
    location = "http://localhost:8081/",
    action = 'http://localhost:8081/', # SOAPAction
    namespace = "http://www.example.com/sdmsegs.wsdl", 
    soap_ns='soap',
    trace = True,
    ns = False)

response = client.sdmsegs(inputData=open('../testdata/owl/bank.tab').read(), 
                          mapping=open('../testdata/owl/bank_map.txt').read(), 
                          ont1=open('../testdata/owl/occupation.owl').read(), 
                          ont2=open('../testdata/owl/banking_services.owl').read(), 
                          ont3=open('../testdata/owl/geography.owl').read(), 
                          #legacy=False,
                          #dataFormat='tab',
                          posClassVal='Yes')

d = json.loads(str(response.rules))
print d
cPickle.dump(d, open('results_example.pkl', 'w'))