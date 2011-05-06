#encoding:utf-8
#author:Mats Boisen
#project:boxeeplay
#repository:https://bitbucket.org/hesapesa/boxeeplay
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/license/GPL/2.0/)

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
        if (len(str(baseAttribute)) > 0):
            base = baseAttribute			
            mc.LogInfo("tv4xml: base: " + base) 

    bodyElement = root.getElementsByTagName("body")[0]
    switchElement = bodyElement.getElementsByTagName("switch")[0]
    for videoElement in switchElement.getElementsByTagName("video"):
        src = videoElement.getAttribute("src").encode("utf-8")
        systemBitRate = videoElement.getAttribute("system-bitrate").encode("utf-8")
        bitRate = int(systemBitRate)
        if (bitRate > bestBitRate):
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
            if (mediaFormat == "mp4"):
                if (scheme == "rtmp" or scheme == "rtmpe"):
                    if (bitrate == "2500"):
                        path2500 = CreateRtmpPath(domain, url)
                        mc.LogInfo("tv4xml: path: " + path2500)
                    if (bitrate == "1500"):
                        path1500 = CreateRtmpPath(domain, url)
                        mc.LogInfo("tv4xml: path: " + path1500)
                    if (bitrate == "800"):
                        path800 = CreateRtmpPath(domain, url)
                        mc.LogInfo("tv4xml: path: " + path800)
                    if (bitrate == "300"):
                        path300 = CreateRtmpPath(domain, url)
                        mc.LogInfo("tv4xml: path: " + path300)
    path = path300
    if (len(path800) > 0):
        path = path800
    if (len(path1500) > 0):
        path = path1500
    if (len(path2500) > 0):
        path = path2500
    mc.LogInfo("tv4xml: path: " + path)
    BPTraceExit("Returning %s" % path)
    return path
  
def GetXmlTv4Play():
    app = mc.GetApp()
    config = app.GetLocalConfig()
    data = config.GetValue("XmlTv4Play")
    if (len(str(data)) == 0):
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
        if (name == "tv4playnew.se"):
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
        if (topName == "tv4playnew.se"):
            categoriesElement = topCategoryElement.getElementsByTagName("categories")[0]
            for categoryElement in categoriesElement.getElementsByTagName("category"):
                categoryName = categoryElement.getAttribute("name").encode("utf-8")
                id = categoryElement.getAttribute("id").encode("utf-8")
                if (id == categoryId):
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
                        mc.LogInfo("tv4xml hej")
                        item.Dump()
                    return items
    return items



	
def GetDirectory(url, maxResults=0):
    BPTraceEnter(url)
    start = 1
    
    if (maxResults <= 0):
        maxResults = 9999
    
    BPLog("svtxml: %s" % url, Level.DEBUG)
    root = RetrieveXmlStream(url)
    
    totalResults = int(root.getElementsByTagName("opensearch:totalResults")[0].childNodes[0].data)
    if (totalResults > maxResults):
        totalResults = maxResults
        
    listItems = ProcessDirectoryPage(root)

    noOfItems = len(listItems)
    start = start + noOfItems
    while (start <= totalResults):
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

def SetItemImages(node, item) :
    BPTraceEnter("%s, %s" % (node, item))
    imageNo = 0
    mediaContentNodes = node.getElementsByTagName("media:content")
    for mediaContentNode in mediaContentNodes:
        if (mediaContentNode.getAttribute("medium").encode("utf-8") == "image"):
            imageUrl = mediaContentNode.getAttribute("url").encode("utf-8")
            if (imageNo == 0):
                item.SetIcon(imageUrl)
                item.SetThumbnail(imageUrl)
            item.SetImage(imageNo, imageUrl)
            imageNo = imageNo + 1
    BPTraceExit()
    
def AddItem(items, node):
    BPTraceEnter("%s, %s" % (items, node))
    videoType = mc.ListItem.MEDIA_VIDEO_CLIP
    try:
        episode = int(GetElementAttribute(node, "svtplay:programInfo", "episodeNo"))
        videoType = mc.ListItem.MEDIA_VIDEO_EPISODE
    except:
        episode = 0

    item = mc.ListItem(videoType)

    try:
        item.SetPath(GetElementData(node, "link"))
        item.SetContentType("text/html")
        item.SetTitle(GetElementData(node, "title"))
        item.SetTVShowTitle(GetElementData(node, "svtplay:titleName"))
        item.SetLabel(GetElementData(node, "title"))
        item.SetDescription(GetElementData(node, "description"))
        item.SetAuthor(GetElementData(node, "author"))
        item.SetProviderSource(GetElementData(node, "svtplay:broadcastChannel"))
        item.SetThumbnail(GetElementAttribute(node, "media:thumbnail", "url"))
        item.SetIcon(GetElementData(node, "svtplay:logotype"))
        SetItemImages(node, item)
        item.SetProperty("id", GetElementData(node, "svtplay:titleId"))
        item.SetGenre(LookupCategory(str(GetElementData(node, "svtplay:category"))))
        item.SetReportToServer(False)
        item.SetAddToHistory(False)
        if episode > 0:
            item.SetEpisode(episode)

        SetDate(item, node)

        SetAlternatePaths(item, node)

        items.append(item)
    except:
        BPLog("svtxml: List item creation failed, url =%s" % item.GetPath(), Level.ERROR)
    BPTraceExit()

def SetAlternatePaths(item, node):
    BPTraceEnter("%s, %s" % (item, node))
    item.SetProperty("replacedPath", "0")
    for mediaGroup in node.getElementsByTagName("media:group"):
        mediaNodes = mediaGroup.getElementsByTagName("media:content")
        AddFlowplayerPaths(item, mediaNodes)
    DumpAlternateMediaPaths(item, node)
    BPTraceExit()
		
