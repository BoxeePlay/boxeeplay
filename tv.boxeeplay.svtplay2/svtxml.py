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
import time
import calendar
import mc
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

def GetDirectory(url, maxResults=0, start=1):
    BPTraceEnter(url)
    
    if (maxResults <= 0):
        maxResults = 9999
    
    BPLog("svtxml: %s" % url, Level.DEBUG)
    pageUrl = url + "&start=" + str(start)
    root = RetrieveXmlStream(pageUrl)
    
    totalResults = int(root.getElementsByTagName("opensearch:totalResults")[0].childNodes[0].data)
    completeResults = totalResults
    if (completeResults > maxResults):
        completeResults = maxResults
        
    listItems = ProcessDirectoryPage(root)

    noOfItems = len(listItems)
    start = start + noOfItems
    # A bit dangerous this loop,
    # If an exception is caught inside and items are not added as they should..
    while (start <= completeResults):
        pageUrl = url + "&start=" + str(start)
        pageListItems = GetDirectoryPage(pageUrl)
        start = start + len(pageListItems)
        for pageListItem in pageListItems:
            listItems.append(pageListItem)

    for listItem in listItems:
        listItem.SetProperty("total-results", str(totalResults))

    BPLog("svtxml: Loaded %s items." % str(len(listItems)), Level.DEBUG)
    BPTraceExit("Returning %s" % listItems)
    return listItems
        
def ProcessDirectoryPage(root) :
    BPTraceEnter(root)
    items = mc.ListItems()
        
    for node in root.getElementsByTagName("item"):
        AddItem(items, node)

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

def GetMediaType(node):
    expressionType = "sample"
    mediaContentNodes = node.getElementsByTagName("media:content")
    for mediaContentNode in mediaContentNodes:
        if (mediaContentNode.getAttribute("medium").encode("utf-8") == "video"):
            expressionType = mediaContentNode.getAttribute("expression")
            break
    if expressionType == "full":
        return "Fullängd"
    if expressionType == "nonstop":
        return "Direkt"
    return "Klipp"
    

def AddItem(items, node):
    BPTraceEnter("%s, %s" % (items, node))

    item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)

    try:
        episode = int(GetElementAttribute(node, "svtplay:programInfo", "episodeNo"))
    except:
        episode = 0

    try:


        item.SetPath(GetElementData(node, "link"))
        item.SetContentType("text/html")
        title = GetElementData(node, "title")
        item.SetTitle(title)
        item.SetLabel(title)
        show = GetElementData(node, "svtplay:titleName")
        item.SetTVShowTitle(show)
        if len(show) > 0:
            item.SetLabel("%s - %s" %(show,title))
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
        #if episode > 0:
        #    item.SetEpisode(episode) #Funkar dåligt i Boxees interface med SVT

        item.SetProperty("media-type", GetMediaType(node))
        SetDate(item, node)
        SetExpireDate(item, node)
        SetAlternatePaths(item, node)

        jsActions = quote_plus('http://boxeeplay.tv/flowplayer/flow.js')
        p = item.GetPath()
        if p.startswith("flash://"):
            item.SetPath(p + "&bx-jsactions=" + jsActions)
        else:
            SetBxJxActionsPath(item)

        SetGuiInfo(item)
        if item.GetProperty("id") != "":
            items.append(item)
    except Exception, e:
        BPLog("svtxml: AddItem failed to load item, url =%s, Exception: %s" % (item.GetPath(),str(e)), Level.ERROR)
        items.append(mc.ListItem())

    BPTraceExit()

def SetBxJxActionsPath(item):
    url = quote_plus(item.GetPath())
    jsActions = quote_plus('http://boxeeplay.tv/bx-jsactions/svtplay.js')
    path = "flash://boxeeplay.tv/src=" + str(url) + "&bx-jsactions=" + jsActions
    item.SetPath(path)

def SetAlternatePaths(item, node):
    BPTraceEnter("%s, %s" % (item, node))
    item.SetProperty("replacedPath", "0")
    for mediaGroup in node.getElementsByTagName("media:group"):
        mediaNodes = mediaGroup.getElementsByTagName("media:content")
        AddFlowplayerPaths(item, mediaNodes)
    #DumpAlternateMediaPaths(item, node)
    if item.GetProperty("replacedPath") == "1" and item.GetPath().startswith("flash://"):
        AddRtmpAlternatives(item)
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

def CreateRtmpDomain(path):
    return re.compile('^(.*/_definst_).*', re.DOTALL + re.IGNORECASE).search(str(path)).group(1)
    
def CreateRtmpId(path):
    return 'mp4:' + re.compile('^.*/_definst_/(.*?)$', re.DOTALL + re.IGNORECASE).search(str(path)).group(1)

