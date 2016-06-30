from __future__ import division
import pandas as pd
import nltk

'''
This file checks speeches for positive and negative words to get a
sense of the attitude of the speaker.
'''

'''
Used the first time to get the lists. Uncomment this section if
you need to refresh the pos/neg lists or the files from the
assets folder are lost/missing.

Requires internet connection

import urllib

# get Neal Caren's lists of pos/neg words

files=['negative.txt','positive.txt']
path='http://www.unc.edu/~ncaren/haphazard/'
for file_name in files:
    urllib.urlretrieve(path+file_name,file_name)
    text_file = open('../assets/'+file_name, 'w+')
    text_file.write(open(file_name).read())
    text_file.close()
'''

# Get pos/neg files, split into useful lists
pos = open("./data/sentiment/positive.txt").read()
neg = open("./data/sentiment/negative.txt").read()

posWords = pos.split('\n')
negWords = neg.split('\n')

def countPosNeg(df):
    words = []
    for i in df.index:
        posCount = 0
        negCount = 0
        posLevel = 0
        negLevel = 0
        words = tokenizer.tokenize(str(df.speech[i]).lower()) # split speaker's speech into words
        if len(words) > 0:
            for word in words:
                if word in posWords:
                    posCount += 1
                elif word in negWords:
                    negCount += 1
            df.loc[i, 'posCount'] = posCount
            df.loc[i, 'posLevel'] = posCount / len(words)
            df.loc[i, 'negCount'] = negCount
            df.loc[i, 'negLevel'] = negCount / len(words)
        else:
            df.loc[i, 'posLevel'] = 0
            df.loc[i, 'negLevel'] = 0
        # print i, posCount, negCount, len(words), df.loc[i, 'posLevel'], df.loc[i, 'negLevel']

if __name__ == '__main__':
    df = pd.read_csv('./data/hearings_with_specifs.csv', index_col=0, header=0, dtype={'committee': str, 'speech': str})
    tokenizer = nltk.RegexpTokenizer(r'\w+') #tokenizer that gets only the alphanumeric items, no punctuation
    countPosNeg(df)
    df.to_csv('./data/hearings_spec_sent.csv', header=True)
