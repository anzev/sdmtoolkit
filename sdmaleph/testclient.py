from pysimplesoap.client import SoapClient, SoapFault
import json
import cPickle

# create a simple consumer
client = SoapClient(
    location = "http://localhost:8082/",
    action = 'http://localhost:8082/', # SOAPAction
    namespace = "http://www.example.com/sdmaleph.wsdl", 
    soap_ns='soap',
    trace = True,
    ns = False)

response = client.sdmaleph(examples=open('../testdata/owl/bank.tab').read(), 
                          mapping=open('../testdata/owl/bank_map.txt').read(), 
                          #ontology=open('../testdata/owl/geography.owl').read(),
                          ontologies=[
                            {'ontology' : open('../testdata/owl/occupation.owl').read()},
                            {'ontology' : open('../testdata/owl/banking_services.owl').read()}, 
                            {'ontology' : open('../testdata/owl/geography.owl').read()}], 
                          #relations=[{'relation' : '[1, [2,3,4]]\n[2, [3,4]]'}],
                          dataFormat='tab',
                          posClassVal='Yes')

# extract and convert the returned value
print response.theory
#dict = json.loads(str(response.results))
#cPickle.dump(dict, open('results_example.pkl', 'w'))