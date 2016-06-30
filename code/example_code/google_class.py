# Python Intro Class
# Google
# March 19, 2014

import os, re, random, string, sys
words = set(open('/Applications/sage/local/include/python2.7/pyconfig.h').read().split())
words = [word for word in words if re.match("^[a-z]+$", word)]
def field():
  if random.randint(1,20) < 19:
    return words[random.randint(0, len(words) -1)]
  else:
    return '<a href="%s.com">link</a>' % random.choice(string.lowercase)
pages = dict()
print 'Generating webpages a.com through z.com'
for i in string.lowercase:
  pages['%s.com' % i] = ' '.join([field() for j in range(0, 100)])
def solicitWebPage():
  return raw_input('enter a webpage such as a.com, b.com, ..., z.com: ')
def getWebPage(url):
  return pages[url]
wordCounts = dict()
def recordWord(word, url):
  if word not in wordCounts:
    wordCounts[word] = {}
  if url not in wordCounts[word]:
    wordCounts[word][url] = 0
  wordCounts[word][url] += 1

# CHALLENGE #0 - Hello, World!
# Instructions:
# * Delete 'raise BaseException...' statement
# * Replace ___1___ with print
# * Replace ___2___ with 'Hello world!'

print('Hello World!')

 #1 - Fetch the content of a web page
# Instructions:
# * Delete 'raise BaseException...' statement
# * Replace ___1___ with url
# * Replace ___2___ with solicitWebPage
# * Replace ___3___ with result
# * Replace ___4___ with getWebPage
# * Replace ___5___ with url
# * Replace ___6___ with print
# * Replace ___7___ with result
#
# Advanced:
# * Print just the first 20 characters of the webpage
# * Print just the last 20 characters of the webpage
# * Print the webpage but replace all the whitespace with underscores

url = solicitWebPage()
result = getWebPage(url)
print(result)

 #2 - Identify how often each word occurs in the page.
# Instructions:
# * Delete 'raise BaseException...' statement
# * Replace ___1___ with recordPage
# * Replace ___2___ with word
# * Replace ___3___ with someWebpage
# * Replace ___4___ with recordWord
# * Replace ___5___ with recordPage
# * Replace ___6___ with print
# * Replace ___7___ with wordCounts
#
# Advanced:
# * Print just the list of identified words, not their counts
# * Exclude links from being recorded

def recordPage (someUrl, someWebpage):
  for word in someWebpage.split():
    recordWord(word, someUrl)
recordPage(url, result)
print(wordCounts)

# CHALLENGE #3: Crawl the web for links.
# Instructions:
# * Delete 'raise BaseException...' statement
# * Replace ___1___ with urlsVisited
# * Replace ___2___ with crawlForLinks
# * Replace ___3___ with someUrl
# * Replace ___4___ with urlsVisited
# * Replace ___5___ with urlsVisited
# * Replace ___6___ with someUrl
# * Replace ___7___ with someWebPage
# * Replace ___8___ with getWebPage
# * Replace ___9___ with links
# * Replace ___10___ with someWebPage
# * Replace ___11___ with link
# * Replace ___12___ with crawlForLinks
# * Replace ___13___ with allLinks
# * Replace ___14___ with crawlForLinks
# * Replace ___15___ with print
# * Replace ___16___ with allLinks
#
# Advanced:
# * g.com has been blacklisted; make sure we never crawl it for links!
# * The server can't handle this many links; once we have collected 50 links
#   we should stop crawling.

urlsVisited = set()
def crawlForLinks(someUrl):
  if someUrl in urlsVisited:
    return set()
  else:
    urlsVisited.add(someUrl)
  someWebpage = getWebPage(someUrl)
  links = re.compile("href\s*=\s*\"\s*([^\"]+)\"").findall(someWebpage)
  for link in links:
    links += crawlForLinks(link)
  return set(links)
allLinks = crawlForLinks(url)
print(allLinks)

# CHALLENGE #4: Crawl each link for word counts.
# Instructions:
# * Delete 'raise BaseException...' statement
# * Replace ___1___ with link
# * Replace ___2___ with allLinks
# * Replace ___3___ with someWebPage
# * Replace ___4___ with getWebPage
# * Replace ___5___ with recordPage
# * Replace ___6___ with link
# * Replace ___7___ with someWebPage
# * Replace ___8___ with print
# * Replace ___9___ with wordCounts
#
# Advanced:
# * The censors aren't happy with words longer than 6 characters. Make sure that
#   the contents of someWebPage exclude any words that are too long.

for link in allLinks:
  someWebpage = getWebPage(link)
  recordPage(link, someWebpage)
print(wordCounts)

# CHALLENGE 5: Let the user search for a word
# Instructions:
# * Delete 'raise BaseException...' statement
# * Replace ___1___ with print
# * Replace ___2___ with sorted
# * Replace ___3___ with wordCounts
# * Replace ___4___ with search
# * Replace ___5___ with info
# * Replace ___6___ with highestCount
# * Replace ___7___ with bestUrl
# * Replace ___8___ with highestCount
# * Replace ___9___ with print
# * Replace ___10___ with search
# * Replace ___11___ with highestCount
# * Replace ___12___ with bestUrl
#
# Advanced:
# * Report which site has the fewest occurrences of the search term.

print '\n\n\nAvailable search terms:', sorted(wordCounts.keys())
search = raw_input('Please select a search term from the list above:')
info = dict((val, key) for key, val in wordCounts[search].iteritems())
highestCount = sorted(info.keys()) [-1]
lowestCount = sorted(info.keys()) [0]
bestUrl = info[highestCount]
print('%s occurs the most times (%d) on %s' % (search, highestCount, bestUrl))
print('%s occures the least times (%d) on %s' % (search, lowestCount, bestUrl))
