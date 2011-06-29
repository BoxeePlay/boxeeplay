#encoding:utf-8
#author:Mats Boisen
#project:boxeeplay
#repository:https://bitbucket.org/hesapesa/boxeeplay
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/license/GPL/2.0/)

from urllib import quote_plus
import urllib2
import xml.dom.minidom
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
    try:
        return node.getElementsByTagName(name)[0].childNodes[0].data.encode("utf-8")
    except:
        return str("")

def GetElementAttribute(node, name, attribute):
    try:
        return node.getElementsByTagName(name)[0].getAttribute(attribute).encode("utf-8")
    except:
        return str("")

# Holding the xml.tv4play minidom structure
xmlTv4Play = None

def LoadXmlTv4Play():
    global xmlTv4Play
    xmlTv4Play = RetrieveXmlStream("http://xml.tv4play.se")
    return

def GetXmlTv4Play():
    global xmlTv4Play
    if xmlTv4Play == None:
        LoadXmlTv4Play()
    return xmlTv4Play

def GetCategories():
    items = mc.ListItems()
    LoadXmlTv4Play()
    root = GetXmlTv4Play()
    for topCategoryElement in root.getElementsByTagName("category"):
        name = topCategoryElement.getAttribute("name").encode("utf-8")
        if name == "tv4playnew.se":
            for categoryElement in topCategoryElement.getElementsByTagName("category"):
                if categoryElement.getAttribute("listable").encode("utf-8") == "true" :
                    name = categoryElement.getAttribute("name").encode("utf-8")
                    id = categoryElement.getAttribute("id").encode("utf-8")
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


def CreateTitleItemFromFormatElement(categoryName, items, programFormatElement):
    if programFormatElement.getAttribute("listable").encode("utf-8") == "true" and GetElementData(programFormatElement,
                                                                                                  "premium") != "true":
        item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
        item.SetContentType("text/xml")
        name = programFormatElement.getAttribute("name").encode("utf-8")
        item.SetLabel(name)
        item.SetTitle(name)
        item.SetTVShowTitle(name)
        titleId = programFormatElement.getAttribute("id").encode("utf-8")
        item.SetProperty("id", titleId)
        item.SetDescription(GetElementData(programFormatElement, "text"))
        item.SetProviderSource(GetElementData(programFormatElement, "channel"))
        item.SetProperty("premium", GetElementData(programFormatElement, "premium"))
        item.SetProperty("airtime-se", GetElementData(programFormatElement, "airtime"))
        imageUrl = ""
        for largeImageElement in programFormatElement.getElementsByTagName("largeimage"):
            imageUrl = largeImageElement.childNodes[0].data.encode("utf-8")
        if len(imageUrl) == 0:
            for imageElement in programFormatElement.getElementsByTagName("image"):
                imageUrl = imageElement.childNodes[0].data.encode("utf-8")
        if len(imageUrl) > 0:
            item.SetThumbnail(imageUrl)
        smallImageUrl = ""
        for smallImageElement in programFormatElement.getElementsByTagName("smallformatimage"):
            smallImageUrl = smallImageElement.childNodes[0].data.encode("utf-8")
        if len(smallImageUrl) > 0:
            item.SetIcon(smallImageUrl)
        item.SetGenre(categoryName)
        item.SetReportToServer(False)
        item.SetAddToHistory(False)
        url = "http://www.tv4play.se/search/search?rows=200&order=desc&categoryids=" + titleId + "&sorttype=date&start=0&video_types="
        item.SetPath(url)
        item.SetAuthor("TV4")
        items.append(item)
        item.Dump()


def GetTitles(categoryId):
    items = mc.ListItems()
    root = GetXmlTv4Play()
    for topCategoryElement in root.getElementsByTagName("category"):
        name = topCategoryElement.getAttribute("name").encode("utf-8")
        if name == "tv4playnew.se":
            for categoryElement in topCategoryElement.getElementsByTagName("category"):
                categoryName = categoryElement.getAttribute("name").encode("utf-8")
                id = categoryElement.getAttribute("id").encode("utf-8")
                if id == categoryId:
                    for programFormatElement in sorted(categoryElement.getElementsByTagName("programformat"), key=lambda x: x.getAttribute("name").encode("utf-8")):
                        CreateTitleItemFromFormatElement(categoryName, items, programFormatElement)
                    return items
    return items

