import re
import sys
import numpy
import nltk
import os
import pandas as pd
import time


# This makes sure python can find liblinear python interface
# Python sometimes has problems finding it, depending on IDE
sys.path.append('/usr/local/lib/python2.7/site-packages/liblinear/python/')

baseDir = './data/'


def buildTextFile(df):
    outText = []
    counter = 0
    # identify the speaker's lines
    # count along the index since the df is passed in with it, and it is how I have to
    for k in df.index:
        # get the speaker's total number of sentences
        try:
            df.loc[k,'numSent'] = len(sent_detect.tokenize(str(df.speech[k])))
        except UnicodeDecodeError:
            df.loc[k,'numSent'] = len(sent_detect.tokenize(str(df.speech[k]).decode('utf8').encode('ascii','xmlcharrefreplace')))
            print "Got a unicode error"
        # now append these sentences to the list
        # with \n so the last sentence of speaker i isn't concatenated w/ 1st sentence of speaker i+1
        try:
            outText.append('\n'.join(item for item in sent_detect.tokenize(str(df.speech[k]).decode('utf8').encode('ascii', 'xmlcharrefreplace')))+'\n')
        except TypeError:
            outText.append('.\n')
            df.loc[k, 'numSent'] = '.'
            print "Got a type error"
            continue
        # counter += 1
        # print counter, k
    fout = open(baseDir+'text.txt', 'w+')
    fout.writelines(outText)
    fout.close()
    return df

def calcSpec(fileName):
    specTime = time.time()
    os.system('python ./data/3_construct_df/speciteller/speciteller.py --inputfile %s --outputfile ./data/probs.txt' % fileName)
    return fileName

def calcAvgSpec(df):
    # read in text file to get word counts
    g = open(baseDir+'text.txt', 'r+')
    gText = g.readlines()
    g.close()
    # read in the list of specificity values (posterior probabilities)
    probs = pd.read_csv(baseDir+'probs.txt', header=None)
    lastSentUsed = 0
    counter = 0
    # count along the index since the df is passed in with it, since that is how I have to
    # identify the speaker's lines
    for speaker in df.index:
        sumSpec = 0
        if df['numSent'][speaker] > 0:
            for sentNum in range(lastSentUsed, lastSentUsed+df['numSent'][speaker]):
                # count words in the sentences, gives |s|
                count = len(re.findall(r'\w+', gText[sentNum]))
                # mult to get one value of second term in word-avg-spec formula
                sentSpec = count*probs.loc[sentNum,0]
                sumSpec += sentSpec
                # this is a counter to work through the list of sentences
                # only get those sentences for the specific speaker
                lastSentUsed += 1
        # already have denominator for formula fraction = all words person spoke
        df.loc[speaker, 'speakerSpec'] = numpy.float32((1.00/(df.loc[speaker, 'words'])))*sumSpec
    return df

if __name__ == '__main__':
    testimony = pd.read_csv(baseDir+'hearings_with_chairs.csv', index_col=0, header=0, dtype={'committee': str, 'speech': str})
    sent_detect = nltk.data.load('tokenizers/punkt/english.pickle')
    testimony['speakerSpec'] = 0
    testimony['numSent'] = 0
    testimony = testimony.loc[(testimony['congress'] == 109)]
    combined = pd.DataFrame()
    for i in testimony['congress'].unique():
        for j in testimony['chamber'].unique():
            congChamberTime = time.time()
            df = testimony.loc[(testimony['congress'] == i) & (testimony['chamber'] == j)]
            buildTextFile(df)
            calcSpec(baseDir+'text.txt')
            calcAvgSpec(df)
            df.loc[:,'congChamber'] = str(i)+'_'+str(j)
            combined = pd.concat([combined, df])
            df.to_csv(baseDir+'chamber_by_congress/'+str(i)+'_'+str(j)+'.csv', header=True)
    combined.to_csv(baseDir+'hearings_with_specifs.csv', header=True)
