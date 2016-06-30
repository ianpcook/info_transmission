# Text procesing file. Ingest and initial processing
# Project: Congressional Testimony Essay
# Ian P. Cook

import os, re, csv, string, operator
import nltk
from nltk.corpus import PlaintextCorpusReader
import time

start_time = time.time()
dir = '/Users/ian/Dropbox/Academia/Dissertation/testimony/hearings/112Congress/'

corpus_root = dir
hearings = PlaintextCorpusReader(corpus_root, '.*')

cfd = nltk.ConditionalFreqDist(
    (target, fileid[-4:-9])
    for fileid in hearings.fileids()
    if os.path.getsize(fileid) > 0
    for w in hearings.words(fileid)
    for target in ['apologize', 'regret']
    if w.lower().startswith(target))
print (time.time() - start_time)
cfd.plot()

# The above code works, with one exception: longer/multi-wor:d
# "targets" causes an error: "local variable 'legend-loc' referenced before
# assignment'. Not sure what that is about.

# Working on getting the filenames into a csv
# pass the function a directory and it should travers all the files
# and subfolders, read the filenames, and put them into the CSV's first column



        