def CreateRtmpPath(domain, id, bitrate):
    BPTraceEnter("domain: %s, id: %s" %(domain,id))
    url = 'http://boxeeplay.tv/flowplayer/index.html?net=' + str(domain) + '&id=' + str(id) + '&bitrate=' + str(bitrate)
    url = quote_plus(url)
    path = 'flash://boxeeplay.tv/src=' + str(url)
    BPLog("svtxml: Media path converted to: %s" % path, Level.DEBUG)
    BPTraceExit()
    return path

def AddRtmpAlternatives(item):
    '''Run this function only when you have finished building the ListItem
    with path and alternative paths. It uses properties stored in the item.
    Properties needed:
        alt-paths            | Nr of alternative paths (indexing starts at 0)
        alt-path-[i]-type    | Type of alt-path with index i "video/mp4" is used
        alt-path-[i]-stream  | Stream path of alt-path, complete with protocol (rtmpe:// and rtmp:// may occur)
        alt-path-[i]-bitrate | Bitrate of alt-path with index i. Used by the player.
    '''
    BPTraceEnter()
    try:
        amount = int(item.GetProperty("alt-paths"))
    except:
        # Normal for samples so just continue
        amount = 0

    path = item.GetPath()
    if not path.startswith("flash://"):
        return

    protMatch = re.match(".*(rtmp|rtmpe)%3A",path)
    if protMatch:
        protocol = protMatch.group(1) + "://"
        BPLog("Matches: " + protMatch.group(0), Level.DEBUG)
        BPLog("Flowplayer streaming protocol matched to: " + protocol, Level.DEBUG)
    else:
        BPLog("No match on streaming protocol.")
        protocol = "rtmpe://"

    try:
        alternatives = [ ( n
                         , item.GetProperty("alt-path-%s-type" %n)
                         , item.GetProperty("alt-path-%s-stream" %n)
                         , int(item.GetProperty("alt-path-%s-bitrate" %n))
                         ) for n in range(amount)
                       ]
    except Exception, e:
        item.Dump()
        BPLog("svtxml: Error when reading alternative paths from item %s: %s" %(item.GetLabel(),e), Level.ERROR)
        alternatives = []

    for (i,type,stream,bits) in alternatives:
        if type == "video/mp4" and stream.startswith(protocol):
            path += quote_plus("&stream-%s=%s" %(i,CreateRtmpId(stream)))
            path += quote_plus("&bitrate-%s=%s" %(i,bits))
        else:
            BPLog("svtxml: Ignoring stream as rtmp(e) alternative: %s" %stream, Level.DEBUG)
    item.SetPath(path)
    BPTraceExit()
        
def AddFlowplayerPaths(item, mediaNodes):
    BPTraceEnter("%s, %s" %(item, mediaNodes))
    AddFlowplayerPath(item, mediaNodes, "mp4-e-v1", "HD-kvalitet, 720p, 2400 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-hd-webb-tv.gif")
    AddFlowplayerPath(item, mediaNodes, "mp4-d-v1", "Hög kvalitet, 1400 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-high-webb-tv.gif")
    AddFlowplayerPath(item, mediaNodes, "mp4-c-v1", "Medelkvalitet, 850 kbs.", "http://svt.se/content/1/c8/01/39/57/98/play-medium-webb-tv.gif")
    BPTraceExit()

def AddAlternativeStream(item, type, stream, bitrate):
    BPTraceEnter("item: %s, type: %s, stream: %s, bitrate: %s" %(item.GetLabel(), type, stream, bitrate))
    try:
        i = int(item.GetProperty("alt-paths"))
    except Exception, e:
        BPLog("Nr of alternative paths not set for item %s: %s" %(item.GetLabel(), item.GetProperty("alt-paths")), Level.DEBUG)
        i = 0
    item.SetProperty("alt-path-%s-type" %i, str(type))
    item.SetProperty("alt-path-%s-stream" %i, str(stream))
    item.SetProperty("alt-path-%s-bitrate" %i, str(bitrate))
    i += 1
    item.SetProperty("alt-paths", str(i))
    BPTraceExit()
    
