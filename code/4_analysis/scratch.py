__author__ = 'ian'

import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm



hmj['chamber'] = 0
for i in hmj.index:
    if 'shrg' in hmj.loc[i, 'filename']:
        hmj.loc[i, 'chamber'] = 1
print i


dels = ['USCode', 'bill.', 'Unnam', 'witness', 'V', 'held', 'congMember', 'title', 'roleT', 'statute', 'congHearing', \
        'congDoc', 'cfr', 'agency.', 'partNum', 'nominee', 'law', 'context', 'Serial', 'congReport', 'congComm', \
        'congress.']

for i in dels:
    drops = [c for c in hmd.columns if str(i) in c]
    hmd = hmd.drop(drops, axis=1)

# clear out places where affil is empty
hmf = hm[(hm['affil'].notnull())]

h = pd.read_csv('./data/testimony_mt_df.new.csv', header=0, index_col=0)

#########################################################################

df = pd.read_csv('./data/testimony_df.csv', header=0, index_col=0)

# first subset: Congress 111, House, Finance Committee

hfin111 = df[(df['congress']==111) & (df['chamber']=='House') & (df['committee'].str.contains("financial|FINANCIAL"))]

# just to test a plot
hfin111['speakerSpec'].plot(kind='hist')

# let's try a model. gulp
y = hfin111['speakerSpec']
x = hfin111['interactive']
X = sm.add_constant(x)


est1 = sm.OLS(hfin111['speakerSpec'],sm.add_constant(hfin111['interactive'])).fit()
est1.summary()
# should i cluster on the hearing? probably
est2 = sm.OLS(hfin111['speakerSpec'],sm.add_constant(hfin111['interactive'])).fit(cov_type='cluster', cov_kwds={'groups': hfin111['hearing']})
est2.summary()

h110 = df[(df['congress'] == 110) & (df['chamber']=='House')]
end = h110['speakerSpec']
ex = h110['house_committee_seniority']
X = sm.add_constant(ex)

model = sm.OLS(y,X).fit()