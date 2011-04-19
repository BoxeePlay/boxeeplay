import urllib2,mc

def getData(url):
    request = urllib2.Request(url)
    request.add_header = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
    response = urllib2.urlopen(request)
    data = response.read()
    response.close();
    return data

def decodeHtmlEntities(string):
    return string.replace("&amp;", "&")

def isNotBeta():
    #Denna SKA skrivas om! Beroende av skinnet nu, inte bra! Men GetPlatform fungerar ej!
    ver = mc.GetActiveWindow().GetLabel(14002).GetLabel()
    if (ver.find('0.')==0):
        return False
    else:
        return True

