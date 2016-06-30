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
        self.debug = debug
        self.current_speaker = None
        self.speeches = collections.defaultdict(list)
        self.speaker_re = re.compile(
            r"\s+(?P<speaker>"
            r"(Senator|Representative|Secretary|Chairman|Chairwoman|Dr\.|Mr\.|Mrs\.|Ms\.|Rev\.|Col\.|Maj\.|Maj\. ?Gen|Gen\.|Sgt\.|Lt\. ?Col)"
            r" \w+[\- ']?\w*)\.(?P<speech>.+)")
        self.sentence_finished = True

    def parse_line(self, line):
        if not line.strip():
            # Empty line - speech is definitely finished
            self.current_speaker = None
            self.sentence_finished = True
        else:
            match = self.speaker_re.match(line)
            if match and self.sentence_finished:
                # Found speaker name.
                groups = match.groupdict()
                self.current_speaker = groups['speaker']
                self.speeches[groups['speaker']].append(groups['speech'].strip())
            elif self.current_speaker:
                # Multi-paragraph speech.
                self.speeches[self.current_speaker].append(line.strip())
            self.sentence_finished = any(line.rstrip().endswith(char) for char in ('.', '!', '?', '--', ']', '\'\''))


def parse_file(prefix, filename, debug=False):
    path = os.path.join(prefix, filename)
    parser = SpeakerCounter(debug)
    for line in file(path):
        parser.parse_line(line)
    if debug:
        result = '\n'.join(
            '{}: {}'.format(*items) for items in parser.speeches.iteritems())
        print result or 'No speakers found'
    return parser.speeches


def store_data(writer, data, filename):
    for speaker, speech in data.iteritems():
        writer.writerow({
            'filename': filename, 'speaker': speaker, 'speech': ' '.join(speech)})



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
            file('./data/speeches.csv', 'w'),
            ['filename', 'speaker', 'speech'])
        writer.writeheader()
    for (filename,) in read_data():
        if allowed_names and filename not in allowed_names:
            continue
        if debug:
            print 'Processing', filename
        try:
            data = parse_file(base_dir, filename, debug)
        except IOError:
            print filename, 'can\'t be read'

        if not debug:
            store_data(writer, data, filename)
        if debug:
            print 'Done!'
