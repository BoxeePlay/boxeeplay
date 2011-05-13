#encoding:utf-8
#author:Mats Boisen
#project:boxeeplay
#repository:https://bitbucket.org/hesapesa/boxeeplay
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/license/GPL/2.0/)

# TODO
# Tv4mc module
# Ladda om xml.tv4play.se - hur ofta?
# Sökning - hur?
# Attribut för titel från xml.tv4play.se skall sättas på episoderna
# Gör en sajt och branda den
# app-ikon
# Spela upp program - via flowplayer? Direkt men med kontrollscript?
# ta fram video-id med split('?')
# Se till att alla episoder laddas (pokemon laddar 6*17 men ej 170)
# Sätt episodattribut på samma sätt som för svt
# Alla titlar har samma bild?
# Episoder - Postis Per - blir fel i inläsningen i avsnitt 6
#

import threading
from urllib import quote_plus
import urllib2
import xml.dom.minidom
import re
import datetime
import mc
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

def RetrieveStream(url):
    BPTraceEnter(url)
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        data = response.read()
        response.close()
        BPTraceExit("Returning %s" % data)
        return data
    except:
        BPLog("tv4xml: http download failed, url=%s" % url, Level.ERROR)
        return str("")

def RetrieveXmlStream(url):
    BPTraceEnter(url)
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        data = response.read()
        response.close()
        root = xml.dom.minidom.parseString(data)
        BPTraceExit("Returning %s" % root)
        return root
    except:
        root = xml.dom.minidom.parseString("<error>error</error>")
        BPLog("tv4xml: http download failed, url=%s" % url, Level.ERROR)
        BPTraceExit("Returning %s" % root)
        return  root

def GetElementData(node, name):
    #BPTraceEnter("%s, %s" % (node, name))
    try:
        #BPTraceExit()
        return node.getElementsByTagName(name)[0].childNodes[0].data.encode("utf-8")
    except:
        #BPTraceExit()
        return str("")

def GetElementAttribute(node, name, attribute):
    #BPTraceEnter("%s, %s, %s" % (node, name, attribute))
    try:
        #BPTraceExit()
        return node.getElementsByTagName(name)[0].getAttribute(attribute).encode("utf-8")
    except:
        #BPTraceExit()
        return str("")

def CreateRtmpPath(domain, url):
    BPTraceEnter("%s, %s" % (domain, url))
    url = 'http://boxeeplay.tv/flowplayer/index.html?net=' + str(domain) + '&id=' + str(url)
    mc.LogInfo("tv4xml: url:" + url)
    url = quote_plus(url)
    jsActions = quote_plus('http://boxeeplay.tv/flowplayer/control.js')
    path = 'flash://boxeeplay.tv/src=' + str(url) + '&bx-jsactions=' + str(jsActions)
    BPLog("tv4xml: Media path converted to: %s" % path, Level.DEBUG)
    BPTraceExit("Returning %s" % path)
    return path

def GetVideoPath(videoId):
    BPTraceEnter(videoId)
	
    base = str("")
    source = str("")
    bestBitRate = 0

    root = RetrieveXmlStream("http://anytime.tv4.se/webtv/metafileFlash.smil?p=" + str(videoId) + "&bw=1000&emulate=true&sl=true")

    headElement = root.getElementsByTagName("head")[0]
    for metaElement in headElement.getElementsByTagName("meta"):
        baseAttribute = metaElement.getAttribute("base").encode("utf-8")
        if len(str(baseAttribute)) > 0:
            base = baseAttribute			
            mc.LogInfo("tv4xml: base: " + base) 

    bodyElement = root.getElementsByTagName("body")[0]
    switchElement = bodyElement.getElementsByTagName("switch")[0]
    for videoElement in switchElement.getElementsByTagName("video"):
        src = videoElement.getAttribute("src").encode("utf-8")
        systemBitRate = videoElement.getAttribute("system-bitrate").encode("utf-8")
        bitRate = int(systemBitRate)
        if bitRate > bestBitRate:
            bestBitRate = bitRate
            mc.LogInfo("tv4xml: bitrate: " + str(bitRate)) 
            source = src
            mc.LogInfo("tv4xml: source: " + source) 
    path = CreateRtmpPath(base, source)
    mc.LogInfo("tv4xml: path: " + path)
    BPTraceExit("Returning %s" % path)
    return path

