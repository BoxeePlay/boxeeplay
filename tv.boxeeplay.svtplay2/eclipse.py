import utilities,re
#===============================================================================
#
#===============================================================================
def printcat():
    items = svtplay.getCategories()
    print len(items)

def printprograms():
    items = svtplay.getPrograms('/c/96251/barn') #barda
    print len(items)

def getItemsFromMRSS(url):
    result = ""
    data = utilities.getData(url)
    total_result = re.compile("<opensearch:totalResults>(.*?)</opensearch:totalResults>", re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
    for i in range(int(total_result)):
        if (i==0):
            result = re.compile('<item [^>]*>[\W\w]+?</item>').findall(data, re.DOTALL)
        else:
            y=i+1
            data = utilities.getData(url+'&start='+str(y))
            result = result + re.compile('<item [^>]*>[\W\w]+?</item>').findall(data, re.DOTALL)

    for node in result:
        title = re.compile("<title>(.*?)</title>").findall(str(node), re.DOTALL)[0]
        print title

        image = re.compile('<media:thumbnail url="(.*?)"').findall(str(node), re.DOTALL)[0]
        print image


def rss():
    items = getItemsFromMRSS('http://xml.svtplay.se/v1/video/list/151490?expression=full')
    #print items
    
rss()

