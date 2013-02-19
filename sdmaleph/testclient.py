from pysimplesoap.client import SoapClient, SoapFault
import json
import cPickle

# create a simple consumer
client = SoapClient(
    location = "http://vihar.ijs.si:8097/",
    action = 'http://vihar.ijs.si:8097/', # SOAPAction
    #location = "http://localhost:8082/",
    #action = 'http://localhost:8082/', # SOAPAction
    namespace = "http://www.example.com/sdmaleph.wsdl", 
    soap_ns='soap',
    trace = True,
    ns = False)

response = client.sdmaleph(examples=open('../testdata/owl/bank.tab').read(), 
                          mapping=open('../testdata/owl/bank_map.txt').read(), 
                          ontologies=[
                            {'ontology' : open('../testdata/owl/occupation.owl').read()},
                            {'ontology' : open('../testdata/owl/banking_services.owl').read()}, 
                            {'ontology' : open('../testdata/owl/geography.owl').read()}], 
                          dataFormat='tab',
                          posClassVal='Yes')

print response.theory