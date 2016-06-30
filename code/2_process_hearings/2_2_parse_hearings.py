import csv
import datetime
import re


class StepFinished(Exception):
    """
    This exception is raised when step is finished.
    """


class BaseStep(object):
    optional = False
    attrs = []

    def __init__(self, data, has_contents):
        self.data = data
        self.has_contents = has_contents
        self.found_contents = False

    def process_line(self, line):
        """
        Every subclass should implement this method.

        @param line: current line value
        """
        raise NotImplementedError

    def check_date(self, line, finish=True):
        found = False
        line = line.rstrip('.')
        try:
            self.data['date'] = datetime.datetime.strptime(
                line.lower().strip().title(), '%A, %B %d, %Y'
            ).strftime('%d/%m/%y')
            found = True
        except ValueError:
            pass

        if not found:
            try:
                self.data['date'] = datetime.datetime.strptime(
                    line.lower().strip().title(), '%B %d, %Y'
                ).strftime('%d/%m/%y')
                found = True
            except ValueError:
                pass

        if finish and found:
            raise StepFinished


class ChamberAndHearingNumber(BaseStep):
    line_re = re.compile(
        '\[(?P<chamber>.+) Hearing,? (?P<hearing_number>.+)\]')
    attrs = [('chamber', str), ('hearing_number', str)]

    def process_line(self, line):
        match = self.line_re.match(line)
        if match:
            self.data.update(match.groupdict())
            raise StepFinished()


class HearingTitle(BaseStep):
    title = ''
    attrs = [('hearing_title', str)]

    def process_line(self, line):
        line = line.strip().replace('=', '')
        if self.data['hearing_number'] in line:
            return

        # We're receving title now
        if self.title:
            if line:
                # Multi-line title
                if self.title:
                    self.title += ' ' + line
            else:
                # Title done
                self.data['hearing_title'] = self.title.rstrip('-=_')
                raise StepFinished()
        elif line and not line.startswith('['):
            # Start title
            self.title = line


class SubcommitteeCommitteeTitle(BaseStep):
    optional = True
    attrs = [
        ('date', str), ('title', str), ('committee', str),
        ('subcommittee', str)]

    found_subcommittee = False
    found_committee = False
    found_title = False
    finished_title = False
    finished_committee = False
    finished_subcommittee = False

    value = ''
    is_parsing = False
    num_blanks = 0

    def __init__(self, data, has_contents):
        super(SubcommitteeCommitteeTitle, self).__init__(data, has_contents)
        data['date'] = ''
        for key in ('title', 'committee', 'subcommittee'):
            self.data[key] = ''

    def process_line(self, line):
        line = line.strip()
        lline = line.lower()
        if 'statement' in lline:
            self._fix_committee()
            raise StepFinished

        self.check_date(line, finish=False)

        if not line:
            self.num_blanks += 1
            if self.found_title:
                self.finished_title = True
            if self.found_committee:
                self.finished_committee = True
            if self.found_subcommittee:
                self.finished_subcommittee = True
        else:
            self.num_blanks = 0
        if self.num_blanks == 3:
            self._fix_committee()
            raise StepFinished

        if line.startswith('='):
            return

        if '_' in line:
            self._fix_committee()
            raise StepFinished

        if self.found_title:
            if '_' in line:
                raise StepFinished
            elif not self.finished_title:
                self.data['title'] += ' ' + line
        elif lline == 'first session':
            self.found_title = True
            self.data['title'] = ''

        elif lline.startswith('committee on') and not self.finished_committee:
            self.found_committee = True
            self.data['committee'] = line

        elif lline.startswith(
                'subcommittee on') and not self.finished_subcommittee:
            self.found_subcommittee = True
            self.data['subcommittee'] = line

        elif self.found_subcommittee:
            if line:
                self.data['subcommittee'] += ' ' + line
            else:
                self.found_subcommittee = False

        elif self.found_committee:
            if line:
                self.data['committee'] += ' ' + line
            else:
                self._fix_committee()
                self.found_committee = False

    def _fix_committee(self):
        if self.data.get('committee'):
            for split_by in (
                    'HOUSE OF REPRESENTATIVES', 'UNITED STATES SENATE'):
                if split_by in self.data['committee']:
                    self.data['committee'] = self.data['committee'].split(split_by)[0].rstrip()
                    break