def AddFlowplayerPath(item, mediaNodes, label, title, thumbnailPath):
    BPTraceEnter("%s, %s, %s, %s" % (item.GetLabel(), label, title, thumbnailPath))
    for mediaNode in mediaNodes:
        if mediaNode.getAttribute("expression").encode("utf-8") != "full":
            continue
        mediaLabel = GetElementData(mediaNode, "svtplay:videoIdentifier")
        mediaPath = mediaNode.getAttribute("url").encode("utf-8")
        mediaType = mediaNode.getAttribute("type").encode("utf-8")
        BPLog("Attempting to add alternative path. item: %s, type: %s, path: %s" %(item.GetLabel(), mediaType, mediaPath), Level.DEBUG)
        if mediaType == "video/mp4" and mediaLabel == label:
            if mediaPath[:5] == "rtmp:" or mediaPath[:6] == "rtmpe:":
                #item.AddAlternativePath(title, mediaPath, "text/html", thumbnailPath) 
                try:
                    duration =  int(mediaNode.getAttribute("duration").encode("utf-8"))
                except:
                    duration = 0
                if duration > 0:
                    item.SetDuration(duration)
                    item.SetProperty("duration",str(duration)) #forall GetDuration() == 0 ...
                item.SetReportToServer(True)
                item.SetAddToHistory(True)
                try:
                    bitrate = int(float(mediaNode.getAttribute("bitrate").encode("utf-8")))
                except:
                    BPLog("bitrate could not be found/parsed")
                    bitrate = 0
                if item.GetProperty("replacedPath") == "0":
                    item.SetProperty("replacedPath", "1")
                    item.SetPath(CreateRtmpPath(CreateRtmpDomain(mediaPath),CreateRtmpId(mediaPath),bitrate))
                else:
                    BPLog("Adding alternative stream: %s for item %s" %(mediaPath, item.GetLabel()), Level.DEBUG)
                    AddAlternativeStream(item, mediaType, mediaPath, bitrate)
    BPTraceExit()
                
def AddDirectPath(item, mediaNodes, label, title, thumbnailPath):
    BPTraceEnter("%s, %s, %s, %s, %s" % (item, mediaNodes, label, title, thumbnailPath))
    for mediaNode in mediaNodes:
        mediaLabel = GetElementData(mediaNode, "svtplay:videoIdentifier")
        mediaPath = mediaNode.getAttribute("url").encode("utf-8")
        mediaType = mediaNode.getAttribute("type").encode("utf-8")
        if mediaLabel == label:
            #item.AddAlternativePath(title, mediaPath, mediaType, thumbnailPath) 
            try:
                duration =  int(mediaNode.getAttribute("duration").encode("utf-8"))
            except:
                duration = 0
            if duration > 0:
                item.SetDuration(duration)
                item.SetProperty("duration", str(duration)) #forall GetDuration() == 0 ...
            item.SetReportToServer(True)
            item.SetAddToHistory(True)
            try:
                bitrate = int(float(mediaNode.getAttribute("bitrate").encode("utf-8")))
            except:
                BPLog("bitrate could not be found/parsed")
                bitrate = 0
            if item.GetProperty("replacedPath") == "0":
                item.SetProperty("replacedPath", "1")
                item.SetPath(str(mediaPath))
                item.SetContentType(mediaType)
            else:
                AddAlternativeStream(item, mediaType, mediaPath, bitrate)
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
        BPLog("svtxml: http download failed, url=%s" % url, Level.ERROR)
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

def SetExpireDate(item, node):
    BPTraceEnter("%s, %s" % (item, node))
    try:
        dateString = GetElementData(node, "svtplay:expiryDate")
        dayString = dateString[0:3]
        day = dateString[5:7]
        monthString = dateString[8:11]
        year = dateString[12:16]

        dayNrMap   = { "Mon" : 0
                     , "Tue" : 1
                     , "Wed" : 2
                     , "Thu" : 3
                     , "Fri" : 4
                     , "Sat" : 5
                     , "Sun" : 6
                     }

        daySEMap   = ["måndag"
                     ,"tisdag"
                     ,"onsdag"
                     ,"torsdag"
                     ,"fredag"
                     ,"lördag"
                     ,"söndag"
                     ]

        monthNrMap = { "Jan" : 1
                     , "Feb" : 2
                     , "Mar" : 3
                     , "Apr" : 4
                     , "May" : 5
                     , "Jun" : 6
                     , "Jul" : 7
                     , "Aug" : 8
                     , "Sep" : 9
                     , "Oct" : 10
                     , "Nov" : 11
                     , "Dec" : 12
                     }

        monthSEMap = ["undefined"
                     ,"januari"
                     ,"februari"
                     ,"mars"
                     ,"april"
                     ,"maj"
                     ,"juni"
                     ,"juli"
                     ,"augusti"
                     ,"september"
                     ,"oktober"
                     ,"november"
                     ,"december"
                     ]

        try:
            hour = dateString[17:19]
            minute = dateString[20:22]
            second = dateString[23:25]
            tstruct = time.struct_time((int(year)
                                      , monthNrMap[monthString]
                                      , int(day)
                                      , int(hour)
                                      , int(minute)
                                      , int(second)
                                      , dayNrMap[dayString]
                                      , 0
                                      , -1
                                      ))
            t = calendar.timegm(tstruct)
            try:
                lt = time.localtime(t)
            except:
                # Fix for strange error on some dates (Windows only?)
                lt = tstruct

            #Fulhack för GUI -.-
            #Format: "Sändes måndag den 2 april, 17:30"
            item.SetProperty("expiretime-se","Slutar %s den %d %s %s, %02d:%02d"
                %(daySEMap[lt.tm_wday], lt.tm_mday, monthSEMap[lt.tm_mon], year, lt.tm_hour, lt.tm_min))
        except Exception, e:
            e = e
    except Exception, e:
        e = e
    BPTraceExit()

