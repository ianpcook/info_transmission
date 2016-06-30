import collections
import csv
import os
import re


def read_data(src='./data/hearing_metadata_2.csv'):
    reader = csv.DictReader(file(src, 'rU'))
    for row in reader:
        yield [row[key] for key in ('filename',)]


class SpeakerCounter(object):
    def __init__(self, debug=False):
        self.speakers = collections.defaultdict(int)
        self.debug = debug
        self.speaker_re = re.compile(
            r"(?P<speaker>"
            r"(Senator|Representative|Secretary|The ?Chairman|Chairman|Chairwoman|Dr\.|Mr\.|Mrs\.|Ms\.|Rev\.|Col\.|Maj\.|Maj\. ?Gen|Gen\.|Sgt\.|Lt\. ?Col)"
            r" \w+[\- ']?\w*)\.")
        self.sentence_finished = True
        self.speakers_order = []

    def parse_line(self, line):
        if self.sentence_finished:
            match = self.speaker_re.match(line.lstrip())
            if match:
                speaker = match.groups()[0]
                self.speakers[speaker] += 1
                self.speakers_order.append(speaker)
        self.sentence_finished = any(
            line.rstrip().endswith(char) for char in ('.', '!', '?', '--', ']', '\'\'')
        ) or not line.strip()


def parse_file(prefix, filename, debug=False):
    path = os.path.join(prefix, filename)
    parser = SpeakerCounter(debug)
    for line in file(path):
        parser.parse_line(line)
    if debug:
        result = ', '.join(
            '{}: {}'.format(*items) for items in parser.speakers.iteritems())
        print result or 'No speakers found'
    return (parser.speakers, parser.speakers_order)


def store_data(writer, data, filename):
    for speaker, counter in data.iteritems():
        writer.writerow({
            'filename': filename, 'speaker': speaker, 'remarks': counter})


def store_speakers_order(dst, max_speakers, all_speakers):
    writer = csv.DictWriter(
        dst,
        ['filename'] + [
            'speaker-{}'.format(i + 1) for i in xrange(max_speakers)])
    writer.writeheader()
    for filename, speakers in all_speakers:
        row = {'filename': filename}
        for i, speaker in enumerate(speakers):
            row['speaker-{}'.format(i + 1)] = speaker
        writer.writerow(row)


if __name__ == '__main__':
    import sys
    base_dir = os.path.join(
        os.path.dirname(__file__),
        '../../data/sample_hearings' if '--sample' in sys.argv else
        '../../data/clean_hearings_flat')
    files = os.listdir(base_dir)
    allowed_names = [
        arg for arg in sys.argv[1:] if arg not in ('--debug', '--sample')
    ] if len(sys.argv) > 1 else None
    debug = '--debug' in sys.argv

    if not debug:
        writer = csv.DictWriter(
            file('./data/speakers.csv', 'w'),
            ['filename', 'speaker', 'remarks'])
        writer.writeheader()
    all_speakers = []
    max_speakers = 0
    for (filename,) in read_data():
        if allowed_names and filename not in allowed_names:
            continue
        if debug:
            print 'Processing', filename
        try:
            speakers, speakers_order = parse_file(base_dir, filename, debug)
        except IOError:
            print filename, 'can\'t be read'

        all_speakers.append((filename, speakers_order))
        max_speakers = max(len(speakers_order), max_speakers)

        if not debug:
            store_data(writer, speakers, filename)
        if debug:
            print 'Done!'
    store_speakers_order(
        file('./data/speakers_order.csv', 'w'), max_speakers, all_speakers)