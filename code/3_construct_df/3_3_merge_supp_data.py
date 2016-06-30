import pandas as pd
import numpy
import re
from fuzzywuzzy import process


def mergeChairMetaData(df1, chairs):
    df1['congress'] = df1['hearing'].map(lambda x: numpy.int(re.findall(r'[+]?\d+', x)[0]))
    chairs.columns = map(str.lower, chairs.columns)
    senateChairs = chairs[chairs['chamber'] == 1]
    houseChairs = chairs[chairs['chamber'] == 0]
    for i in range(len(df1)):
        if df1.loc[i, 'chamber'] == 0:
            df1.loc[i, 'committee name'] = process.extractOne(df1.loc[i, 'comShortName'], \
                                                              list(houseChairs['committee name'].unique()))[0]
        else:
            df1.loc[i, 'committee name'] = process.extractOne(df1.loc[i, 'comShortName'], \
                                                              list(senateChairs['committee name'].unique()))[0]
        print i
    df1.to_csv('./data/df1.csv', header=True)
    chairDF = pd.merge(chairs, df1, on=['congress', 'committee name', 'chamber'], how='inner')
    return chairDF

def mergeAgencyIdealPoints(df, cjags):
    # reshape the Chen data from wide to long
    cjags_l = pd.melt(cjags, id_vars=['agency'], var_name='congress', value_name='ag_ideal')
    # strip leading and trailing whitespace to improve matching
    cjags_l['agency'] = cjags_l['agency'].map(lambda x: x.lstrip().rstrip())
    df['affil'] = df['affil'].map(lambda x: x.lstrip().rstrip())
    # the congress variable comes in as a str; convert to int
    cjags_l['congress'] = cjags_l['congress'].apply(numpy.int)
    # and make the congress var in the target df an int; int64 messes up the merge
    df['congress'] = df['congress'].apply(numpy.int)
    # rename column so it matches the dataframe I want to merge it with
    cjags_l.rename(columns={'agency': 'affil'}, inplace=True)
    df1 = pd.merge(df, cjags_l, on=['affil', 'congress'], how='inner')
    return df1

def mergeChairIdealPoints(df):
    scores = pd.read_csv('./data/supplemental_data/HANDSL01113C20_BSSE.csv', header=None, usecols=[0,1,5,6,7], names=['congress', 'idno', 'party', 'name', 'dw1'])
    # drop congresses I don't need
    scores = scores[(scores['congress']>104)]
    # get names to match across sets
    df = df.rename(columns={'id #' : 'idno'})
    df1  = pd.merge(df, scores, on=['idno', 'congress'], how='inner')
    return df1

if __name__ == '__main__':
    df = pd.read_csv('./data/hearing_metadata_2', header=0)
    chairs = pd.read_csv('./data/supplemental_data/chairs.csv', header=0)
    cjags = pd.read_csv('./data/supplemental_data/Chen_Johnson_AgencyIdealPoints.JTP.csv', header=0, index_col=0, dtype={'agency' : 'str'})
    hmd_chairs = mergeChairMetaData(df, chairs)
    hmd_ags = mergeAgencyIdealPoints(hmd_chairs, cjags)
    hmd_ideal = mergeChairIdealPoints(hmd_ags, )
    print hmd_chairs.shape
    print hmd_chairs['name'].head()
    hmd_chairs.to_csv('./data/hmdc.csv', header=True)
