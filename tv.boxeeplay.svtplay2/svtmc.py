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
    # Could potentially load categories directly from
    # http://svtplay.se/mobil/deviceconfiguration.xml
    
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
    item7.SetProperty("id", "arkiv")
    items.append(item7)

    BPTraceExit("Returning %s" % items)
    return items

def GetCategoryId(item) :
    return item.GetProperty("id")

def GetArchiveTitles():
    98382
    BPTraceEnter()
    items = mc.ListItems()

    item1 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item1.SetContentType("text/html")
    item1.SetLabel("Barn")
    item1.SetPath("http://svtplay.se/c/96252/oppet_arkiv?cb,a1364145,1,f,103001/pb,a1364142,1,f,103001/pl,v,,1370538/sb,k102995,1,f,")
    item1.SetAuthor("SVT")
    item1.SetThumbnail("http://material.svtplay.se/content/2/c6/10/29/93/oa_hyland_a.jpg")
    item1.SetProperty("id", "102995")
    items.append(item1)

    item2 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item2.SetContentType("text/html")
    item2.SetLabel("Fakta")
    item2.SetPath("http://svtplay.se/c/96252/oppet_arkiv?cb,a1364145,1,f,103001/pb,a1364142,1,f,103001/pl,v,,1370538/sb,k103004,1,f,")
    item2.SetAuthor("SVT")
    item2.SetThumbnail("http://material.svtplay.se/content/2/c6/10/29/93/oa_hyland_a.jpg")
    item2.SetProperty("id", "103004")
    items.append(item2)

    item3 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item3.SetContentType("text/html")
    item3.SetLabel("Fritid")
    item3.SetPath("http://svtplay.se/c/96252/oppet_arkiv?cb,a1364145,1,f,103001/pb,a1364142,1,f,103001/pl,v,,1370538/sb,k103034,1,f,")
    item3.SetAuthor("SVT")
    item3.SetThumbnail("http://material.svtplay.se/content/2/c6/10/29/93/oa_hyland_a.jpg")
    item3.SetProperty("id", "103034")
    items.append(item3)

    item4 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item4.SetContentType("text/html")
    item4.SetLabel("Kultur")
    item4.SetPath("http://svtplay.se/c/96252/oppet_arkiv?cb,a1364145,1,f,103001/pb,a1364142,1,f,103001/pl,v,,1370538/sb,k103069,1,f,")
    item4.SetAuthor("SVT")
    item4.SetThumbnail("http://material.svtplay.se/content/2/c6/10/29/93/oa_hyland_a.jpg")
    item4.SetProperty("id", "103069")
    items.append(item4)

    item5 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item5.SetContentType("text/html")
    item5.SetLabel("Nyheter")
    item5.SetPath("http://svtplay.se/c/96252/oppet_arkiv?cb,a1364145,1,f,103001/pb,a1364142,1,f,103001/pl,v,,1370538/sb,k103107,1,f,")
    item5.SetAuthor("SVT")
    item5.SetThumbnail("http://material.svtplay.se/content/2/c6/10/29/93/oa_hyland_a.jpg")
    item5.SetProperty("id", "103107")
    items.append(item5)

    item6 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item6.SetContentType("text/html")
    item6.SetLabel("Nöje")
    item6.SetPath("http://svtplay.se/c/96252/oppet_arkiv?cb,a1364145,1,f,103001/pb,a1364142,1,f,103001/pl,v,,1370538/sb,k103200,1,f,")
    item6.SetAuthor("SVT")
    item6.SetThumbnail("http://material.svtplay.se/content/2/c6/10/29/93/oa_hyland_a.jpg")
    item6.SetProperty("id", "103200")
    items.append(item6)

    item7 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item7.SetContentType("text/html")
    item7.SetLabel("Samhälle")
    item7.SetPath("http://svtplay.se/c/96252/oppet_arkiv?cb,a1364145,1,f,103001/pb,a1364142,1,f,103001/pl,v,,1370538/sb,k103213,1,f,")
    item7.SetAuthor("SVT")
    item7.SetThumbnail("http://material.svtplay.se/content/2/c6/10/29/93/oa_hyland_a.jpg")
    item7.SetProperty("id", "103213")
    items.append(item7)

    item8 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item8.SetContentType("text/html")
    item8.SetLabel("Sport")
    item8.SetPath("http://svtplay.se/c/96252/oppet_arkiv?cb,a1364145,1,f,103001/pb,a1364142,1,f,103001/pl,v,,1370538/sb,k103230,1,f,")
    item8.SetAuthor("SVT")
    item8.SetThumbnail("http://material.svtplay.se/content/2/c6/10/29/93/oa_hyland_a.jpg")
    item8.SetProperty("id", "103230")
    items.append(item8)

    item9 = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    item9.SetContentType("text/html")
    item9.SetLabel("Jubileumsklipp")
    item9.SetPath("http://svtplay.se/c/96252/oppet_arkiv?cb,a1364145,1,f,103001/pb,a1364142,1,f,103001/pl,v,,1370538/sb,k103243,1,f,")
    item9.SetAuthor("SVT")
    item9.SetThumbnail("http://material.svtplay.se/content/2/c6/10/29/93/oa_hyland_a.jpg")
    item9.SetProperty("id", "103243")
    items.append(item9)

    BPTraceExit("Returning %s" % items)
    return items

def GetTitles(id) :
    if id =="arkiv":
        return GetArchiveTitles()
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/title/list/" + str(id) + "?num=100", 999)

def GetTitleId(item) :
    return item.GetProperty("id")

def GetEpisodes(id=96238) :
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/video/list/" + str(id) + "?expression=full&num=100", 200)

def GetSamples(id=96238) :
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/video/list/" + str(id) + "?expression=sample&num=100", 200)

def GetEpisodesAndSamples(id=96238):
    listItems = GetEpisodes(id)
    sampleItems = GetSamples(id)
    for sampleItem in sampleItems:
        listItems.append(sampleItem)
    return listItems

def GetLiveEpisodes():
    episodes = svtxml.GetDirectory("http://xml.svtplay.se/v1/video/list/96238?expression=nonstop&orderBy=chronological&num=100", 100)
    svtxml.FixLiveAirTime(episodes)
    return episodes

def SearchEpisodes(searchTerm, id="96238", maxItems=100) :
    if (len(searchTerm) == 0):
        return mc.ListItems()
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/video/search/" + str(id) + "?expression=full&num=100&q=" + quote_plus(searchTerm), maxItems)

def SearchSamples(searchTerm, id="96238", maxItems=100) :
    if (len(searchTerm) == 0):
        return mc.ListItems()
    return svtxml.GetDirectory("http://xml.svtplay.se/v1/video/search/" + str(id) + "?expression=sample&num=100&q=" + quote_plus(searchTerm), maxItems)

def SearchEpisodesAndSamples(searchTerm, id="96238", maxItems=100) :
    listItems = SearchEpisodes(searchTerm, id, maxItems)
    sampleItems = SearchSamples(searchTerm, id, maxItems)
    for sampleItem in sampleItems:
        listItems.append(sampleItem)
    return listItems

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
