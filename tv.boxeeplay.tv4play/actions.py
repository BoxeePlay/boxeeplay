import mc
import tv4mc as playmc
import time
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

focusedCategoryNo = -1
focusedTitleNo = -1
focusedEpisodeNo = -1
labelPrograms = ""
labelEpisodes = ""

def initiate():
    global focusedCategoryNo
    global focusedTitleNo
    global focusedEpisodeNo
    global labelPrograms
    global labelEpisodes
    BPTraceEnter()
    if len(mc.GetWindow(14000).GetList(1000).GetItems()) == 0:
        BPLog("No programs in program listing. Loading defaults.", Level.DEBUG)
        loadCategories()
        time.sleep(0.001) #Äckelfulhack
        loadMostViewedPrograms()
    else:
        #Restore last focus
        mc.GetWindow(14000).GetLabel(2001).SetLabel(labelPrograms)
        mc.GetWindow(14000).GetLabel(3002).SetLabel(labelEpisodes)
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
    win = mc.GetWindow(14000)
    time.sleep(0.001) #Äckelfulhack
    target = win.GetList(1000)
    time.sleep(0.001) #Äckelfulhack
    cats = playmc.GetCategories()
    time.sleep(0.001) #Äckelfulhack
    target.SetItems(cats)
    mc.HideDialogWait()
    BPLog("Successfully loaded all categories.", Level.DEBUG)
    BPTraceExit()

def loadPrograms():
    BPTraceEnter()
    mc.ShowDialogWait()
    cList = mc.GetWindow(14000).GetList(1000)
    setPrograms(mc.ListItems(),"")
    setEpisodes(mc.ListItems(),"")
    try:
        cItem = cList.GetItem(cList.GetFocusedItem())
        cId   = playmc.GetCategoryId(cItem)
        programs = playmc.GetTitles(cId)
        title = cItem.GetLabel()
    except Exception, e:
        BPLog("Laddning av program misslyckades: %s" %e, Level.ERROR)
        cId = -1
        programs = mc.ListItems() #Empty..
        title = ""
    setPrograms(programs, title)
    mc.HideDialogWait()
    BPLog("Finished loading programs in category %s." %cId, Level.DEBUG)
    BPTraceExit()

selectedTitleId = str("")
    
def loadMostViewedPrograms():
    BPTraceEnter()
    mc.ShowDialogWait()
    setPrograms(mc.ListItems(),"")
    setEpisodes(mc.ListItems(),"")
    try:
        programs = playmc.GetMostViewedPrograms()
        title = "Mest sedda program"
    except Exception, e:
        BPLog("Laddning av program misslyckades: %s" %e, Level.ERROR)
        programs = mc.ListItems() #Empty..
        title = ""
    setEpisodes(programs, title)
    mc.HideDialogWait()
    BPLog("Finished loading most viewed programs.", Level.DEBUG)
    BPTraceExit()

def loadMostViewedClips():
    BPTraceEnter()
    mc.ShowDialogWait()
    setPrograms(mc.ListItems(),"")
    setEpisodes(mc.ListItems(),"")
    try:
        programs = playmc.GetMostViewedClips()
        title = "Mest sedda klipp"
    except Exception, e:
        BPLog("Laddning av klipp misslyckades: %s" %e, Level.ERROR)
        programs = mc.ListItems() #Empty..
        title = ""
    setEpisodes(programs, title)
    mc.HideDialogWait()
    BPLog("Finished loading most viewed programs.", Level.DEBUG)
    BPTraceExit()

def loadEpisodes():
    global selectedTitleId

    BPTraceEnter()
    mc.ShowDialogWait()
    pList = mc.GetWindow(14000).GetList(2000)
    try:
        pItem = pList.GetItem(pList.GetFocusedItem())
        selectedTitleId = playmc.GetTitleId(pItem)
        episodes = playmc.GetEpisodesAndSamples(selectedTitleId)
        title = pItem.GetLabel()
    except Exception, e:
        BPLog("Exception: %s." %str(e), Level.DEBUG)
        BPLog("Laddning av avsnitt misslyckades.", Level.ERROR)
        selectedTitleId = str("")
        episodes = mc.ListItems() #Empty
        title = ""
    setEpisodes(episodes, title)
    mc.HideDialogWait()
    BPLog("Finished loading episodes in category %s." %selectedTitleId, Level.DEBUG)
    BPTraceExit()

def setPrograms(items, title):
    global labelPrograms

    BPTraceEnter()
    win = mc.GetWindow(14000)
    time.sleep(0.01) #Äckelfulhack
    target = win.GetList(2000)
    time.sleep(0.01) #Äckelfulhack
    # for program in items:
        # BPLog(program.GetIcon(), Level.DEBUG)
        # program.Dump()
    # BPLog("---", Level.DEBUG)
    target.SetItems(items)
    # for program in items:
        # BPLog(program.GetIcon(), Level.DEBUG)
    # BPLog("---", Level.DEBUG)
    time.sleep(0.01) #Äckelfulhack
    for program in target.GetItems():
        BPLog(program.GetThumbnail(), Level.DEBUG)
        # program.Dump()
    labelPrograms = title
    win.GetLabel(2001).SetLabel(title)
    if len(items) > 0:
        target.SetFocus()
    BPTraceExit()

def setEpisodes(items, title):
    global labelEpisodes

    BPTraceEnter()

    win = mc.GetWindow(14000)
    time.sleep(0.01) #Äckelfulhack
    target = win.GetList(3001)
    time.sleep(0.01) #Äckelfulhack
    target.SetItems(items)
    labelEpisodes = title

    win.GetLabel(3002).SetLabel(title)
    if len(items) > 0:
        target.SetFocus()
    BPTraceExit()

def showLive():
    global selectedTitleId

    BPTraceEnter()
    mc.ShowDialogWait()
    selectedTitleId = str("")
    setPrograms(mc.ListItems(), "")
    setEpisodes(mc.ListItems(), "")
    try:
        setEpisodes(playmc.GetLiveEpisodes(), "Livesändningar")
    except Exception, e:
        BPLog("Could not show live episodes: %s" %e, Level.ERROR)
    mc.HideDialogWait()
    BPTraceExit()

def search():
    global selectedTitleId

    BPTraceEnter()
    mc.ShowDialogWait()
    selectedTitleId = str("")
    setPrograms(mc.ListItems(), "")
    setEpisodes(mc.ListItems(), "")
    try:
        searchTerm = mc.GetWindow(14000).GetEdit(110).GetText()
        try:
            searchTerm = searchTerm.decode("utf-8")
            programs = playmc.SearchPrograms(searchTerm.encode("utf-8"))
            setPrograms(programs, "Program: " + str(len(programs)) + " träffar på \"" + searchTerm.encode("utf-8") + "\"")
            episodes = playmc.SearchEpisodesAndSamples(searchTerm.encode("utf-8"))
            setEpisodes(episodes, "Avsnitt och klipp: " + str(len(episodes)) + " träffar på \"" + searchTerm.encode("utf-8") + "\"")
        except Exception, e:
            BPLog("Could not search for %s: %s" %(searchTerm.encode("utf-8"), e), Level.ERROR)
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
