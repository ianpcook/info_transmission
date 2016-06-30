import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
import statsmodels.api as sma
from statsmodels.iolib.summary2 import summary_col

# bring in the working datafame (hearing data --> "hd")
hd = pd.read_csv('./data/working_df.csv', header=0)

# create the measure of ideological distance between the chair and the speaker
# Note: the "ag_ideal" is the agency ideal point as a measure of the speaker's ideal point
hd['ideoDiff'] = np.absolute(hd['ag_ideal'] - hd['dw1'])

# bring in the speaker specificities
def mergeSpeakerSpecs(df):
    specs = pd.read_csv('./data/hearings_with_specifs.csv', header=0, usecols=['speakerSpec', 'congress', 'speaker', 'filename'])
    specs['speaker'] = [x.lower() for x in specs['speaker'].astype(str)]
    specs['filename'] = specs['filename'].map(lambda x: x.rstrip('.txt'))
    df  = pd.merge(df, specs, on=['filename', 'speaker'], how='inner')
    # get rid of one congress col and fix the remaining congress col
    del df['congress_y']
    df.rename(columns={'congress_x' : 'congress'}, inplace=True)
    return df

# zscore across the entire sample (between congress -- "bc")
hd.rename(columns={'speakerSpec_x' : 'speakerSpec'}, inplace=True)
hd['bc_specZ'] = stats.zscore(hd['speakerSpec'])

# zscore in just one session (within congress -- "wc")

def withinCongressZscore(df):
    df_z = []
    for i in df['congress'].unique():
        group = df[(df['congress']==i)]
        group['wc_zscore'] = (group['speakerSpec'] - group['speakerSpec'].mean())/group['speakerSpec'].std(ddof=0)
        df_z = df_z + list(group['wc_zscore'])
    df['wc_specZ'] = df_z
    return df

# create a divided gov variable (chair of different party than president)
# expectation: specificity should go up under div gov because of the ally principle
hd['divgov'] = np.absolute(hd['party_x']/100 - hd['pres_party'])
hd.rename(columns={'committee seniority': 'seniority'}, inplace=True)

# square the predictor of interest
hd['ideoSq'] = np.square(hd['ideoDiff'])

def genMajStrength(hd):
    for i in range(len(hd)):
        if hd.loc[i, 'chamber'] == 0:
            hd.loc[i, 'majStrength'] = np.absolute(hd.loc[i, 'hdems'] - hd.loc[i, 'hreps'])
        elif hd.loc[i, 'chamber'] == 1:
            hd.loc[i, 'majStrength'] = np.absolute(hd.loc[i, 'sdems'] - hd.loc[i, 'sreps'])
        else:
            hd.loc[i, 'majStrength'] == 0
        print i
    return hd


# final trim of the dataset to get rid of remaining columns that do not contribute
hd = hd.loc[:,hd.count() > 0]

# summary stats and graphics for DV (to be included in appendix)
hcounts = hd.groupby(['congress', 'chamber'])['hearing'].count()
hcounts_tex = pd.DataFrame(hcounts).to_latex()
print hcounts_tex

# largest distances between agency representative ideal points
ag_dist = hd.groupby(hd.hearing).ag_ideal.max() - hd.groupby(hd.hearing).ag_ideal.min()
ag_dist = ag_dist.to_frame()
plt.figure()
distplot = ag_dist.plot(kind='hist', bins=100, alpha=0.5, colormap='cubehelix', legend=False)
distplot.set_xlabel('Maximum Ideological Difference Between Agency Representatives within Hearings')
plt.show()
plt.savefig('./manuscript/floats/ag_dist.pdf')

plt.figure()
plt.xlim(0,1)
ss = hd['speakerSpec'].plot(kind='hist', bins=40, alpha=0.5, colormap='cubehelix')
ss.set_xlabel('Raw Speaker Specificity Score')
plt.show()
plt.savefig('./manuscript/floats/speakerspec_hist.pdf')

plt.figure()
ax = hd['wc_specZ'].plot(kind='hist', bins=40, alpha=0.5, colormap='cubehelix')
ax.set_xlabel('Within-Congress Specificity Z-Score')
plt.show()
plt.savefig('./manuscript/floats/wc_spec_hist.pdf')

# summary stats for key IVs
ivs = hd[['ideoDiff', 'majStrength', 'interactive', 'seniority']].describe().transpose()
ivs_df = pd.DataFrame(ivs)
def f1(x):
    return '%1.2f' % x
print ivs_df.to_latex()

# let's run a model. gulp.
# this is the untransformed dep variable
est0 = sm.ols(formula='speakerSpec ~ ideoDiff', missing='drop', data=hd).fit()
est0.summary()
predict = est0.predict()


