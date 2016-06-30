__author__ = 'ian'

import pandas as pd
import os
import fnmatch


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                fullpath = os.path.join(root, basename)
                yield fullpath


def getCongress(df):
    files = list(find_files(mydir, '*_witness_list.csv'))
    for f in files:
        turkFile = pd.read_csv(f, header=0, usecols=range(27, 75, 1))
        temp = pd.DataFrame(turkFile['Input.url'].str.split('/').tolist())  # get hearing identifier from the "Input.url" column
        turkFile['hearing'] = temp[:][5]
        turkFile['hearing'] = turkFile['hearing'].map(lambda x: x.rstrip('.txt'))  # clean out the '.txt' bit
        df = df.append(turkFile)
    return df


def joinTurkResults(df1, df2):
    df = pd.concat(df1, df2, on='hearing', how='outer')
    return df


if __name__ == '__main__':
    mydir = './data/mturk/'
    fullTurk = pd.DataFrame()
    fullTurk = getCongress(fullTurk)
    hearings = pd.read_csv('./data/testimony_df.csv', header=0)
    hearings = pd.merge(hearings, fullTurk, how='outer', on='hearing')
    hearings.to_csv('./data/testimony_mt_df.csv', header=True)