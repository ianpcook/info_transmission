## reads and extracts info from txt files of state statutes 
## downloaded from LexisNexis and Hein Online
## written for python 2.6.*
##
## Rachael Hinkle
## 11/27/2012

import os, re, csv, string, operator

mydir = "/Users/rachaelhinkle/Dropbox/Dissertation/PolicyDiffusion/"

## function to expand abbreviated month names
def expandmonth(mstring):
    mstring2 = re.sub("Jan\.", "January", mstring)
    mstring2 = re.sub("Feb\.", "February", mstring2)
    mstring2 = re.sub("Mar\.", "March", mstring2)
    mstring2 = re.sub("Apr\.", "April", mstring2)
    mstring2 = re.sub("Aug\.", "August", mstring2)
    mstring2 = re.sub("Sept\.", "September", mstring2)
    mstring2 = re.sub("Oct\.", "October", mstring2)
    mstring2 = re.sub("Nov\.", "November", mstring2)
    mstring2 = re.sub("Dec\.", "December", mstring2)
    return mstring2
    

## function to convert month names to numbers 
def month2number(mstring):
    mnumber = -999
    if (mstring == "January"):
        mnumber = "01"
    if (mstring == "February"):
        mnumber = "02"
    if (mstring == "March"):
        mnumber = "03"
    if (mstring == "April"):
        mnumber = "04"
    if (mstring == "May"):
        mnumber = "05"
    if (mstring == "June"):
        mnumber = "06"
    if (mstring == "July"):
        mnumber = "07"
    if (mstring == "August"):
        mnumber = "08"
    if (mstring == "September"):
        mnumber = "09"
    if (mstring == "October"):
        mnumber = "10"
    if (mstring == "November"):
        mnumber = "11"
    if (mstring == "December"):
        mnumber = "12"
    return mnumber



# .csv file where extracted metadata will be stored
fout = open(mydir + "statute.metadata3.csv", "w")
outfilehandle = csv.writer(fout,
                           delimiter=",",
                           quotechar='"',
                           quoting=csv.QUOTE_NONNUMERIC)

# Create your own label for each column of the metadata .csv file
localrow = []
localrow.append("lawID")
#localrow.append("filename")
localrow.append("state")
localrow.append("topic")
localrow.append("subtopic")
localrow.append("year")
localrow.append("citation")
localrow.append("Act No.")
localrow.append("repealed")
localrow.append("amended")
localrow.append("Law amended")
localrow.append("Waiting period (hours)")
localrow.append("Prev. law year")
localrow.append("Notes")
localrow.append("Statute Text")
localrow.append("Casenotes")

outfilehandle.writerow(localrow)


# Name of folder where all cases are located (and nothing else)
dirname = mydir + "AllStatutes/"
dirlist = os.listdir(dirname)
cleandirlist = []
for entry in dirlist:
    matchresult = re.match('.+\\.txt$', entry)
    if matchresult != None:
        cleandirlist.append(matchresult.group())

#dirlist = [file for file in dirlist if len(file) > 20]

# Use (uncomment) following line to test code on a small handful of cases    
#cleandirlist = cleandirlist[0:10]
            
for entry in cleandirlist: ## each entry is a txt file with an opinion
    infilepath = dirname + entry
    infilehandle = open(infilepath)
    txtlines = infilehandle.readlines()

    lawid = ""
    topic = ""
    subtopic = ""
    state = ""
    year = ""
    citation = ""
    act_no = ""
    repealed = ""
    amended = ""
    law_amended = ""
    hours = ""
    prev_yr = ""
    notes = ""
    text = ""
    cnote = ""

    text_line = False
    cnote_line = False
    

    localrow = []
    topic = str(re.split("\.", entry)[0])
    subtopic = str(re.split("\.", entry)[1])
    state = str(re.split("\.", entry)[2])
    year = str(re.split("\.", entry)[3])

    lawid = topic + "." + subtopic + "." + state + "." + year
    print lawid

    for txtline in txtlines:
        if(re.search("^CODE CITATION:", txtline)):
            citation = txtline
            citation = re.sub("CODE CITATION:\s*\n*", "", citation)

        if(re.search("^ACT NO:", txtline)):
            act_no = txtline
            act_no = re.sub("ACT NO:\s*\n*" , "", act_no)

        if(re.search("^YEAR REPEALED:", txtline)):
            repealed = txtline
            repealed = re.sub("YEAR REPEALED:\s*\n*", "", repealed)

        if(re.search("^YEAR AMENDED:", txtline)):
            amended = txtline
            amended = re.sub("YEAR AMENDED:\s*\n*", "", amended)

        if(re.search("^STATUTE AMENDED:", txtline)):
            law_amended = txtline
            law_amended = re.sub("STATUTE AMENDED:\s*\n*", "", law_amended)

        if(re.search("^WAITING PERIOD \(HOURS\):", txtline)):
            hours = txtline
            hours = re.sub("WAITING PERIOD \(HOURS\):\s*\n*", "", txtline)

        if(re.search("^PREVIOUS STATUTE YEAR \(not in data\):", txtline)):
            prev_yr = txtline
            prev_yr = re.sub("PREVIOUS STATUTE YEAR \(not in data\):\s*\n*", "", txtline)

        if(re.search("^NOTES:", txtline)):
            notes = txtline
            notes = re.sub("^<BEGIN STATUTE>\s*\n*", "", notes)
            notes = re.sub("\x93", "", notes)
            notes = re.sub("\x94", "", notes)
            notes = re.sub("\x96", "", notes)
            notes = re.sub("\xa7", "", notes)
            notes = re.sub("\x93", "", notes)
            notes = re.sub("\+>>", "", notes)
            notes = re.sub("<<\+", "", notes)
            notes = re.sub("\n", "", notes)
            notes = re.sub("NOTES:\s*\n*", "", notes)


        if (re.search("^<BEGIN STATUTE>", txtline)):
            text_line = True

        if (re.search("^<END STATUTE>", txtline)):
            text_line = False

        if text_line:
            text = text + txtline
            text = re.sub("^<BEGIN STATUTE>\s*\n*", "", text)


        if (re.search("^<BEGIN CASENOTES>", txtline)):
            cnote_line = True

        if (re.search("^<END CASENOTES>", txtline)):
            cnote_line = False

        if cnote_line:
            cnote = cnote + txtline
            cnote = re.sub("^<BEGIN CASENOTES>\s*\n*", "", cnote)

       
    #print citation

    # For each case, write a row to the .csv file which contains the desired variables.                        
    localrow = []
    localrow.append(lawid)
    #localrow.append(entry)
    localrow.append(state)
    localrow.append(topic)
    localrow.append(subtopic)
    localrow.append(year)
    localrow.append(citation)
    localrow.append(act_no)
    localrow.append(repealed)
    localrow.append(amended)
    localrow.append(law_amended)
    localrow.append(hours)
    localrow.append(prev_yr)
    localrow.append(notes)
    localrow.append(text)
    localrow.append(cnote)
    
    outfilehandle.writerow(localrow)

# Finish writing to the .csv file and close it so the process is complete 
infilehandle.close()
fout.close()





