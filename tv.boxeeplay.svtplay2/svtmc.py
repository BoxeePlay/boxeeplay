#encoding:utf-8
#author:Mats Boisen
#project:boxeeplay
#repository:https://bitbucket.org/hesapesa/boxeeplay
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/license/GPL/2.0/)

import mc
from urllib import quote_plus
import svtxml
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

def GetCategories() :
    BPTraceEnter()
    items = mc.ListItems()

    item1 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item1.SetContentType("text/html")
    item1.SetLabel("Barn")
    item1.SetPath("http://svtplay.se/c/96251/barn")
    item1.SetAuthor("SVT")
    item1.SetThumbnail("http://material.svtplay.se/content/1/c8/01/36/41/35/barn141.jpg")
    item1.SetProperty("id", "96240")
    items.append(item1)

    item2 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item2.SetContentType("text/html")
    item2.SetLabel("Film och drama")
    item2.SetPath("http://svtplay.se/c/96257/film_och_drama")
    item2.SetAuthor("SVT")
    item2.SetThumbnail("http://material.svtplay.se/content/1/c8/01/36/41/36/film141.jpg")
    item2.SetProperty("id", "96242,96247")
    items.append(item2)

    item3 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item3.SetContentType("text/html")
    item3.SetLabel("Kultur och nöje")
    item3.SetPath("http://svtplay.se/c/96256/kultur_och_noje")
    item3.SetAuthor("SVT")
    item3.SetThumbnail("http://material.svtplay.se/content/1/c8/01/36/41/37/kultur141.jpg")
    item3.SetProperty("id", "96243,96245")
    items.append(item3)

    item4 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item4.SetContentType("text/html")
    item4.SetLabel("Samhälle och fakta")

    item4.SetPath("http://svtplay.se/c/96254/samhalle_och_fakta")
    item4.SetAuthor("SVT")
    item4.SetThumbnail("http://material.svtplay.se/content/1/c8/01/36/41/39/fakta141.jpg")
    item4.SetProperty("id", "96246,96241")
    items.append(item4)

    item5 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item5.SetContentType("text/html")
    item5.SetLabel("Nyheter")
    item5.SetPath("http://svtplay.se/c/96255/nyheter")
    item5.SetAuthor("SVT")
    item5.SetThumbnail("http://material.svtplay.se/content/1/c8/01/36/41/38/nyheter141.jpg")
    item5.SetProperty("id", "96244")
    items.append(item5)

    item6 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item6.SetContentType("text/html")
    item6.SetLabel("Sport")
    item6.SetPath("http://svtplay.se/c/96253/sport")
    item6.SetAuthor("SVT")
    item6.SetThumbnail("http://material.svtplay.se/content/1/c8/01/36/41/40/sport141.jpg")
    item6.SetProperty("id", "96248")
    items.append(item6)

    item7 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item7.SetContentType("text/html")
    item7.SetLabel("Öppet arkiv")
    item7.SetPath("http://svtplay.se/c/96252/oppet_arkiv")
    item7.SetAuthor("SVT")
    item7.SetThumbnail("http://material.svtplay.se/content/1/c8/01/36/41/41/oppetarkiv141.jpg")
    item7.SetProperty("id", "98382")
    items.append(item7)

    BPTraceExit("Returning %s" % items)
    return items

def GetCategoryId(item) :
    return item.GetProperty("id")

def GetTitles(id) :
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/title/list/" + str(id) + "?num=100", 999)

def GetTitleId(item) :
    return item.GetProperty("id")

def GetEpisodes(id=96238, maxItems=100) :
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/video/list/" + str(id) + "?expression=full&num=100", maxItems)

def GetSamples(id=96238, maxItems=100) :
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/video/list/" + str(id) + "?expression=sample&num=100", maxItems)

def SearchEpisodes(searchTerm, id="96238", maxItems=100) :
    if (len(searchTerm) == 0):
        return mc.ListItems()
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/video/search/" + str(id) + "?expression=full&num=100&q=" + quote_plus(searchTerm), maxItems)

def SearchSamples(searchTerm, id="96238", maxItems=100) :
    if (len(searchTerm) == 0):
        return mc.ListItems()
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/video/search/" + str(id) + "?expression=sample&num=100&q=" + quote_plus(searchTerm), maxItems)

def DumpAllEpisodes():
    BPTraceEnter()
    categories = GetCategories()
    for category in categories:
        categoryId = GetCategoryId(category)
        titles = GetTitles(categoryId)
        for title in titles:
            titleId = GetTitleId(title)
            episodes = GetEpisodes(titleId, 100)
    BPTraceExit()

def DumpAllSamples():
    BPTraceEnter()
    categories = GetCategories()
    for category in categories:
        categoryId = GetCategoryId(category)
        titles = GetTitles(categoryId)
        for title in titles:
            titleId = GetTitleId(title)
            episodes = GetSamples(titleId, 100)
    BPTraceExit()