def GetEpisodes(titleId, loadSamples = False):
    #TODO Is it possible to load episodes through xml.tv4play.se?
    #as in http://xml.tv4play.se/1.1215984?selection=1.1062581
    items = mc.ListItems()

    showTitle = ""
    channel = ""
    premium = "false"
    categoryName = ""
    root = GetXmlTv4Play()
    titleFound = False
    for topCategoryElement in root.getElementsByTagName("category"):
        name = topCategoryElement.getAttribute("name").encode("utf-8")
        if name == "tv4playnew.se":
            for categoryElement in topCategoryElement.getElementsByTagName("category"):
                categoryName = categoryElement.getAttribute("name").encode("utf-8")
                for programFormatElement in categoryElement.getElementsByTagName("programformat"):
                    if programFormatElement.getAttribute("id").encode("utf-8") == titleId:
                        showTitle = programFormatElement.getAttribute("name").encode("utf-8")
                        channel = GetElementData(programFormatElement, "channel")
                        premium = GetElementData(programFormatElement, "premium")
                        titleFound = True;
                        break
                if titleFound:
                    break

    #TODO How to load all episodes, pokemon is 172?
    #TODO Load season per season, loop module, check showprograms=true and showclips=true
    #TODO Add season title to ShowTitle (if not "Hela program")
    searchUrl = "http://www.tv4play.se/search/search?rows=200&order=desc&categoryids=" + titleId + "&sorttype=date&start=0&video_types="
    if loadSamples:
        searchUrl += "clips"
    else:
        searchUrl += "programs"
    data = RetrieveStream(searchUrl)
    data = "<root>" + data + "</root>"
    root = xml.dom.minidom.parseString(data)
    for liElement in root.getElementsByTagName("li"):
        className = liElement.getAttribute("class").encode("utf-8")
        if className[:11] == "video-panel":
            premiumSkip = False
            item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
            item.SetContentType("text/html")
            for imgElement in liElement.getElementsByTagName("img"):
                item.SetThumbnail(imgElement.getAttribute("src").encode("utf-8"))
            for pElement in liElement.getElementsByTagName("p"):
                className = pElement.getAttribute("class").encode("utf-8")
                if className == "premium":
                    premiumSkip = True
                if className == "date":
                    item.SetProperty("airtime-se", pElement.childNodes[0].data.encode("utf-8"))
                if className == "video-description":
                    try:
                        item.SetDescription(pElement.childNodes[0].data.encode("utf-8"))
                    except:
                        item.SetDescription("")
            for h3Element in liElement.getElementsByTagName("h3"):
                className = h3Element.getAttribute("class").encode("utf-8")
                if className == "video-title":
                    item.SetTitle(GetElementAttribute(h3Element, "a", "title"))
                    item.SetLabel(GetElementAttribute(h3Element, "a", "title"))
                    path = GetElementAttribute(h3Element, "a", "href")
                    videoId = path.split("videoid=")[1]
                    url = CreateFlashUrl(videoId)
                    item.SetPath(url)
                    item.SetProperty("id", videoId)
            if not premiumSkip:
                item.SetTVShowTitle(showTitle)
                item.SetProviderSource(channel)
                item.SetGenre(categoryName)
                item.SetProperty("premium", premium)
                item.SetReportToServer(True)
                item.SetAddToHistory(True)
                if loadSamples == True:
                    item.SetProperty("media-type", "Klipp")
                else:
                    item.SetProperty("media-type", "Fullängd")
                SetGuiInfo(item)
                items.append(item)
    return items

def CreateFlashUrl(videoId):
    #path = quote_plus("http://www.tv4play.se/flash%2ftv4play30Default_sa.swf?vid=" + videoId)
    #jsActions = quote_plus("http://boxeeplay.tv/tv4play/tv4play.js")
    #url = "flash://boxeeplay.tv/src=" + path + "&bx-jsactions=" + jsActions
    url = "http://www.tv4play.se/flash%2ftv4play30Default_sa.swf?vid=" + videoId
    return url

