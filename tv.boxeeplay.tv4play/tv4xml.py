#encoding:utf-8
#author:Mats Boisen
#project:boxeeplay
#repository:https://bitbucket.org/hesapesa/boxeeplay
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/license/GPL/2.0/)

from urllib import quote_plus
import urllib2, re
import simplejson as json
import mc
import datetime
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

API_URL = "http://api.tv4play.se"
LIVE_URL = "/video/mobile/programs/search.json?livepublished=true&premium=false&sorttype=date&order=asc"
SEARCHPROG_URL = "/video/mobile/program_formats/list.json?sorttype=date&premium_filter=none&rows=50&name="
SEARCHEPIS_URL = "/video/mobile/programs/search.json?sorttype=date&rows=25&video_types=programs&start=0&premium=false&text="
SEARCHCLIP_URL = "/video/mobile/programs/search.json?sorttype=date&rows=25&video_types=clipss&start=0&premium=false&text="
imageResizeRe = re.compile("resize=[0-9]+x[0-9]+")
imageBeforeSource = re.compile("\A.+img\.tv4\.se.+source=")
# EXAMPLE http://img.tv4.se/?resize=260x146&source=http://cdn01.tv4.se/polopoly_fs/1.1820955.1329917569!originalformatimage/2357196325.jpg

def RetrieveStream(url):
    BPTraceEnter(url)
    try:
        request = urllib2.Request(API_URL + url)
        response = urllib2.urlopen(request)
        data = response.read()
        response.close()
        BPTraceExit("Returning %s" % data)
        return data
    except Exception, e:
        BPLog("tv4xml: http download failed, url=%s | Exception: %s" % (url,e), Level.ERROR)
        return str("")

def GetCategories():
    items = mc.ListItems()
    data = RetrieveStream("/video/tv4play/mobile/categories/list.json")
    for topCategoryElement in json.loads(data):
        if topCategoryElement.get(u"listable", False):
            name = topCategoryElement[u"name"].encode("utf-8")
            id   = topCategoryElement[u"id"].encode("utf-8")
            item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
            item.SetContentType("text/html")
            item.SetLabel(name)
            item.SetPath("http://www.tv4play.se")
            item.SetAuthor("TV4")
            item.SetProperty("id", id)
            item.SetReportToServer(False)
            item.SetAddToHistory(False)
            items.append(item)
    return items


def GetTitles(categoryId):
    items = mc.ListItems()
    data = RetrieveStream("/video/mobile/program_formats/list.json?categoryid=" + categoryId + "&sorttype=alpha&premium_filter=none")
    for topCategoryElement in json.loads(data):
        items.append(GetTitle(topCategoryElement))
    return items
    
def GetTitle(topCategoryElement):
    name = topCategoryElement[u"name"].encode("utf-8")
    item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
    item.SetContentType("text/html")
    image = topCategoryElement[u"image"].encode("utf-8")
    # image = imageBeforeSource.sub("", image) # img.tv4.se serving too slow
    image = imageResizeRe.sub("resize=100x56", image)
    
    item.SetThumbnail(image)
    item.SetIcon(image)
    item.SetDescription(topCategoryElement[u"text"].encode("utf-8"))
    item.SetTitle(name)
    item.SetLabel(name)
    titleId = str(topCategoryElement[u"id"]).encode("utf-8")
    item.SetProperty("id", titleId)
    path = topCategoryElement[u"siteurl"]
    item.SetPath((titleId, path.encode("utf-8"))[path != None or path != ""])
    item.SetTVShowTitle(name)
    item.SetReportToServer(False)
    item.SetAddToHistory(False)
    item.SetAuthor("TV4")
    # item.SetProperty("premium", str(topCategoryElement[u"premium"]).encode("utf-8"))
    # item.SetProperty("airtime-se", topCategoryElement[u"airtime"].encode("utf-8"))
    # item.SetGenre(topCategoryElement[u"category"].encode("utf-8"))
    return item

def GetEpisodes(titleId, loadSamples = False):
    items = mc.ListItems()
    searchUrl = "/video/mobile/programs/search.json?sorttype=date&categoryids=" + titleId + "&rows=1000&premium=false&video_types="
    if loadSamples:
        searchUrl += "clips"
    else:
        searchUrl += "programs"
    data = RetrieveStream(searchUrl)
    data = json.loads(data)[u"results"]
    BPLog(str(data))
    for elem in data:
        if not elem[u"requires_authorization"]:
            item = GetEpisode(elem)
            items.append(item)
    return items
 
