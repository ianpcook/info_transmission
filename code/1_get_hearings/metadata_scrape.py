__author__ = 'ian'

import pandas as pd
import os


def xml2df(url):
     # make some terrible R code
     from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage
     from rpy2.robjects import pandas2ri

     string = """
     require(XML)
     require(plyr)

     getXML <- function(x) {
          xmlfile <- xmlTreeParse(x)
          temp = xmlToList(xmlfile, addAttributes = F)
          df <- ldply(temp, .fun=function(x) {data.frame(t(unlist(x)))})
          return(df)
     }
     """
     test = SignatureTranslatedAnonymousPackage(string, "test")

     # make a pandas DF out of the stupid R df
     pydf = pandas2ri.ri2py_dataframe(test.getXML(url))
     return pydf

def trimDF(df):
    for i in range(len(df)):
        if str(df.loc[i,'congCommittee1']) == 'nan':
            df.loc[i, 'congCommittee1'] = df.loc[i, 'congCommittee']
    df.rename(columns={'congCommittee1' : 'comLongName', 'congCommittee2' : 'comShortName', 'congCommittee3' : 'subComName'}, inplace=True)
    df = df.filter(regex='witness|congMem|comLongName|comShortName|subComName|recordIdentifier')
    df.rename(columns={'recordIdentifier' : 'filename'}, inplace=True)
    return df

if __name__ == '__main__':
    hearings = [h.replace('.txt', '') for h in os.listdir('./data/clean_hearings_flat/')]
    metadf = pd.DataFrame()
    for i in hearings:
         try:
             url = 'http://www.gpo.gov/fdsys/pkg/'+i+'/mods.xml'
             tempdf = xml2df(url)
             metadf = metadf.append(tempdf.ix[:0:])
             print 'Done with ' + i
         except:
             print 'Trouble with '+i
             continue
    meta = metadf
    meta = trimDF(meta)
    meta.to_csv('./data/hearing_metadata_1.csv', header='True', index=0, encoding='utf-8')