def GetPremiumVideoPath(videoId):
    BPTraceEnter(videoId)
    path2500 = str("")
    path1500 = str("")
    path800 = str("")
    path300 = str("")
    root = RetrieveXmlStream("http://premium.tv4play.se/api/web/asset/" + str(videoId) + "/play")
    for itemsElement in root.getElementsByTagName("items"):
        for itemElement in itemsElement.getElementsByTagName("item"):
            bitrate = GetElementData(itemElement, "bitrate")
            mc.LogInfo("tv4xml: bitrate: " + bitrate) 
            mediaFormat = GetElementData(itemElement, "mediaFormat")
            mc.LogInfo("tv4xml: mediaFormat: " + mediaFormat)
            scheme = GetElementData(itemElement, "scheme")
            mc.LogInfo("tv4xml: scheme: " + scheme)
            domain = GetElementData(itemElement, "base")
            mc.LogInfo("tv4xml: domain: " + domain)
            url = GetElementData(itemElement, "url")
            mc.LogInfo("tv4xml: url: " + url)
            if mediaFormat == "mp4":
                if scheme == "rtmp" or scheme == "rtmpe":
                    if bitrate == "2500":
                        path2500 = CreateRtmpPath(domain, url)
                        mc.LogInfo("tv4xml: path: " + path2500)
                    if bitrate == "1500":
                        path1500 = CreateRtmpPath(domain, url)
                        mc.LogInfo("tv4xml: path: " + path1500)
                    if bitrate == "800":
                        path800 = CreateRtmpPath(domain, url)
                        mc.LogInfo("tv4xml: path: " + path800)
                    if bitrate == "300":
                        path300 = CreateRtmpPath(domain, url)
                        mc.LogInfo("tv4xml: path: " + path300)
    path = path300
    if len(path800) > 0:
        path = path800
    if len(path1500) > 0:
        path = path1500
    if len(path2500) > 0:
        path = path2500
    mc.LogInfo("tv4xml: path: " + path)
    BPTraceExit("Returning %s" % path)
    return path
  
def GetXmlTv4Play():
    app = mc.GetApp()
    config = app.GetLocalConfig()
    data = config.GetValue("XmlTv4Play")
    if len(str(data)) == 0:
        data = RetrieveStream("http://xml.tv4play.se")    
        config.SetValue("XmlTv4Play", data)	
    root = xml.dom.minidom.parseString(data)
    BPTraceExit("Returning %s" % root)
    return root

def GetCategories():
    items = mc.ListItems()
    root = GetXmlTv4Play()
    topCategoriesElement = root.getElementsByTagName("categories")[0]
    for topCategoryElement in topCategoriesElement.getElementsByTagName("category"):
        name = topCategoryElement.getAttribute("name").encode("utf-8")
        if name == "tv4playnew.se":
            categoriesElement = topCategoryElement.getElementsByTagName("categories")[0]
            for categoryElement in categoriesElement.getElementsByTagName("category"):
                name = categoryElement.getAttribute("name").encode("utf-8")
                id = categoryElement.getAttribute("id").encode("utf-8")
                item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                item.SetContentType("text/xml")
                item.SetLabel(name)
                item.SetPath("http://xml.tv4play.se")
                item.SetAuthor("TV4")
                item.SetProperty("id", id)
                item.SetReportToServer(False)
                item.SetAddToHistory(False)
                items.append(item)
    return items

def GetTitles(categoryId):
    items = mc.ListItems()
    root = GetXmlTv4Play()
    topCategoriesElement = root.getElementsByTagName("categories")[0]
    for topCategoryElement in topCategoriesElement.getElementsByTagName("category"):
        topName = topCategoryElement.getAttribute("name").encode("utf-8")
        if topName == "tv4playnew.se":
            categoriesElement = topCategoryElement.getElementsByTagName("categories")[0]
            for categoryElement in categoriesElement.getElementsByTagName("category"):
                categoryName = categoryElement.getAttribute("name").encode("utf-8")
                id = categoryElement.getAttribute("id").encode("utf-8")
                if id == categoryId:
                    programFormatsElement = categoryElement.getElementsByTagName("programformats")[0]
                    for programFormatElement in programFormatsElement.getElementsByTagName("programformat"):
                        item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                        item.SetContentType("text/xml")
                        name = programFormatElement.getAttribute("name").encode("utf-8")
                        item.SetLabel(name)
                        item.SetTitle(name)
                        item.SetTVShowTitle(name)
                        id = programFormatElement.getAttribute("id").encode("utf-8")
                        item.SetProperty("id", id)
                        item.SetDescription(GetElementData(programFormatElement, "text"))
                        item.SetProviderSource(GetElementData(programFormatElement, "channel"))
                        premium = GetElementData(programFormatElement, "premium")
                        item.SetProperty("premium", premium)
                        airtime = GetElementData(programFormatElement, "airtime")
                        item.SetProperty("airtime", airtime)
                        item.SetThumbnail(GetElementData(programFormatElement, "largeimage"))
                        item.SetIcon(GetElementData(programFormatElement, "smallformatimage"))
                        item.SetGenre(categoryName)
                        item.SetReportToServer(False)
                        item.SetAddToHistory(False)
                        item.SetPath("http://xml.tv4play.se")
                        item.SetAuthor("TV4")
                        items.append(item)
                        item.Dump()
                    return items
    return items