def GetEpisode(elem):
    item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
    item.SetContentType("text/html")
    image = ("", elem[u"largeimage"].encode("utf-8"))[elem[u"largeimage"] != None]
    item.SetThumbnail(image)
    item.SetIcon(image)
    desc = elem[u"lead"]
    if desc is None:
        item.SetDescription("")
    else:
        item.SetDescription(desc.encode("utf-8"))
    item.SetTitle(elem[u"name"].encode("utf-8"))
    item.SetLabel(elem[u"name"].encode("utf-8"))
    videoId = str(elem[u"vmanprogid"]).encode("utf-8")
    item.SetProperty("id", videoId)
    item.SetPath(CreateFlashUrl(videoId))
    item.SetProperty("ontime", ("", str(elem[u"ontime"]).encode("utf-8"))[elem[u"ontime"] != None])
    item.SetProperty("offtime", ("", str(elem[u"offdate"]).encode("utf-8"))[elem[u"offdate"] != None])
    item.SetProperty("live", str(elem[u"livepublished"]))
    item.SetTVShowTitle(elem[u"category"].encode("utf-8"))
    item.SetGenre(elem[u"category"].encode("utf-8"))
    # item.SetProperty("premium", premium)
    item.SetReportToServer(True)
    item.SetAddToHistory(True)
    item.SetAuthor("TV4")
    if elem[u"livepublished"]:
        item.SetProperty("media-type", "Direkt")
    else:
        if elem[u"full_program"]:
            item.SetProperty("media-type", "Fullängd")
        else:
            item.SetProperty("media-type", "Klipp")
    SetGuiInfo(item)
    return item

def CreateFlashUrl(videoId):
    #path = quote_plus("http://www.tv4play.se/flash%2ftv4play30Default_sa.swf?vid=" + videoId)
    #jsActions = quote_plus("http://boxeeplay.tv/tv4play/tv4play.js")
    #url = "flash://boxeeplay.tv/src=" + path + "&bx-jsactions=" + jsActions
    url = "http://www.tv4play.se/flash%2ftv4play30Default_sa.swf?vid=" + videoId
    return url
    
def SearchPrograms(searchTerm):
    items = mc.ListItems()

    searchTerm = quote_plus(searchTerm)
    searchUrl = SEARCHPROG_URL + searchTerm
    
    data = RetrieveStream(searchUrl)
    data = json.loads(data)
    BPLog(str(data))
    for elem in data:
        item = GetTitle(elem)
        items.append(item)
    return items

def SearchEpisodes(searchTerm, loadSamples = False):
    items = mc.ListItems()

    if loadSamples:
        searchUrl = SEARCHCLIP_URL
    else:
        searchUrl = SEARCHEPIS_URL
    searchTerm = quote_plus(searchTerm)
    
    # Manually fix åäö - not an optimal fix
    # searchTerm = searchTerm.replace("%E5", "%C3%A5") #å
    # searchTerm = searchTerm.replace("%E4", "%C3%A4") #ä
    # searchTerm = searchTerm.replace("%F6", "%C3%B6") #ö
    # searchTerm = searchTerm.replace("%C5", "%C3%85") #Å
    # searchTerm = searchTerm.replace("%C4", "%C3%84") #Ä
    # searchTerm = searchTerm.replace("%D6", "%C3%96") #Ö

    searchUrl = searchUrl + searchTerm
    data = RetrieveStream(searchUrl)
    data = json.loads(data)[u"results"]
    BPLog(str(data))
    for elem in data:
        if not elem[u"requires_authorization"]:
            item = GetEpisode(elem)
            items.append(item)
    return items


def SetGuiInfo(item):
    BPTraceEnter()
    try:
        info = ""
        ontime    = item.GetProperty("ontime")
        offtime   = item.GetProperty("offtime")
        mediaType = item.GetProperty("media-type")
        cat       = item.GetGenre()
        chan      = item.GetProviderSource()
        
        if len(ontime) == 12:
            aired = GetTimeObject(ontime)
            info += "Sändes " + GetTimeRepr(aired) + "\n"
        if len(offtime) == 12:
            stopped = GetTimeObject(offtime)
            info += "Slutar " + GetTimeRepr(stopped) + "\n"
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
        item.SetProperty("info", info)
        item.SetProperty("bitrate", "unknown")
    except Exception, e:
        BPLog("tv4xml: Could not set GUI info, Exception: %s" %e, Level.ERROR)
    BPTraceExit()
    
def GetTimeRepr(obj):
    daySEMap   = ["måndag"
                 ,"tisdag"
                 ,"onsdag"
                 ,"torsdag"
                 ,"fredag"
                 ,"lördag"
                 ,"söndag"
                 ]
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
                     
    return "%s den %02d %s %d, %02d:%02d" % \
        (daySEMap[obj.weekday()], obj.day, monthSEMap[obj.month], obj.year, obj.hour, obj.minute)
    
def GetTimeObject(str):
    addDay = False
    year   = int(str[0:4])
    month  = int(str[4:6])
    day    = int(str[6:8])
    hour   = int(str[8:10])
    minute = int(str[10:12])
    if hour == 24:
        hour = 0
        addDay = True
    obj = datetime.datetime(year,month,day,hour,minute)
    if addDay:
        obj = obj + datetime.timedelta(1) # Add 1 day
    return obj
    
def GetMostViewedPrograms():
    items = mc.ListItems()
    data = RetrieveStream("/video/mobile/programs/most_viewed.json?video_types=programs&premium=false")
    data = json.loads(data)[u"results"]
    BPLog(str(data))
    for elem in data:
        if not elem[u"requires_authorization"]:
            item = GetEpisode(elem)
            items.append(item)
    return items

