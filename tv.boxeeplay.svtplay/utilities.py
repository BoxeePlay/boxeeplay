import urllib2

def getData(url):
    request = urllib2.Request(url)
    request.add_header = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
    response = urllib2.urlopen(request)
    data = response.read()
    response.close();
    return data

def decodeHtmlEntities(string):
    return string.replace("&amp;", "&")