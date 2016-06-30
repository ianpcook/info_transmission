import csv
import re


speaker_re = re.compile(
    r"(?P<title>"
    r"(senator|representative|secretary|chairman|chairwoman|dr\.|mr\.|mrs\.|ms\.|rev\."
    r"|col\.|maj\.|maj\. ?gen|gen\.|sgt\.|lt\. ?col))\s+(?P<speaker>.+)")


def clean(name):
    name = name.strip().lower()
    while '  ' in name:
        name = name.replace('  ', ' ')
    return name


def match(name, speaker):
    if isinstance(speaker, basestring):
        if isinstance(name, basestring):
            return name == speaker
        else:
            name = name.groupdict()['speaker']
            return name in speaker
    else:
        if isinstance(name, basestring):
            speaker = speaker.groupdict()['speaker']
            return speaker in name
        else:
            speaker = speaker.groupdict()['speaker']
            name = name.groupdict()['speaker']
            return name in speaker or speaker in name


def process_files(in_file, out_file):
    reader = csv.DictReader(in_file)
    writer = csv.DictWriter(
        out_file, reader.fieldnames + ['speaker_credential', 'speaker_inst'])

    num_answers = max(
        int(fieldname.split('Answer.credential_')[1])
        for fieldname in reader.fieldnames if fieldname.startswith('Answer.credential_'))

    writer.writeheader()
    for row in reader:
        writer.writerow(match_speaker(row, num_answers, writer))
    out_file.close()


def match_speaker(row, num_answers, writer):
    clean_speaker = clean(row['speaker'])
    speaker = speaker_re.match(clean_speaker) or clean_speaker
    if not speaker:
        return row
    
    result = row.copy()
    for i in xrange(1, num_answers + 1):
        try:
            clean_name = clean(row['Answer.name_{}'.format(i)])
            name = speaker_re.match(clean_name) or clean_name
        except KeyError:
            continue
        if match(name, speaker):
            try:
                inst = row['Answer.inst_{}'.format(i)]
            except KeyError:
                inst = ''
            result['speaker_inst'] = inst
            try:
                credential = row['Answer.credential_{}'.format(i)]
            except KeyError:
                credential = ''
            result['speaker_credential'] = credential
            print 'Found: {} = {} ({}, {})'.format(
                clean_speaker, clean_name, credential, inst)
            break
    return result

if __name__ == '__main__':
    import sys
    in_file_name, out_file_name = sys.argv[1:] if len(sys.argv) == 3 else (
        './data/testimony_mt_df.csv', './data/testimony_mt_df.new.csv')
    in_file = file(in_file_name)
    out_file = file(out_file_name, 'w')
    process_files(in_file, out_file)