def GetMostViewedClips():
    items = mc.ListItems()
    data = RetrieveStream("/video/mobile/programs/most_viewed.json?video_types=clips&premium=false")
    data = json.loads(data)[u"results"]
    BPLog(str(data))
    for elem in data:
        if not elem[u"requires_authorization"]:
            item = GetEpisode(elem)
            items.append(item)
    return items

def GetLiveEpisodes():
    items = mc.ListItems()
    data = RetrieveStream(LIVE_URL)
    data = json.loads(data)[u"results"]
    BPLog(str(data))
    for elem in data:
        if not elem[u"requires_authorization"]:
            item = GetEpisode(elem)
            items.append(item)
    return items

#  -- This block of code is not currently used
# -- but might be used if we decide to process the video streams our selves
#def CreateRtmpPath(domain, url):
#    BPTraceEnter("%s, %s" % (domain, url))
#    url = 'http://boxeeplay.tv/flowplayer/index.html?net=' + str(domain) + '&id=' + str(url)
#    mc.LogInfo("tv4xml: url:" + url)
#    url = quote_plus(url)
#    jsActions = quote_plus('http://boxeeplay.tv/flowplayer/control.js')
#    path = 'flash://boxeeplay.tv/src=' + str(url) + '&bx-jsactions=' + str(jsActions)
#    BPLog("tv4xml: Media path converted to: %s" % path, Level.DEBUG)
#    BPTraceExit("Returning %s" % path)
#    return path
#
#def GetVideoPath(videoId):
#    BPTraceEnter(videoId)
#
#    base = str("")
#    source = str("")
#    bestBitRate = 0
#
#    root = RetrieveXmlStream("http://anytime.tv4.se/webtv/metafileFlash.smil?p=" + str(videoId) + "&bw=1000&emulate=true&sl=true")
#
#    headElement = root.getElementsByTagName("head")[0]
#    for metaElement in headElement.getElementsByTagName("meta"):
#        baseAttribute = metaElement.getAttribute("base").encode("utf-8")
#        if len(str(baseAttribute)) > 0:
#            base = baseAttribute
#            mc.LogInfo("tv4xml: base: " + base)
#
#    bodyElement = root.getElementsByTagName("body")[0]
#    switchElement = bodyElement.getElementsByTagName("switch")[0]
#    for videoElement in switchElement.getElementsByTagName("video"):
#        src = videoElement.getAttribute("src").encode("utf-8")
#        systemBitRate = videoElement.getAttribute("system-bitrate").encode("utf-8")
#        bitRate = int(systemBitRate)
#        if bitRate > bestBitRate:
#            bestBitRate = bitRate
#            mc.LogInfo("tv4xml: bitrate: " + str(bitRate))
#            source = src
#            mc.LogInfo("tv4xml: source: " + source)
#    path = CreateRtmpPath(base, source)
#    mc.LogInfo("tv4xml: path: " + path)
#    BPTraceExit("Returning %s" % path)
#    return path
#
#def GetPremiumVideoPath(videoId):
#    BPTraceEnter(videoId)
#    path2500 = str("")
#    path1500 = str("")
#    path800 = str("")
#    path300 = str("")
#    root = RetrieveXmlStream("http://premium.tv4play.se/api/web/asset/" + str(videoId) + "/play")
#    for itemsElement in root.getElementsByTagName("items"):
#        for itemElement in itemsElement.getElementsByTagName("item"):
#            bitrate = GetElementData(itemElement, "bitrate")
#            mc.LogInfo("tv4xml: bitrate: " + bitrate)
#            mediaFormat = GetElementData(itemElement, "mediaFormat")
#            mc.LogInfo("tv4xml: mediaFormat: " + mediaFormat)
#            scheme = GetElementData(itemElement, "scheme")
#            mc.LogInfo("tv4xml: scheme: " + scheme)
#            domain = GetElementData(itemElement, "base")
#            mc.LogInfo("tv4xml: domain: " + domain)
#            url = GetElementData(itemElement, "url")
#            mc.LogInfo("tv4xml: url: " + url)
#            if mediaFormat == "mp4":
#                if scheme == "rtmp" or scheme == "rtmpe":
#                    if bitrate == "2500":
#                        path2500 = CreateRtmpPath(domain, url)
#                        mc.LogInfo("tv4xml: path: " + path2500)
#                    if bitrate == "1500":
#                        path1500 = CreateRtmpPath(domain, url)
#                        mc.LogInfo("tv4xml: path: " + path1500)
#                    if bitrate == "800":
#                        path800 = CreateRtmpPath(domain, url)
#                        mc.LogInfo("tv4xml: path: " + path800)
#                    if bitrate == "300":
#                        path300 = CreateRtmpPath(domain, url)
#                        mc.LogInfo("tv4xml: path: " + path300)
#    path = path300
#    if len(path800) > 0:
#        path = path800
#    if len(path1500) > 0:
#        path = path1500
#    if len(path2500) > 0:
#        path = path2500
#    mc.LogInfo("tv4xml: path: " + path)
#    BPTraceExit("Returning %s" % path)
#    return path