class ChairmenAndAttendees(BaseStep):
    attrs = [
        ('committee_chairman', str),
        ('committee_attendees', list), ('subcommittee_chairman', str),
        ('subcommittee_attendees', list)]
    state = None
    separators = ['(ii)', 'page ii', 'c o n t e n t s', 'contents']
    optional = True
    found_contents = False
    weekdays = [
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
        'sunday']
    chairman_re = re.compile('.*, .*, chairman', re.I)

    def __init__(self, data, has_contents):
        super(ChairmenAndAttendees, self).__init__(data, has_contents)

        data['committee_chairman'] = ''
        data['subcommittee_chairman'] = ''
        data['committee_attendees'] = []
        data['subcommittee_attendees'] = []

    def process_line(self, line):
        line = line.strip()

        if '--' in line:
            return

        if line.lower() in ('c o n t e n t s', 'contents'):
            self.found_contents = True

        self.check_date(line)

        lline = line.lower()
        if lline.startswith('subcommittee on'):
            self.data['subcommittee'] = lline.upper()

        if 'statement' in lline:
            raise StepFinished

        if any(sep in lline for sep in self.separators):
            raise StepFinished

        if self.state is None or self.state == 'committee-attendees':
            if "subcommittee" in line.lower():
                self.state = 'subcommittee-header'
                return
        if self.state == 'subcommittee-header' and not line:
            self.state = 'subcommittee-chairman'
            return

        if (
                self.state == 'subcommittee-chairman' and
                self.chairman_re.match(line.strip())):
            self.data['subcommittee_chairman'] = line
            self.state = 'subcommittee-attendees'
            return

        if self.state == 'subcommittee-attendees':
            if line:
                attendees = [a.strip() for a in line.split('  ') if a.strip()]
                self.data['subcommittee_attendees'].extend(attendees)
                return
            elif self.data['subcommittee_attendees']:
                self.state = None
                return

        if self.state is None or self.state == 'subcommittee-attendees':
            if 'committee' in line.lower():
                self.state = 'committee-header'
                return

        if self.state == 'committee-header' and not line:
            self.state = 'committee-chairman'
            return

        if (
                self.state == 'committee-chairman' and
                self.chairman_re.match(line.strip())):
            self.data['committee_chairman'] = line
            self.state = 'committee-attendees'
            return

        if self.state == 'committee-attendees':
            if line:
                attendees = [a.strip() for a in line.split('  ') if a.strip()]
                self.data['committee_attendees'].extend(attendees)
                return
            elif self.data['committee_attendees']:
                self.state = None
                return


class Witnesses(BaseStep):
    attrs = [
        ('witnesses', list), ('committee-chairman', str),
        ('subcommittee-chairman', str)]
    current_value = ''
    optional = True
    num_blanks = 0
    chairman_re = re.compile('.*, .*, chairman', re.I)

    def __init__(self, data, has_contents):
        super(Witnesses, self).__init__(data, has_contents)

        self.data['witnesses'] = []
        self.is_committee = False
        self.is_subcommittee = False

    def process_line(self, line):
        if not self.has_contents:
            raise StepFinished

        if self.data['witnesses']:
            if not self.has_contents or '----' in line or '(iii)' in line:
                raise StepFinished
            self.check_date(line)

        lline = line.lower()
        if lline.strip().startswith('committee'):
            self.is_committee = True
            self.is_subcommittee = False
        elif lline.strip().startswith('subcommittee'):
            self.is_committee = False
            self.is_subcommittee = True

        if lline.strip().endswith('chairman'):
            is_chairman = self.chairman_re.match(line.strip())
            if self.is_committee:
                self.data['committee-chairman'] = line.strip()
                self.is_committee = False
            elif self.is_subcommittee:
                self.data['subcommittee-chairman'] = line.strip()
                self.is_subcommittee = False
            
        if not self.found_contents:
            if 'c o n t e n t s' in lline or 'contents' in lline:
                self.found_contents = True
            return

        if not line.strip():
            self.num_blanks += 1
        else:
            self.num_blanks = 0
        if self.num_blanks == 3:
            raise StepFinished

        if self.found_contents:
            if not line.strip():
                self.save_current()

            else:
                line = line.rstrip(' ')
                if not self.current_value and line.startswith(' '):
                    # Not a witness name - subparagraph
                    return

                if line[-1].isdigit():
                    line = line.rsplit(' ', 1)[0].rstrip().rstrip(
                        '.').lstrip(' ')
                    if self.current_value:
                        self.current_value += ' ' + line
                        self.save_current()
                    else:
                        self.current_value = line.rstrip()
                        self.save_current()
                else:
                    if self.current_value:
                        if not line.startswith(' '):
                            # Actual contents entry is recorded with no
                            # page number - save and repeat line processing
                            self.current_value = self.current_value.rstrip('.')
                            self.save_current()
                            
                            self.process_line(line)
                        else:
                            self.current_value += ' ' + line
                    else:
                        self.current_value = line

    def save_current(self):
        if not self.current_value:
            return
        self.data['witnesses'].append(self.current_value)
        self.current_value = ''


