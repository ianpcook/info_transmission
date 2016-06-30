import pandas as pd
from multiprocessing import Pool
from itertools import izip_longest

def get_affiliation(worklist):
    for i in range(len(worklist[2])):
        if worklist[2][i] in [worklist][0][i][0]:
            worklist[3][i] = worklist[0][i][1]
    return worklist


def create_lists(full, ags, cleanwitlist):
    affiliations = []
    for i in range(len(cleanwitlist)):
        for j in range(len(ags)):
            if ags[j] in cleanwitlist[i]:
                affiliations.append((cleanwitlist[i], ags[j]))
    filenames = list(full['filename'])
    lastnames = [x.split()[1].lower() for x in full['speaker']]
    return [affiliations, filenames, lastnames]

if __name__ == '__main__':
    ags = [line.rstrip('\n').lower() for line in open('./data/supplemental_data/us_agency_list.txt')]
    cleanwitlist = [line.rstrip('\n').lower() for line in open('./data/supplemental_data/witness_list.txt')]
    full = pd.read_csv('./data/hearing_metadata_3.csv', header=0)
    del full['speech']
    full = full[0:100]
    [affiliations, filenames, lastnames] = create_lists(full, ags, cleanwitlist)
    agency = []
    worklist = [affiliations, filenames, lastnames, agency]
    pool = Pool()
    pool.map(get_affiliation, worklist)
    pool.close()
    work = pool.join()
    f = open('./test.txt', 'w')
    for item in work:
        f.write(item+'\n')
