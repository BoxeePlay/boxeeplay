import urllib2
from logger import BPLog, BPTraceEnter, BPTraceExit

def getData(url):
    BPTraceEnter(url)
    request = urllib2.Request(url)
    request.add_header = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
    response = urllib2.urlopen(request)
    data = response.read()
    response.close();
    BPTraceExit("Returning %s" % data)
    return data

def decodeHtmlEntities(string):
    BPTraceEnter(string)
    r = string.replace("&amp;", "&")
    BPTraceExit("Returning %s" % r)
    return r