def FixLiveAirTime(episodes):
    for episode in episodes:
        try:
            expiretime = episode.GetProperty("expiretime-se")
            episode.SetProperty("airtime-se", expiretime)
            SetGuiInfo(episode)
        except Exception, e:
            BPLog("svtxml: Failed to set live airtime date. Exception: %s" % e, Level.ERROR)

def SetDate(item, node):
    BPTraceEnter("%s, %s" % (item, node))
    try:
        dateString = GetElementData(node, "svtplay:broadcastDate")
        if len(str(dateString)) == 0:
            dateString = GetElementData(node, "pubDate")
        dayString = dateString[0:3]
        day = dateString[5:7]
        monthString = dateString[8:11]
        year = dateString[12:16]

        dayNrMap   = { "Mon" : 0
                     , "Tue" : 1
                     , "Wed" : 2
                     , "Thu" : 3
                     , "Fri" : 4
                     , "Sat" : 5
                     , "Sun" : 6
                     }

        daySEMap   = ["måndag"
                     ,"tisdag"
                     ,"onsdag"
                     ,"torsdag"
                     ,"fredag"
                     ,"lördag"
                     ,"söndag"
                     ]

        monthNrMap = { "Jan" : 1
                     , "Feb" : 2
                     , "Mar" : 3
                     , "Apr" : 4
                     , "May" : 5
                     , "Jun" : 6
                     , "Jul" : 7
                     , "Aug" : 8
                     , "Sep" : 9
                     , "Oct" : 10
                     , "Nov" : 11
                     , "Dec" : 12
                     }

        monthSEMap = ["undefined"
                     ,"januari"
                     ,"februari"
                     ,"mars"
                     ,"april"
                     ,"maj"
                     ,"juni"
                     ,"juli"
                     ,"augusti"
                     ,"september"
                     ,"oktober"
                     ,"november"
                     ,"december"
                     ]

        item.SetDate(int(year), monthNrMap[monthString], int(day))
        
        try:
            hour = dateString[17:19]
            minute = dateString[20:22]
            second = dateString[23:25]
            tstruct = time.struct_time((int(year)
                                      , monthNrMap[monthString]
                                      , int(day)
                                      , int(hour)
                                      , int(minute)
                                      , int(second)
                                      , dayNrMap[dayString]
                                      , 0
                                      , -1
                                      ))
            t = calendar.timegm(tstruct)
            try:
                lt = time.localtime(t)
            except:
                # Fix for strange error on some dates (Windows only?)
                lt = tstruct

            #Fulhack för GUI -.-
            #Format: "Sändes måndag den 2 april, 17:30"
            item.SetProperty("airtime-se", "Sändes %s den %d %s %s, %02d:%02d" %(daySEMap[lt.tm_wday], lt.tm_mday, monthSEMap[lt.tm_mon], year, lt.tm_hour, lt.tm_min))
        except Exception, e:
            BPLog("svtxml: %s" %e)
            BPLog("svtxml: Failed to set GUI air date. Exception: %s" %e, Level.ERROR)
    except Exception, e:
        BPLog("svtxml: Failed to set item date. Exception: %s" %e ,Level.ERROR)
    BPTraceExit()

def SetGuiInfo(item):
    BPTraceEnter()
    try:
        info = ""
        airtime = item.GetProperty("airtime-se")
        mediaType = item.GetProperty("media-type")
        if len(airtime) > 0:
            info += airtime + '\n'
        cat = item.GetGenre()
        chan = item.GetProviderSource()

        if len(cat) > 0:
            info += "Kategori: %s" %cat
            if len(chan) > 0:
                info += ", "
        if len(chan) > 0:
            info += "Kanal: %s" %chan
        if len(mediaType) > 0:
            if len(cat) or len(chan):
                info += ", "
            info += "Typ: %s" %mediaType
        if len(cat) or len(chan) or len(mediaType):
            info += '\n'
        dur = item.GetProperty("duration")
        if len(dur) > 0:
            info += "Längd: %s minuter" %(int(dur)//60)
        item.SetStudio(info)
    except Exception, e:
        BPLog("svtxml: Could not set GUI info, Exception: %s" %e, Level.ERROR)
    BPTraceExit()
