import csv
import sys
from collections import defaultdict
from fuzzywuzzy import fuzz


THRESHOLD_MAX_RATIO = 50


csv.field_size_limit(sys.maxsize)
char_map = {'#': 'num'}
default_fieldname = 'id'

def convert_fieldname(chamber, fieldname):
    name_bits = [chamber]
    for bit in fieldname.split(' '):
        bit = ''.join(
            char if char.isalnum() else char_map.get(char, '_')
            for char in bit.lower()) or default_fieldname
        name_bits.append(bit)
    new_name = '_'.join(name_bits)
    while '__' in new_name:
        new_name = new_name.replace('__', '_')
    return new_name


def get_mapping(chamber, reader):
    mapping = {}
    for field in reader.fieldnames:
        mapping[field] = convert_fieldname(chamber, field)
    return mapping
        
def get_name(row, field):
    return row[field].lower().replace(
        ',', ' ').replace('committee on', '').replace(
            '(select committee)', '').replace('  ', ' ')


def find_chair(data, chairman):
    chairman = chairman.split(',', 1)[0].lower()
    if len(data) == 1:
        return data.values()[0]
    else:
        chairs = {}
        for chair in data.iterkeys():
            chairs[chair] = fuzz.partial_token_sort_ratio(chair, chairman)
        max_chair = tuple(max(item[::-1] for item in chairs.iteritems()))[1]
        return data[max_chair]


def get_chair(chair):
    return ' '.join(chair.split(',')[::-1]).lower().strip()                


def join(testimony_file, house_file, senate_file, result_file):
    t_reader = csv.DictReader(testimony_file)
    h_reader = csv.DictReader(house_file)
    s_reader = csv.DictReader(senate_file)

    # Get result headers
    mappings = {
        'house': get_mapping('house', h_reader),
        'senate': get_mapping('senate', s_reader)}
    result_headers = t_reader.fieldnames[:]
    result_headers.extend(mappings['house'].itervalues())
    result_headers.extend(mappings['senate'].itervalues())
    r_writer = csv.DictWriter(result_file, fieldnames=result_headers)
    r_writer.writeheader()

    # Structure data for easier access
    row_mapping = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(dict)))
    for chamber, reader in (('house', h_reader), ('senate', s_reader)):
        for row in reader:
            name = get_chair(row['Name'])
            row_mapping[chamber][row['Congress']][
                get_name(row, 'Committee Name')][name] = row

    # Match the committee
    for row in t_reader:
        chamber = row['chamber'].lower()
        if chamber:
            committee_name = get_name(row, 'committee')
            committees_data = row_mapping[chamber][row['congress']]
            if committee_name and committees_data:
                # First try to match a substring in committee name
                for committee, data in committees_data.iteritems():
                    if committee in committee_name:
                        chair_data = find_chair(data, row['committee_chairman'])
                        if chair_data:
                            for key, value in chair_data.iteritems():
                                row[mappings[chamber][key]] = value
                            break
                else:
                    # Otherwise, try fuzzy match
                    ratios = {}
                    for committee, data in committees_data.iteritems():
                        ratio = fuzz.partial_token_sort_ratio(committee_name, committee)
                        ratios[ratio] = data
                    max_ratio = max(ratios.iterkeys())
                    if max_ratio > THRESHOLD_MAX_RATIO:
                        data = ratios[max_ratio]
                        chair_data = find_chair(data, row['committee_chairman'])
                        for key, value  in chair_data.iteritems():
                            row[mappings[chamber][key]] = value

        r_writer.writerow(row)

if __name__ == '__main__':
    if '--help' in sys.argv or sys.argv > 1 and len(sys.argv) != 5:
        print 'Run this script like "python {} [testimony.csv house_chairs.csv senate_chairs.csv results.csv] minus the brackets."'.format(sys.argv[0])
    else:
        if len(sys.argv) > 0:
            t_name, h_name, s_name, r_name = sys.argv[1:]
        else:
            t_name, h_name, s_name, r_name = (
                'testimony.csv', 'house_chairs.csv', 'senate_chairs.csv',
                'hearing_metadata_3_2.csv')
        t_file = file(t_name)
        h_file = file(h_name)
        s_file = file(s_name)
        r_file = file(r_name, 'w')
        join(t_file, h_file, s_file, r_file)