# now use the transformed, within-congress ("wc") specificity as DV
est1 = sm.ols(formula='wc_specZ ~ ideoDiff', missing='drop', data=hd).fit()
est1.summary()
est1.mse_resid
est1.mse_total
est2 = sm.ols(formula='wc_specZ ~ ideoDiff + seniority', missing='drop', data=hd).fit()
est2.summary()

# using the between-congress ("bc") specificity as DV
est2 = sm.ols(formula='bc_specZ ~ ideoDiff', missing='drop', data=hd).fit()
est2.summary()
print summary_col([est0, est1, est2], stars=True, float_format='%0.2f', info_dict={'N':lambda x: "{0:d}".format(int(x.nobs)),'R2': lambda x: "{:.2f}".format(x.rsquared)}).as_latex()

est3 = sm.ols(formula='wc_specZ ~ seniority ', missing='drop', data=hd).fit()
est3.summary()

est4 = sm.ols(formula='bc_specZ ~ seniority', missing='drop', data=hd).fit()
est4.summary()
print summary_col([est3, est4], stars=True, float_format='%0.2f', info_dict={'N':lambda x: "{0:d}".format(int(x.nobs)),'R2': lambda x: "{:.2f}".format(x.rsquared)}).as_latex()

# using the wc DV, but with more variables for robustness check
est5 = sm.ols(formula='wc_specZ ~ ideoDiff + divgov + interactive + seniority', missing='drop', data=hd).fit()
est5.summary()

# using the between-congress ("bc") specificity as DV
est4 = sm.ols(formula='bc_specZ ~ ideoDiff', missing='drop', data=hd).fit()
est4.summary()

# using bc DV, but with more varibles for robustness check
est5 = sm.ols(formula='bc_specZ ~ ideoDiff + divgov + interactive + seniority', missing='drop', data=hd).fit()
est5.summary()

print summary_col([est0, est1, est2, est3, est4], stars=True, float_format='%0.2f').as_latex()

# check to see if the relationship holds for just one chamber
hdsen = hd[(hd['chamber'] == 1)
est_sen0 = sm.ols(formula='wc_specZ ~ ideoDiff', missing='drop', data=hdsen).fit()
est_sen0.summary()

hdhouse = hd[(hd['chamber'] == 0)]
est_house0 = sm.ols(formula='wc_specZ ~ ideoDiff', missing='drop', data=hdhouse).fit(
est_house0.summary()

print summary_col([est_house0, est_sen0], stars=True, float_format='%0.2f', model_names=['House', 'Senate'], info_dict={'N':lambda x: "{0:d}".format(int(x.nobs)),'R2': lambda x: "{:.2f}".format(x.rsquared)}).as_latex()

# build table of results for Moderating Relationship section
# first, create dummy vars from ag_ideal, since these are equal across agencies, so they
# can be used as agency dummies
# then they can be used as agency fixed effects
hd['ag_cat'] = pd.Categorical(hd.ag_ideal).codes

est_mod0 = sm.ols(formula='wc_specZ ~ ideoDiff + ag_cat', missing='drop', data=hd).fit()
est_mod1 = sm.ols(formula='wc_specZ ~ ideoDiff + seniority + ag_cat', missing='drop', data=hd).fit()
est_mod2 = sm.ols(formula='wc_specZ ~ ideoDiff + seniority + divgov + ag_cat', missing='drop', data=hd).fit()
est_mod3 = sm.ols(formula='wc_specZ ~ ideoDiff + seniority + divgov + majStrength + ag_cat', missing='drop', data=hd).fit()
est_mod4 = sm.ols(formula='wc_specZ ~ ideoDiff + seniority + divgov + majStrength + interactive + ag_cat', missing='drop', data=hd).fit()

print summary_col([est_mod0, est_mod1, est_mod2, est_mod3, est_mod4], stars=True, float_format='%0.3f', model_names=['1', '2', '3', '4', '5'], info_dict={'N':lambda x: "{0:d}".format(int(x.nobs)),'R2': lambda x: "{:.3f}".format(x.rsquared)}).as_latex()

hd['ag_cat'] = pd.Categorical(hd.ag_ideal).codes
est_mod4 = sm.ols(formula='wc_specZ ~ ideoDiff + seniority + divgov + majStrength + interactive + ag_cat', missing='drop', data=hd).fit()
# Scratch below this
model = sm.ols(formula='wc_specZ ~ ideoDiff + seniority + divgov', missing='drop', data=hd).fit()
resid = model.resid
stats.normaltest(resid)

plt.hist(fitted.mse_resid)
fig = plt.figure(figsize=(12,8))
fig = sma.graphics.plot_partregress_grid(model, fig=fig)
fig = sma.graphics.plot_regress_exog(model, 'ideoDiff', fig=fig)
modh.summary()
