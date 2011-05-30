#encoding:utf-8
#author:Mats Boisen
#project:boxeeplay
#repository:https://bitbucket.org/hesapesa/boxeeplay
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/license/GPL/2.0/)

#TODO Sort the episodes
#TODO Control scripts
#TODO remove series not from sweden
#TODO icons

from urllib import quote_plus
import urllib2
import xml.dom.minidom
import mc
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

def GetChannels() :
    BPTraceEnter()
    items = mc.ListItems()

    item0 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item0.SetContentType("text/html")
    item0.SetLabel("Senaste")
    item0.SetPath("http://www.boxeeplay.tv")
    item0.SetThumbnail("http://boxeeplay.tv/wp-content/uploads/2011/04/boxeeplay.png")
    item0.SetProperty("provider", "")
    item0.SetProperty("sortBy", "release")
    item0.SetProperty("count", "100")
    items.append(item0)

    item1 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item1.SetContentType("text/html")
    item1.SetLabel("SVT")
    item1.SetPath("http://svtplay.se")
    item1.SetThumbnail("http://s3.boxee.tv/provider/1.1.0.18734/se_svtplay.png")
    item1.SetProperty("provider", "se_svtplay")
    item1.SetProperty("sortBy", "title")
    item1.SetProperty("count", "1000")
    items.append(item1)

    item2 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item2.SetContentType("text/html")
    item2.SetLabel("TV3")
    item2.SetPath("http://www.tv3.se")
    item2.SetThumbnail("http://s3.boxee.tv/provider/1.1.0.18734/se_tv3play.png")
    item2.SetProperty("provider", "se_tv3play")
    item2.SetProperty("sortBy", "title")
    item2.SetProperty("count", "1000")
    items.append(item2)

    item3 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item3.SetContentType("text/html")
    item3.SetLabel("TV4")
    item3.SetPath("http://www.tv4play.se")
    item3.SetThumbnail("http://s3.boxee.tv/provider/1.1.0.18734/se_tv4play.png")
    item3.SetProperty("provider", "se_tv4play")
    item3.SetProperty("sortBy", "title")
    item3.SetProperty("count", "1000")
    items.append(item3)

    item4 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item4.SetContentType("text/html")
    item4.SetLabel("Kanal 5")
    item4.SetPath("http://www.kanal5.se")
    item4.SetThumbnail("http://s3.boxee.tv/provider/1.1.0.18734/se_kanal5.png")
    item4.SetProperty("provider", "se_kanal5")
    item4.SetProperty("sortBy", "title")
    item4.SetProperty("count", "1000")
    items.append(item4)

    item5 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item5.SetContentType("text/html")
    item5.SetLabel("TV6")
    item5.SetPath("http://www.tv6.se")
    item5.SetThumbnail("http://s3.boxee.tv/provider/1.1.0.18734/se_tv6play.png")
    item5.SetProperty("provider", "se_tv6play")
    item5.SetProperty("sortBy", "title")
    item5.SetProperty("count", "1000")
    items.append(item5)

    item6 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item6.SetContentType("text/html")
    item6.SetLabel("TV8")
    item6.SetPath("http://www.tv8.se")
    item6.SetThumbnail("http://s3.boxee.tv/provider/1.1.0.18734/se_tv8play.png")
    item6.SetProperty("provider", "se_tv8play")
    item6.SetProperty("sortBy", "title")
    item6.SetProperty("count", "1000")
    items.append(item6)
    
    BPTraceExit("Returning %s" % items)
    return items

def GetSeriesUrlForChannel(item) :
    return "http://res.boxee.tv/titles/tv?adult=yes&count=" + item.GetProperty("count") + "&geo=se&provider=" + item.GetProperty("provider") + "&sort=" + item.GetProperty("sortBy") + "&start=0"

def GetSeries(url):
    return mc.GetDirectory(url)

def GetEpisodesUrlForSerie(item) :
    return item.GetPath().replace("rss:", "http:") + "?adult=no&geo=se"

def GetEpisodes(url):
    items = mc.GetDirectory(url)
    for item in items:
        item.Dump()
    return items

def SearchSeries(searchTerm) :
    searchTerm = quote_plus(searchTerm)

    # Manually fix åäö - not an optimal fix
    searchTerm = searchTerm.replace("%E5", "%C3%A5") #å
    searchTerm = searchTerm.replace("%E4", "%C3%A4") #ä
    searchTerm = searchTerm.replace("%F6", "%C3%B6") #ö
    searchTerm = searchTerm.replace("%C5", "%C3%85") #Å
    searchTerm = searchTerm.replace("%C4", "%C3%84") #Ä
    searchTerm = searchTerm.replace("%D6", "%C3%96") #Ö

    return mc.GetDirectory("http://res.boxee.tv/titles/search/tv?adult=no&geo=se&term=" + searchTerm)
