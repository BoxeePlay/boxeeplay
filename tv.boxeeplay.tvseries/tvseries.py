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

def GetChannels() :
    BPTraceEnter()
    items = mc.ListItems()

    item1 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item1.SetContentType("text/html")
    item1.SetLabel("SVT")
    item1.SetPath("http://svtplay.se")
    item1.SetThumbnail("http://dir.boxee.tv/apps/providerthmb/se_svtplay.png")
    item1.SetProperty("id", "se_svtplay")
    items.append(item1)

    item2 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item2.SetContentType("text/html")
    item2.SetLabel("TV3")
    item2.SetPath("http://www.tv3.se")
    item2.SetThumbnail("http://dir.boxee.tv/apps/providerthmb/se_tv3play.png")
    item2.SetProperty("id", "se_tv3play")
    items.append(item2)

    item3 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item3.SetContentType("text/html")
    item3.SetLabel("TV4")
    item3.SetPath("http://www.tv4play.se")
    item3.SetThumbnail("http://dir.boxee.tv/apps/providerthmb/se_tv4play.png")
    item3.SetProperty("id", "se_tv4play")
    items.append(item3)

    item4 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item4.SetContentType("text/html")
    item4.SetLabel("Kanal 5")
    item4.SetPath("http://www.kanal5.se")
    item4.SetThumbnail("http://dir.boxee.tv/apps/providerthmb/se_kanal5.png")
    item4.SetProperty("id", "se_kanal5")
    items.append(item4)

    item5 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item5.SetContentType("text/html")
    item5.SetLabel("TV6")
    item5.SetPath("http://www.tv6.se")
    item5.SetThumbnail("http://dir.boxee.tv/apps/providerthmb/se_tv6play.png")
    item5.SetProperty("id", "se_tv6play")
    items.append(item5)

    item6 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item6.SetContentType("text/html")
    item6.SetLabel("TV8")
    item6.SetPath("http://www.tv8.se")
    item6.SetThumbnail("http://dir.boxee.tv/apps/providerthmb/se_tv8play.png")
    item6.SetProperty("id", "se_tv8play")
    items.append(item6)
    
    BPTraceExit("Returning %s" % items)
    return items

def GetChannelId(item) :
    return item.GetProperty("id")

