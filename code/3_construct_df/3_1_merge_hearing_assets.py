
from __future__ import division
import pandas as pd
import re
import sys
import numpy


# This makes sure python can find liblinear python interface
# Python sometimes has problems finding it, depending on IDE
sys.path.append('/usr/local/lib/python2.7/site-packages/liblinear/python/')


def genFloorControl(dir, file):
    # generate floor control variable
    # Import speeches iteratively b/c of the filesize
    tempframe = pd.read_csv(dir+file+'.csv', iterator=True, chunksize=1000)
    speeches = pd.concat(tempframe, ignore_index=True)
    # cast 'speech' column into string. On import, becomes float ~60K; no idea why
    speeches['speech'] = speeches['speech'].astype(str)
    speeches['words'] = 0
    for i in range(0, len(speeches)):  # Count words in each person's speech
        speeches.loc[i, 'words'] = len(re.findall(r'\w+', speeches.loc[i, 'speech']))
    # Get total of all words spoken in hearing
    speeches = speeches.join(speeches.groupby('filename')['words'].sum(), on='filename', rsuffix='_tot')
    # Create measure of how dominant speakers are in a hearing
    speeches['floor_control'] = speeches['words'] / speeches['words_tot']
    return speeches


def genInteract(dir, file):
    # Creating "interactivity" variable as a measure of back-and-forth
    speakers = pd.read_csv(dir+file+'.csv', header=0)
    speakers = speakers.join(speakers.groupby('filename')['remarks'].sum(), on='filename', rsuffix='_tot')
    speakers = speakers.join(speakers.groupby('filename')['speaker'].count(), on='filename', rsuffix='_tot')
    speakers['interactive'] = speakers['speaker_tot'] / speakers['remarks_tot']
    return speakers


def buildSet(dir, speeches, speakers):
    hmd = pd.read_csv(dir+'hearing_metadata_2.csv', header=0)
    # cleaning and prepping to match with other datasets
     # pull out info buried in other variables
    hmd['filename'] = hmd['filename'].map(lambda x: x.rstrip('.txt'))
    # Extract congress number from hearing variable
    hmd['congress'] = hmd['filename'].map(lambda x: numpy.int(re.findall(r'[+]?\d+', x)[0]))
    # merge parsed hearing results with GPO xml scrape
    gpo = pd.read_csv(dir+'hearing_metadata_1.csv', header=0)
    hmd = pd.merge(hmd, gpo, on='filename', how='inner')
    full = pd.merge(speeches, hmd, on='filename', how='outer')
    full = pd.merge(full, speakers, on=('filename', 'speaker'), how='outer')
    # now add party control/composition variables
    parties = pd.read_csv(dir+'supplemental_data/party_comp_usgov.csv', header=0)
    parties.columns = map(str.lower, parties.columns)
    full = pd.merge(full, parties, on='congress', how='inner')
    return full


def genSpeakerType(full):  # pass in the dataframe with all the metadata
    # read in list of agency names for checking
    ags = [line.rstrip('\n').lower() for line in open('./data/supplemental_data/us_agency_list.txt')]
    '''
    # list of witness columns to check
    witCols = [col for col in full.columns if 'witness' in col]
    longwitlist = []
    for m in range(0,len(witCols)):
        longwitlist = longwitlist + full[witCols[m]].tolist()
        print m
    # now clean up this ridiculously long list
    cleanwitlist = [x for x in longwitlist if str(x) != 'nan']
    cleanwitlist = [x.lower() for x in cleanwitlist]
    '''
    # since I've done the witness list recently, use the next line:
    cleanwitlist = [line.rstrip('\n').lower() for line in open('./data/supplemental_data/witness_list.txt')]
    full['speaker'] = [x.lower() for x in full['speaker']]
    affiliations = {}
    for i in range(len(cleanwitlist)):
        for j in range(len(ags)):
            if ags[j] in cleanwitlist[i]:
                affiliations.append((cleanwitlist[i], ags[j]))
    for k in range(len(full)):
        for m in range(len(affiliations)):
            if full['speaker'][k].split()[1] in affiliations[m][0]:
                full.loc[k, 'affil'] = affiliations[m][1]
        print k, ' out of ', len(full)
    return full


def cleanFull(full, firstCong, lastCong):
    full =  full[(full['congress'] >= firstCong) & (full['congress'] <= lastCong)]
    # Drop observations where there is no hearing number
    # full = full[(full['hearing_number'].isnull() == False)]
    #  drop observations that have no discussion
    full = full.loc[(full['words'] > 0)]
    # "NaN" values interfere with the speciteller code; replace them with single letter
    full = full.replace({'speech': 'NaN'}, {'speech': 'o'})
    return full


if __name__ == '__main__':
    dir = './data/'
    firstCong = 105
    lastCong = 112
    #speeches = genFloorControl(dir, 'speeches')
    #speakers = genInteract(dir, 'speakers')
    #full = buildSet(dir, speeches, speakers)
    full = pd.read_csv('./data/hearing_metadata_3_1.csv', header=0)
    full = genSpeakerType(full)
    #full = cleanFull(full, firstCong, lastCong)
    full.to_csv(dir+'hearing_metadata_3_12.csv', header=True, sep=',')