def GetEpisodes(titleId):
    items = mc.ListItems()
    data = RetrieveStream("http://www.tv4play.se/search/search?rows=200&order=desc&categoryids=" + titleId + "&sorttype=date&start=0")
    data = "<root>" + data + "</root>"
    root = xml.dom.minidom.parseString(data)
    for divElement in root.getElementsByTagName("div"):
        className = divElement.getAttribute("class").encode("utf-8")
        if className == "module-content":
            sectionElement = divElement.getElementsByTagName("section")[0]
            ulElement = sectionElement.getElementsByTagName("ul")[0]
            for liElement in ulElement.getElementsByTagName("li"):
                item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
                item.SetContentType("text/html")
                pElement = liElement.getElementsByTagName("p")[0]
                aElement = pElement.getElementsByTagName("a")[0]	
                path = aElement.getAttribute("href").encode("utf-8")				
                videoId = path.split("videoid=")[1]
                item.SetPath("http://www.tv4play.se/flash%2ftv4play30Default_sa.swf?vid=" + videoId)
                item.SetProperty("id", path)
                item.SetThumbnail(GetElementAttribute(aElement, "img", "src"))
                item.SetTitle(GetElementAttribute(aElement, "img", "alt"))
                item.SetLabel(GetElementAttribute(aElement, "img", "alt"))
                innerDivElement = liElement.getElementsByTagName("div")[0]
                for innerPElement in innerDivElement.getElementsByTagName("p"):
                    className = innerPElement.getAttribute("class").encode("utf-8")
                    if className == "program-format":
                        item.SetTVShowTitle(GetElementAttribute(innerPElement, "a", "title"))
                    if className == "video-description":
                        try:
                            item.SetDescription(innerPElement.childNodes[0].data.encode("utf-8"))
                        except:
                            item.SetDescription("")
                for innerMostDivElement in innerDivElement.getElementsByTagName("div"):
                    className = innerMostDivElement.getAttribute("class").encode("utf-8")
                    if className == "video-meta":
                        item.SetProperty("airtime", GetElementData(innerMostDivElement, "p"))
                item.SetProviderSource("TV4")
                item.SetGenre("TOBESET")
                item.SetReportToServer(True)
                item.SetAddToHistory(True)
                items.append(item)
                item.Dump()
    return items                        



  
       

   
   
	
def GetDirectory(url, maxResults=0):
    BPTraceEnter(url)
    start = 1
    
    if maxResults <= 0:
        maxResults = 9999
    
    BPLog("svtxml: %s" % url, Level.DEBUG)
    root = RetrieveXmlStream(url)
    
    totalResults = int(root.getElementsByTagName("opensearch:totalResults")[0].childNodes[0].data)
    if totalResults > maxResults:
        totalResults = maxResults
        
    listItems = ProcessDirectoryPage(root)

    noOfItems = len(listItems)
    start = start + noOfItems
    while start <= totalResults:
        pageUrl = url + "&start=" + str(start)
        pageListItems = GetDirectoryPage(pageUrl)
        start = start + len(pageListItems)
        for pageListItem in pageListItems:
            listItems.append(pageListItem)
        
    BPLog("svtxml: Loaded %s items." % str(len(listItems)), Level.DEBUG)
    BPTraceExit("Returning %s" % listItems)
    return listItems
        
def ProcessDirectoryPage(root) :
    BPTraceEnter(root)
    items = mc.ListItems()
        
    for node in root.getElementsByTagName("item"):
        item = AddItem(items, node)

    BPTraceExit("Returning %s" % items)
    return items

def GetDirectoryPage(url) :
    BPTraceEnter(url)
    BPLog("svtxml: %s" %url, Level.DEBUG)
    root = RetrieveXmlStream(url)
    r = ProcessDirectoryPage(root)
    BPTraceExit("Returning %s" % r)
    return r