class Date(BaseStep):
    # Actual date may be stored by previous step, hence no attributes here
    def process_line(self, line):
        if self.data['date']:
            raise StepFinished

        self.check_date(line)

step_classes = [
    ChamberAndHearingNumber, HearingTitle, SubcommitteeCommitteeTitle,
    ChairmenAndAttendees, Witnesses, Date
]


def process_steps(file_name, text, debug):
    steps = step_classes[:]
    step = None
    data = {}
    has_contents = 'C O N T E N T S' in text or 'CONTENTS' in text
    found_contents = False

    for line in text.splitlines():
        if not step and not steps:
            break

        if not step:
            step = steps[0](data, has_contents=has_contents)
            step.found_contents = found_contents
            steps = steps[1:]

        try:
            if debug:
                print step.__class__.__name__, line.rstrip()
            step.process_line(line)
            found_contents = step.found_contents
        except StepFinished:
            data = step.data
            found_contents = step.found_contents
            step = None
    else:
        if steps and step:
            if debug and not step.optional:
                print '{} step not found in {}'.format(
                    step.__class__.__name__, file_name)

    return data


def get_csv(data, dst):
    # Get fieldnames
    fieldnames = ['filename']
    attr_lists = [('filename', None)]
    for step in step_classes:
        for attr, attr_type in step.attrs:
            if attr_type is list:
                # Lists are expanded to create a column for each value
                max_attrs = 0
                for result in data:
                    max_attrs = max(max_attrs, len(result.get(attr, ())))
                attr_lists.append((attr, max_attrs))
                for i in xrange(max_attrs):
                    fieldnames.append('{}_{}'.format(attr, i + 1))
            else:
                fieldnames.append(attr)
                attr_lists.append((attr, None))

    writer = csv.DictWriter(dst, fieldnames)
    writer.writeheader()
    for result in data:
        row = {}
        for attr, max_attrs in attr_lists:
            if max_attrs is not None:
                for i, val in enumerate(result.get(attr, ())):
                    row['{}_{}'.format(attr, i + 1)] = val
            else:
                row[attr] = result.get(attr, '')
        writer.writerow(row)


if __name__ == '__main__':
    import os
    import sys
    base_dir = os.path.join(
        os.path.dirname(__file__),
        '../../data/sample_hearings' if '--sample' in sys.argv else
        '../../data/clean_hearings_flat')
    files = os.listdir(base_dir)
    data = []
    allowed_names = [
        arg for arg in sys.argv[1:] if arg != '--debug' and arg != '--sample'
    ] if len(sys.argv) > 1 else None
    debug = '--debug' in sys.argv

    for filename in files:
        if allowed_names and filename not in allowed_names:
            continues
        if filename.endswith('.txt'):
            result = process_steps(
                filename, open(os.path.join(base_dir, filename)).read(),
                debug)
            result['filename'] = filename
            data.append(result)
            if debug:
                for k, v in sorted(result.iteritems()):
                    print k, '=>', v

    if not debug:
        get_csv(data, file('./data/hearing_metadata_2.csv', 'w'))