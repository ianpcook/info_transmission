import csv
import collections
from sklearn.decomposition import NMF
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer


hearing_groups = collections.OrderedDict([
    ('all', None),
    ('senate_and_environment',
     {'chamber': 'senate', 'committee': 'environment'}),
    ('house_105', {'chamber': 'house', 'congress': '105'}),
    ('indian', {'committee': 'indian'}),
    ('veterans_and_foreign', {'committee': 'veterans,foreign'})
])

stop_words = list(ENGLISH_STOP_WORDS)
for i in xrange(2050):
    stop_words.append(str(i))
# Add some extra stop words that are too vague:
stop_words.extend(
    'act hearing hearings management va united affairs'.split(' '))

def load_results(src="results.csv"):
    """
    Read CSV file's contents into a list.
    """
    reader = csv.DictReader(open(src))
    return list(reader)


def get_groups_for_row(row, conf=hearing_groups):
    """
    Get all groups whose filters are matched by this row.
    """
    result = []
    for key, params in conf.items():
        if not params:
            result.append(key)
            continue
        else:
            # Check params to avoid typos
            for param in params.keys():
                if param not in ('chamber', 'congress', 'committee'):
                    raise Exception('Invalid param "{}" in config'.format(
                        param))

            # Check if all params are matched
            if'chamber' in params:
                if params['chamber'].lower() != row['chamber'].lower():
                    continue
            if 'congress' in params:
                if params['congress'] != row['hearing_number'][:3]:
                    continue
            if 'committee' in params:
                keywords = params['committee'].split(',')
                for keyword in keywords:
                    if keyword.lower() in row['committee'].lower():
                        break
                else:
                    continue
            result.append(key)
    return result


def groups_to_dict(groups, hearings, conf=hearing_groups):
    """
    Make a dict with data like {group_name: [filename1, filename2, ...]}
    """
    results = collections.OrderedDict()
    for group in conf.iterkeys():
        results[group] = []
    for filename, groups_list in groups.iteritems():
        for group in groups_list:
            results[group].append(hearings[filename])
    return results


def process_hearings(hearings, n_topics=10, n_top_words=10, n_features=1000):
    for h in hearings:
        print h
    vectorizer = TfidfVectorizer(
        max_df=0.95, min_df=3, max_features=None, use_idf=1,
        stop_words=stop_words)
    tfidf = vectorizer.fit_transform(hearings)
    nmf = NMF(n_components=n_topics, random_state=1).fit(tfidf)
    feature_names = vectorizer.get_feature_names()

    for topic_idx, topic in enumerate(nmf.components_):
        print "Topic #%d:" % (topic_idx + 1)
        print " ".join([
            feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
        
if __name__ == '__main__':
    input_data = load_results()
    hearings = dict(
        (row['filename'], row['hearing_title']) for row in input_data)
    groups = groups_to_dict(
        dict(
            (row['filename'], get_groups_for_row(row))
            for row in input_data if row['hearing_title']),
        hearings)
    for group, hearings in groups.iteritems():
        print '!', group
        process_hearings(hearings)