def DumpAlternateMediaPaths(item, node):
    BPTraceEnter("%s, %s" %(item, node))
    if item.GetProperty("replacedPath") == "0":
        for mediaGroup in node.getElementsByTagName("media:group"):
            mediaNodes = mediaGroup.getElementsByTagName("media:content")
            if (len(mediaNodes) > 0):
                BPLog("svtxml: No playable media path was found! Alternative paths listed below.")
                for mediaNode in mediaNodes:	
                    mediaLabel = GetElementData(mediaNode, "svtplay:videoIdentifier")
                    mediaPath = mediaNode.getAttribute("url").encode("utf-8")
                    mediaType = mediaNode.getAttribute("type").encode("utf-8")
                    BPLog("svtxml: %s - %s - %s" %(mediaLabel, mediaType, mediaPath))
    BPTraceExit()
        
def AddFlowplayerPaths(item, mediaNodes):
    BPTraceEnter("%s, %s" %(item, mediaNodes))
    AddFlowplayerPath(item, mediaNodes, "mp4-e-v1", "HD-kvalitet, 720p, 2400 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-hd-webb-tv.gif")
    AddFlowplayerPath(item, mediaNodes, "mp4-d-v1", "Hög kvalitet, 1400 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-high-webb-tv.gif")
    AddFlowplayerPath(item, mediaNodes, "mp4-c-v1", "Medelkvalitet, 850 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-medium-webb-tv.gif")
    AddDirectPath(item, mediaNodes, "wmv-a-v1", "Låg kvalitet, 340 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-low-webb-tv.gif")
    AddDirectPath(item, mediaNodes, "video/x-ms-asf", "Låg kvalitet, 340 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-low-webb-tv.gif")
    BPTraceExit()
    
    
def AddFlowplayerPath(item, mediaNodes, label, title, thumbnailPath):
    BPTraceEnter("%s, %s, %s, %s, %s" % (item, mediaNodes, label, title, thumbnailPath))
    for mediaNode in mediaNodes:
        mediaLabel = GetElementData(mediaNode, "svtplay:videoIdentifier")
        mediaPath = mediaNode.getAttribute("url").encode("utf-8")
        mediaType = mediaNode.getAttribute("type").encode("utf-8")
        if mediaType == "video/mp4" and mediaLabel == label:
            if mediaPath[:5] == "rtmp:" or mediaPath[:6] == "rtmpe:":
                mediaPath = CreateRtmpPath(mediaPath)
                item.AddAlternativePath(title, mediaPath, "text/html", thumbnailPath) 
                try:
                    duration =  int(mediaNode.getAttribute("duration").encode("utf-8"))
                except:
                    duration = 0
                if duration > 0:
                    item.SetDuration(duration)
                item.SetReportToServer(True)
                item.SetAddToHistory(True)
                if item.GetProperty("replacedPath") == "0":
                    item.SetProperty("replacedPath", "1")
                    item.SetPath(str(mediaPath))
    BPTraceExit()
                
def AddDirectPath(item, mediaNodes, label, title, thumbnailPath):
    BPTraceEnter("%s, %s, %s, %s, %s" % (item, mediaNodes, label, title, thumbnailPath))
    for mediaNode in mediaNodes:
        mediaLabel = GetElementData(mediaNode, "svtplay:videoIdentifier")
        mediaPath = mediaNode.getAttribute("url").encode("utf-8")
        mediaType = mediaNode.getAttribute("type").encode("utf-8")
        if mediaLabel == label:
			item.AddAlternativePath(title, mediaPath, mediaType, thumbnailPath) 
			try:
				duration =  int(mediaNode.getAttribute("duration").encode("utf-8"))
			except:
				duration = 0
			if duration > 0:
				item.SetDuration(duration)
			item.SetReportToServer(True)
			item.SetAddToHistory(True)
			if item.GetProperty("replacedPath") == "0":
				item.SetProperty("replacedPath", "1")
				item.SetPath(str(mediaPath))
				item.SetContentType(mediaType)
    BPTraceExit()



def LookupCategory(id):
    BPTraceEnter(id)
    if (id == "96240"):
        r = "Barn"
    elif (id == "96242"):
        r = "Film"
    elif (id == "96247"):
        r = "Drama"
    elif (id == "96243"):
        r = "Kultur"
    elif (id == "96245"):
        r = "Nöje"
    elif (id == "96246"):
        r = "Samhälle"
    elif (id == "96241"):
        r = "Fakta"
    elif (id == "96244"):
        r = "Nyheter"
    elif (id == "96248"):
        r = "Sport"
    elif (id == "98382"):
        r = "Öppet arkiv"
    else:
        r = "Okänd (" + str(id) + ")"
    BPTraceExit("Returning %s" % r)
    return r
        
def SetDate(item, node):
    BPTraceEnter("%s, %s" % (item, node))
    try:
        dateString = GetElementData(node, "pubDate")
        day = dateString[5:7]
        monthString = dateString[8:11]
        year = dateString[12:16]
        
        if monthString == "Jan":
            month = 1
        elif monthString == "Feb":
            month = 2
        elif monthString == "Mar":
            month = 3
        elif monthString == "Apr":
            month = 4
        elif monthString == "May":
            month = 5
        elif monthString == "Jun":
            month = 6
        elif monthString == "Jul":
            month = 7
        elif monthString == "Aug":
            month = 8
        elif monthString == "Sep":
            month = 9
        elif monthString == "Oct":
            month = 10
        elif monthString == "Nov":
            month = 11
        elif monthString == "Dec":
            month = 12
        
        item.SetDate(int(year), int(month), int(day))
    except:
        BPLog("svtxml: Failed to set item date" ,Level.ERROR)
    BPTraceExit()
