import mc
import tv4mc as playmc
import time
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

focusedCategoryNo = -1
focusedTitleNo = -1
focusedEpisodeNo = -1

def initiate():
    global focusedCategoryNo
    global focusedTitleNo
    global focusedEpisodeNo
    BPTraceEnter()
    if len(mc.GetWindow(14000).GetList(1000).GetItems()) == 0:
        BPLog("No programs in program listing. Loading defaults.", Level.DEBUG)
        loadCategories()
        time.sleep(0.001) #Äckelfulhack
        loadRecommendedPrograms()
    else:
        #Restore last focus
        if focusedCategoryNo >= 0:
            categoryList = mc.GetWindow(14000).GetList(1000)
            categoryList.SetFocusedItem(focusedCategoryNo)
        if focusedTitleNo >= 0:
            titleList = mc.GetWindow(14000).GetList(2000)
            titleList.SetFocusedItem(focusedTitleNo)
        if focusedEpisodeNo >= 0:
            episodeList = mc.GetWindow(14000).GetList(3001)
            episodeList.SetFocusedItem(focusedEpisodeNo)
    BPTraceExit()

def loadCategories():
    BPTraceEnter()
    mc.ShowDialogWait()
    target = mc.GetWindow(14000).GetList(1000)
    target.SetItems(playmc.GetCategories())
    mc.HideDialogWait()
    BPLog("Successfully loaded all categories.", Level.DEBUG)
    BPTraceExit()

def loadPrograms():
    BPTraceEnter()
    mc.ShowDialogWait()
    setPrograms(mc.ListItems())
    setEpisodes(mc.ListItems())
    cList = mc.GetWindow(14000).GetList(1000)
    try:
        cItem = cList.GetItem(cList.GetFocusedItem())
        cId   = playmc.GetCategoryId(cItem)
        programs = playmc.GetTitles(cId)
    except Exception, e:
        BPLog("Laddning av program misslyckades: %s" %e, Level.ERROR)
        cId = -1
        programs = mc.ListItems() #Empty..
    setPrograms(programs)
    mc.HideDialogWait()
    BPLog("Finished loading programs in category %s." %cId, Level.DEBUG)
    BPTraceExit()

def loadRecommendedPrograms():
    BPTraceEnter()
    mc.ShowDialogWait()
    setPrograms(mc.ListItems())
    setEpisodes(mc.ListItems())
    try:
        programs = playmc.GetRecommendedTitles()
    except Exception, e:
        BPLog("Laddning av program misslyckades: %s" %e, Level.ERROR)
        programs = mc.ListItems() #Empty..
    setPrograms(programs)
    mc.HideDialogWait()
    BPLog("Finished loading recomended programs.", Level.DEBUG)
    BPTraceExit()

def loadEpisodes():
    BPTraceEnter()
    mc.ShowDialogWait()
    pList = mc.GetWindow(14000).GetList(2000)
    try:
        pItem = pList.GetItem(pList.GetFocusedItem())
        pId   = playmc.GetTitleId(pItem)
        episodes = playmc.GetEpisodesAndSamples(pId)
    except:
        BPLog("Laddning av avsnitt misslyckades.", Level.ERROR)
        pId = -1
        episodes = mc.ListItems() #Empty
    setEpisodes(episodes)
    mc.HideDialogWait()
    BPLog("Finished loading episodes in category %s." %pId, Level.DEBUG)
    BPTraceExit()

def setPrograms(items):
    BPTraceEnter()
    target = mc.GetWindow(14000).GetList(2000)
    target.SetItems(items)
    if len(items) > 0:
        target.SetFocus()
    BPTraceExit()

def setEpisodes(items):
    BPTraceEnter()
    target = mc.GetWindow(14000).GetList(3001)
    target.SetItems(items)
    if len(items) > 0:
        target.SetFocus()
    BPTraceExit()

def showLive():
    BPTraceEnter()
    mc.ShowDialogWait()
    setPrograms(mc.ListItems())
    setEpisodes(mc.ListItems())
    try:
            setEpisodes(playmc.GetLiveEpisodes())
    except Exception, e:
        BPLog("Could not show live episodes: %s" %e, Level.ERROR)
    mc.HideDialogWait()
    BPTraceExit()

def search():
    BPTraceEnter()
    mc.ShowDialogWait()
    setPrograms(mc.ListItems())
    setEpisodes(mc.ListItems())
    try:
        searchTerm = mc.GetWindow(14000).GetEdit(110).GetText()
        try:
            searchTerm = searchTerm.decode("utf-8").encode("latin1")
            setEpisodes(playmc.SearchEpisodesAndSamples(searchTerm))
        except Exception, e:
            BPLog("Could not search for %s: %s" %(searchTerm, e), Level.ERROR)
    except Exception, e:
        BPLog("Could not search: %s" %e, Level.ERROR)
    mc.HideDialogWait()
    BPTraceExit()

def appendSearch(str):
    BPTraceEnter()
    try:
        searchBar = mc.GetWindow(14000).GetEdit(110)
        searchBar.SetText(searchBar.GetText()+str)
    except Exception, e:
        BPLog("Could not append searchbar with %s. Exception: %s" %(str,e), Level.ERROR)
    BPTraceExit()

def playVideo():
    global focusedCategoryNo
    global focusedTitleNo
    global focusedEpisodeNo
    BPTraceEnter()

    # Remember the selections in the lists
    categoryList = mc.GetWindow(14000).GetList(1000)
    if len(categoryList.GetItems()) > 0:
        focusedCategoryNo = categoryList.GetFocusedItem()
    else:
        focusedCategoryNo = -1

    titleList = mc.GetWindow(14000).GetList(2000)
    if len(titleList.GetItems()) > 0:
        focusedTitleNo = titleList.GetFocusedItem()
    else:
        focusedTitleNo = -1

    episodeList = mc.GetWindow(14000).GetList(3001)
    if len(episodeList.GetItems()) > 0:
        focusedEpisodeNo = episodeList.GetFocusedItem()
    else:
        focusedEpisodeNo = -1

    item = episodeList.GetItem(focusedEpisodeNo)
    BPLog("Playing clip \"%s\" with path \"%s\" and bitrate %s." %(item.GetLabel(), item.GetPath(), item.GetProperty("bitrate")))
    mc.GetPlayer().Play(item)
    BPTraceExit()
