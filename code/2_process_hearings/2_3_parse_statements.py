import collections
import csv
import os


def read_data(src='./data/hearing_metadata_2.csv'):
    reader = csv.DictReader(file(src, 'rU'))
    for row in reader:
        yield [row[key] for key in ('filename', 'committee')]


class StatementParser(object):
    def __init__(self, debug=False):
        self.statements = collections.OrderedDict()
        self.debug = debug
        self.reset_context()

    def parse_line(self, line):
        line = line.strip()
        if (
                line.startswith('STATEMENT OF') or
                line.startswith('OPENING STATEMENT OF')):
            # New header
            if self.reading_statement:
                self.store_statement()
            self.cur_header.append(line)
            self.reading_header = True
        elif self.reading_header:
            if line:
                if line.isupper():
                    self.cur_header.append(line)
                else:
                    self.cur_statement = [line]
                    self.reading_statement = True
                    self.reading_header = False
            else:
                self.reading_statement = True
                self.reading_header = False
        elif self.reading_statement:
            self.cur_statement.append(line)

    def store_statement(self):
        if self.cur_header and self.cur_statement:
            header = ' '.join(self.cur_header)
            if self.debug:
                print header
            self.statements[header] = '\n'.join(self.cur_statement)
        self.reset_context()

    def reset_context(self):
        self.found_statement = False
        self.reading_header = False
        self.reading_statement = False
        self.cur_header = []
        self.cur_statement = []


def parse_file(prefix, filename, debug=False):
    path = os.path.join(prefix, filename)
    parser = StatementParser(debug)
    for line in file(path):
        parser.parse_line(line)
    else:
        parser.store_statement()
    return parser.statements


def store_data(writer, data, filename, committee):
    for header, statement in data.iteritems():
        writer.writerow({
            'filename': filename, 'committee': committee,
            'speaker': header.split('STATEMENT OF', 1)[1],
            'statement': statement})


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

    badStatementFiles = []
    if not debug:
        writer = csv.DictWriter(
            file('./data/statements.csv', 'w'),
            ['filename', 'committee', 'speaker', 'statement'])
    for filename, committee in read_data():
        if allowed_names and filename not in allowed_names:
            continue
        if debug:
            print 'Processing', filename
        try:
            data = parse_file(base_dir, filename, debug)
        except IOError:
            print filename, 'can\'t be read'
            badStatementFiles.append(filename)
        if not debug:
            store_data(writer, data, filename, committee)
        if debug:
            print 'Done!'
    outfile = open('../../data/badStatementFiles.csv', 'w+')
    wr = csv.writer(outfile, delimiter=',')
    wr.writerow(badStatementFiles+'\n')
    outfile.close()