def SearchEpisodes(searchTerm, loadSamples = False):
    items = mc.ListItems()

    searchUrl = "http://www.tv4play.se/search/search?rows=200&order=desc&categoryids=2.76225&sorttype=date&start=0&video_types="
    if loadSamples:
        searchUrl += "clips"
    else:
        searchUrl += "programs"
    searchTerm = quote_plus(searchTerm)
    # Manually fix åäö - not an optimal fix
    searchTerm = searchTerm.replace("%E5", "%C3%A5") #å
    searchTerm = searchTerm.replace("%E4", "%C3%A4") #ä
    searchTerm = searchTerm.replace("%F6", "%C3%B6") #ö
    searchTerm = searchTerm.replace("%C5", "%C3%85") #Å
    searchTerm = searchTerm.replace("%C4", "%C3%84") #Ä
    searchTerm = searchTerm.replace("%D6", "%C3%96") #Ö

    searchUrl = searchUrl + "&text=" + searchTerm
    mc.LogInfo("tv4play - search: " + searchUrl)
    data = RetrieveStream(searchUrl)
    data = "<root>" + data + "</root>"
    root = xml.dom.minidom.parseString(data)
    for liElement in root.getElementsByTagName("li"):
        className = liElement.getAttribute("class").encode("utf-8")
        if className[:11] == "video-panel":
            premiumSkip = False
            item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
            item.SetContentType("text/html")
            for imgElement in liElement.getElementsByTagName("img"):
                item.SetThumbnail(imgElement.getAttribute("src").encode("utf-8"))
            for pElement in liElement.getElementsByTagName("p"):
                className = pElement.getAttribute("class").encode("utf-8")
                if className == "premium":
                    premiumSkip = True
                if className == "date":
                    item.SetProperty("airtime-se", pElement.childNodes[0].data.encode("utf-8"))
                if className == "video-description":
                    try:
                        item.SetDescription(pElement.childNodes[0].data.encode("utf-8"))
                    except:
                        item.SetDescription("")
            for h3Element in liElement.getElementsByTagName("h3"):
                className = h3Element.getAttribute("class").encode("utf-8")
                if className == "video-title":
                    item.SetTitle(GetElementAttribute(h3Element, "a", "title"))
                    item.SetLabel(GetElementAttribute(h3Element, "a", "title"))
                    path = GetElementAttribute(h3Element, "a", "href")
                    videoId = path.split("videoid=")[1]
                    url = CreateFlashUrl(videoId)
                    item.SetPath(url)
                    item.SetProperty("id", videoId)
            if loadSamples == True:
                item.SetProperty("media-type", "Klipp")
            else:
                item.SetProperty("media-type", "Fullängd")
            item.SetReportToServer(True)
            item.SetAddToHistory(True)
            if not premiumSkip:
                SetGuiInfo(item)
                items.append(item)
    return items

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
        item.SetProperty("bitrate", "unknown")
    except Exception, e:
        BPLog("tv4xml: Could not set GUI info, Exception: %s" %e, Level.ERROR)
    BPTraceExit()

