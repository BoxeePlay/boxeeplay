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

def GetDirectory(url, maxResults=0):
    BPTraceEnter(url)
    start = 1
    
    if (maxResults <= 0):
        maxResults = 9999
    
    #mc.LogDebug("svtxml:" + url)
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
        
    #mc.LogDebug("svtxml: Loaded " + str(len(listItems)) + " items:")
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
    #mc.LogDebug("svtxml:" + url)
    BPLog("svtxml: %s" %url, Level.DEBUG)
    root = RetrieveXmlStream(url)
    r = ProcessDirectoryPage(root)
    BPTraceExit("Returning %s" % r)
    return r
    
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
        item.SetProperty("id", GetElementData(node, "svtplay:titleId"))
        item.SetGenre(LookupCategory(str(GetElementData(node, "svtplay:category"))))
        item.SetReportToServer(False)
        item.SetAddToHistory(False)
        if episode > 0:
            item.SetEpisode(episode)

        SetDate(item, node)

        SetAlternatePaths(item, node)

        items.append(item)
        item.Dump()
    except:
        #mc.LogError("svtxml: List item creation failed, url=" + item.GetPath())
        BPLog("svtxml: List item creation failed, url =%s" % item.GetPath(), Level.ERROR)
    BPTraceExit()

def SetAlternatePaths(item, node):
    BPTraceEnter("%s, %s" % (item, node))
    item.SetProperty("replacedPath", "0")
    for mediaGroup in node.getElementsByTagName("media:group"):
        mediaNodes = mediaGroup.getElementsByTagName("media:content")
        AddRtmpPaths(item, mediaNodes)
    BPTraceExit()
        
def AddRtmpPaths(item, mediaNodes):
    BPTraceEnter("%s, %s" %(item, mediaNodes))
    AddRtmpPath(item, mediaNodes, "mp4-e-v1", "HD-kvalitet, 720p, 2400 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-hd-webb-tv.gif")
    AddRtmpPath(item, mediaNodes, "mp4-c-v1", "H�g kvalitet, 1400 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-high-webb-tv.gif")
    AddRtmpPath(item, mediaNodes, "mp4-b-v1", "Medelkvalitet, 850 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-medium-webb-tv.gif")
    AddRtmpPath(item, mediaNodes, "mp4-a-v1", "L�g kvalitet, 340 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-low-webb-tv.gif")
    BPTraceExit()
    
def CreateRtmpPath(path):
    BPTraceEnter(path)
    domain = re.compile('^(.*?)/kluster', re.DOTALL + re.IGNORECASE).search(str(path)).group(1)
    id = re.compile(domain + '/(.*?)$', re.DOTALL + re.IGNORECASE).search(str(path)).group(1)
    url = 'http://boxeeplay.tv/flowplayer/index.html?net=' + str(domain) + '&id=mp4:' + str(id)
    url = quote_plus(url)
    jsActions = quote_plus('http://boxeeplay.tv/flowplayer/flow.js')
    path = 'flash://boxeeplay.tv/src=' + str(url) + '&bx-jsactions=' + str(jsActions)
    #mc.LogDebug("svtxml: Media path converted to: " + path)
    BPLog("svtxml: Media path converted to: %s" % path, Level.DEBUG)
    BPTraceExit("Returning %s" % path)
    return path
    
def AddRtmpPath(item, mediaNodes, label, title, thumbnailPath):
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
        #mc.LogError("svtxml: http download failed, url=" + url)
        BPLog("svtxml: http download failed, url=%s" % url, Level.ERROR)
        BPTraceExit("Returning %s" % root)
        return  root

def GetElementData(node, name):
    BPTraceEnter("%s, %s" % (node, name))
    try:
        BPTraceExit()
        return node.getElementsByTagName(name)[0].childNodes[0].data.encode("utf-8")
    except:
        BPTraceExit()
        return str("")

def GetElementAttribute(node, name, attribute):
    BPTraceEnter("%s, %s, %s" % (node, name, attribute))
    try:
        BPTraceExit()
        return node.getElementsByTagName(name)[0].getAttribute(attribute).encode("utf-8")
    except:
        BPTraceExit()
        return str("")

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
        r = "Ökand (" + str(id) + ")"
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
        #mc.LogError("svtxml: Failed to set item date")
        BPLog("svtxml: Failed to set item date" ,Level.ERROR)
    BPTraceExit()
