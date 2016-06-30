library(stringr)

names = NA
allhear = data.frame()
isup <- function(x){
  x==toupper(x)
}
speechtotals = data.frame()


for (i in 1:length(hearings)){
  dat = readLines(paste("E:/Hearings/GPO/",hearings[i],'.htm',sep=''))##CHANGE FILE LOCATION##
  print(i)
  dat = as.data.frame(dat)
  dat$dat = as.character(dat$dat)
  dat$speak = NA
  dat = dat[grepl('\\[GRAPHIC\\] \\[TIFF OMITTED\\]', dat$dat)==F,] ##Remove graphic markers
  ##dat = dat[grepl('\\[(.*?)\\]',dat$dat)==F,] ##remove all bracketed lines
  dat = dat[grepl('\\((.*?)\\)',dat$dat)==F,] ##Remove all lines contained in parentheses
  dat = dat[isup(dat$dat)==F,]##Remove lines with all caps
  dat$hearingid = hearings[i]
  
  ##IDENTIFY SPEAKERS USING AS MANY TITLES AS POSSIBLE##
  dat$speak = ifelse(grepl("^(    |     )(Mr|Mrs|Ms|Dr)\\. ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\.", dat$dat),
                     str_trim(str_extract(dat$dat, "^(    |     )(Mr|Mrs|Ms|Dr)\\. ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\."), side='both'),
                     dat$speak)
  
  
  dat$speak = ifelse(grepl("^(    |     )(Chairman|Chairwoman) ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\.", dat$dat),
                     str_trim(str_extract(dat$dat, "^(    |     )(Chairman|Chairwoman) ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\."), side='both'),
                     dat$speak)
  
  dat$speak = ifelse(grepl("^(    |     )The (Chairman|Chairwoman)\\.",dat$dat),
                     'chair',
                     dat$speak)
  
  dat$speak = ifelse(grepl("^(    |     )(Mr|Mrs|Ms)\\. ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*) of [A-Za-z]*\\.", dat$dat),
                     str_trim(str_extract(dat$dat, "^(    |     )(Mr|Mrs|Ms)\\. ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*) of [A-Za-z]*\\."), side='both'),
                     dat$speak)
  
  dat$speak = ifelse(grepl("^(    |     )(General|Admiral|Lieutenant|Captain|Chief|Major|Commander|VADM) ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\.", dat$dat),
                     str_trim(str_extract(dat$dat, "^(    |     )(General|Admiral|Lieutenant|Captain|Chief|Major|Commander|VADM) ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\."), side='both'),
                     dat$speak)
  
  dat$speak = ifelse(grepl("^(    |     )(Gen|Adm|Maj|Cap)\\. ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\.", dat$dat),
                     str_trim(str_extract(dat$dat, "^(    |     )(Gen|Adm|Maj|Cap)\\. ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\."), side='both'),
                     dat$speak)
  
  dat$speak = ifelse(grepl("^(    |     )(Governor|Senator|Representative|Ambassador|Secretary) ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\.", dat$dat),
                     str_trim(str_extract(dat$dat, "^(    |     )(Governor|Senator|Representative|Ambassador) ([A-Za-z]*|[A-Za-z]*-[A-Za-z]*|[A-Za-z]* [A-Za-z]*|[A-Za-z]*[[:punct:]]*[A-Za-z]*)\\."), side='both'),
                     dat$speak)
  
  
  beginbody = which(is.na(dat$speak)==F)[1]
  if (is.na(beginbody)==F){##THERE IS SOME TEXT THAT BEGINS THE BODY##
    endbody = grep('\\[.*was adjourned.*|.*was adjourned.*\\]', dat$dat)
    if (length(endbody)>1) {
      for (k in 1:length(endbody)){
        if (is.na(endbody[k+1])==F & is.na(endbody[k])==F){
          if(abs(endbody[k]-endbody[k+1])<=3) endbody = endbody[-k]}
      }
    }
    if (length(endbody)==0) endbody = grep('adjourned;',dat$dat)##THERE WAS NO STANDARD ADJOURNED ENDING
    if (length(endbody)==0) endbody = which(is.na(dat$speak)==F)[length(which(is.na(dat$speak)==F))]##IF NO ADJOURNED ENDING REVERT TO BEGINNING OF LAST PIECE OF SPEECH##
    
    if (length(endbody)>1){##IF THERE ARE MULTIPLE ENDINGS (MULTI-DAY HEARING), FIND ALL OF THE ENDINGS AND PASTE THE VARIOUS HEARING BODIES TOGETHER##
      body = dat[beginbody:endbody[1],]
      body$speaker = na.locf(body$speak)
      data=list()
      for (k in 1:(length(endbody)-1)){
        z = endbody[k]
        a = dat[z:nrow(dat),]
        nextbegin = which(is.na(a$speak)==F)[1]
        data[[i]] = a[nextbegin:endbody[k+1],]
      }
      body = rbind(body,do.call(rbind,data))
      body$speaker = na.locf(body$speak)
    } else{
      body = dat[beginbody:endbody,]
      body$speaker = na.locf(body$speak)
    }
    
    ##REMOVE TITLES, MAKE LOWERCASE, ETC...#
    body$spclean = str_replace(string = body$speaker, 
                               pattern =  '(Mr|Mrs|Ms|Dr|Chairman|Chairwoman|General|Admiral|Lieutenant|Captain|Chief|Major|Commander|VADM|Gen|Adm|Maj|Cap|Governor|Senator|Representative|Ambassador|Secretary)',
                               replacement = '')
    body$spclean = str_replace(string = body$spclean, pattern = '[[:punct:]]', replacement = '')
    body$spclean = str_replace(string = body$spclean, pattern = '\\.', replacement = '')
    body$spclean = str_replace(string = body$spclean, pattern = ' ', replacement = '')
    body$spclean = tolower(body$spclean)
    body$spclean = str_trim(body$spclean, side = 'both')
    body = body[grepl('\\[(.*?)\\]',body$dat)==F,] ##remove all bracketed lines
  }
  if (is.na(beginbody)) {body = data.frame(dat = NA, speak = NA, hearingid = hearings[i], speaker = NA, spclean = NA)}
  if (i == 1) {allhear = body} else {allhear = rbind(allhear, body)}
}