def AppendLiveItems(items):
    LoadXmlTv4Play()
    root = GetXmlTv4Play()
    for showParam in root.getElementsByTagName("param"):
        if showParam.getAttribute("name").encode("utf-8") == "item":
            isLive = False
            for subParam in showParam.getElementsByTagName("param"):
                if subParam.getAttribute("premium").encode("utf-8") == "true":
                    continue
                if subParam.getAttribute("name").encode("utf-8") == "imageleadcss":
                    if subParam.childNodes[0].data.encode("utf-8") == "live-now":
                        isLive = True
            if isLive == False:
                continue

            path = str("")
            text = str("")
            title = str("")
            titleId = str("")
            largeImage = str("")
            for subParam in showParam.getElementsByTagName("param"):
                mc.LogInfo("tv4xml - name: " + subParam.getAttribute("name").encode("utf-8"))
                if subParam.getAttribute("name").encode("utf-8") == "href":
                    path = subParam.childNodes[0].data.encode("utf-8")
                if subParam.getAttribute("name").encode("utf-8") == "text":
                    text = subParam.childNodes[0].data.encode("utf-8")
                if subParam.getAttribute("name").encode("utf-8") == "title":
                    title = subParam.childNodes[0].data.encode("utf-8")
                if subParam.getAttribute("name").encode("utf-8") == "id":
                    titleId = subParam.childNodes[0].data.encode("utf-8")
                if subParam.getAttribute("name").encode("utf-8") == "largeimage":
                    largeImage = subParam.childNodes[0].data.encode("utf-8")

            titleFound = False
            for topCategoryElement in root.getElementsByTagName("category"):
                name = topCategoryElement.getAttribute("name").encode("utf-8")
                if name == "tv4playnew.se":
                    for categoryElement in topCategoryElement.getElementsByTagName("category"):
                        categoryName = categoryElement.getAttribute("name").encode("utf-8")
                        for programFormatElement in categoryElement.getElementsByTagName("programformat"):
                            if programFormatElement.getAttribute("id").encode("utf-8") == titleId:
                                showTitle = programFormatElement.getAttribute("name").encode("utf-8")
                                channel = GetElementData(programFormatElement, "channel")
                                premium = GetElementData(programFormatElement, "premium")

                                if len(largeImage) == 0:
                                    for largeImageElement in programFormatElement.getElementsByTagName("largeimage"):
                                        largeImage = largeImageElement.childNodes[0].data.encode("utf-8")
                                    if len(largeImage) == 0:
                                        for imageElement in programFormatElement.getElementsByTagName("image"):
                                            largeImage = imageElement.childNodes[0].data.encode("utf-8")

                                titleFound = True
                                break

                        if titleFound:
                            break

            item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
            item.SetContentType("text/html")
            if len(largeImage) > 0:
                item.SetThumbnail(largeImage)

            item.SetDescription(text)
            item.SetTitle(title)
            item.SetLabel(title)

            mc.LogInfo("tv4xml - 90 - path: " + path)
            videoId = path.split("videoid=")[1]
            mc.LogInfo("tv4xml - 91")
            url = CreateFlashUrl(videoId)
            item.SetPath(url)
            item.SetProperty("id", videoId)
            item.SetTVShowTitle(showTitle)
            item.SetProviderSource(channel)
            item.SetGenre(categoryName)
            item.SetProperty("premium", "False")
            item.SetReportToServer(True)
            item.SetAddToHistory(True)
            item.SetProperty("media-type", "Direkt")
            SetGuiInfo(item)
            items.append(item)
            mc.LogInfo("tv4xml - 99")

def GetRecommendedTitles():
    items = mc.ListItems()

    idList = []
    root = GetXmlTv4Play()
    for modulesElement in root.getElementsByTagName("modules"):
        if modulesElement.parentNode.nodeName == "category":
            for moduleElement in modulesElement.getElementsByTagName("module"):
                if moduleElement.getAttribute("type").encode("utf-8") == "bigcarousel":
                    for paramElement in moduleElement.getElementsByTagName("param"):
                        if paramElement.getAttribute("name").encode("utf-8") == "id":
                            idList.append(paramElement.childNodes[0].data.encode("utf-8"))

    for id in idList:
        for topCategoryElement in root.getElementsByTagName("category"):
            name = topCategoryElement.getAttribute("name").encode("utf-8")
            if name == "tv4playnew.se":
                for categoryElement in topCategoryElement.getElementsByTagName("category"):
                    categoryName = categoryElement.getAttribute("name").encode("utf-8")
                    for programFormatElement in categoryElement.getElementsByTagName("programformat"):
                        titleId = programFormatElement.getAttribute("id").encode("utf-8")
                        if id == titleId:
                            CreateTitleItemFromFormatElement(categoryName, items, programFormatElement)

    return items

def GetLiveEpisodes():
    items = mc.ListItems()

    AppendLiveItems(items)

    items.append(GetNyheternaSeItem())
                
    return items

def GetNyheternaSeItem():
    item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_EPISODE)
    item.SetContentType("text/html")
    item.SetThumbnail("http://www.boxeeplay.tv/images/nyheterna_live.png")

    item.SetDescription("Senaste nytt från Nyheterna.se")
    item.SetTitle("Nyheterna.se")
    item.SetLabel("Nyheterna.se")

    videoId = "774267"
    url = CreateFlashUrl(videoId)
    item.SetPath(url)
    item.SetProperty("id", videoId)
    item.SetTVShowTitle("Nyheterna.se")
    item.SetProviderSource("TV4")
    item.SetGenre("Nyheter")
    item.SetProperty("premium", "False")
    item.SetReportToServer(True)
    item.SetAddToHistory(True)
    item.SetProperty("media-type", "Direkt")

    SetGuiInfo(item)
    return item

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
