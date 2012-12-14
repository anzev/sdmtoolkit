#
# Example of using sdmsegs for legacy segs data.
# 
import cPickle
import random

from sdmsegs.sdmsegs import sdmsegs

data = 'testdata/'
sample = 300

# Read experimental data.
ranks = cPickle.load(open(data + 'all_scores.pkl'))
de = ranks[:sample]
not_de = random.sample(ranks[sample:], sample)

# Read ontology definition.
ontology = open(data + 'ont').read()

# Read mapping.
mapping = []
for line in open(data + 'g2ont'):
    mapping.append(eval(line))
    
# Read interactions.
interactions = []
for line in open(data + 'g2g'):
    interactions.append(eval(line))

runner = sdmsegs()
result = runner.run('progress.txt', 
                de + not_de,
                interactions,
                mapping,
                ontology,
                legacy = True,          # The ontology is in the legacy format.
                cutoff = sample, 
                minimalSetSize = 30,    # Specify the minimum subgroup size.
                maxReported = 20        # Return top 20 rules.
                )
