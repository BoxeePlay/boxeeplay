import mc
import svtmc as svt
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
        time.sleep(0.001) #�ckelfulhack
        loadPrograms()
        loadEpisodes()
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
    target.SetItems(svt.GetCategories())
    mc.HideDialogWait()
    BPLog("Successfully loaded all categories.", Level.DEBUG)
    BPTraceExit()

def loadPrograms():
    BPTraceEnter()
    mc.ShowDialogWait()
    cList = mc.GetWindow(14000).GetList(1000)
    try:
        cItem = cList.GetItem(cList.GetFocusedItem())
        cId   = svt.GetCategoryId(cItem)
        programs = svt.GetTitles(cId)
    except Exception, e:
        BPLog("Laddning av program misslyckades: %s" %e, Level.ERROR)
        cId = -1
        programs = mc.ListItems() #Empty..
    setPrograms(programs)
    mc.HideDialogWait()
    BPLog("Finished loading programs in category %s." %cId, Level.DEBUG)
    BPTraceExit()

selectedTitleId = str("")

def loadEpisodes():
    global selectedTitleId

    BPTraceEnter()
    mc.ShowDialogWait()
    pList = mc.GetWindow(14000).GetList(2000)
    try:
        pItem = pList.GetItem(pList.GetFocusedItem())
        selectedTitleId = svt.GetTitleId(pItem)
        episodes = svt.GetEpisodesAndSamples(selectedTitleId)
    except:
        BPLog("Laddning av avsnitt misslyckades.", Level.ERROR)
        selectedTitleId = str("")
        episodes = mc.ListItems() #Empty
    setEpisodes(episodes)
    mc.HideDialogWait()
    BPLog("Finished loading episodes in category %s." %selectedTitleId, Level.DEBUG)
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
    global selectedTitleId

    BPTraceEnter()
    mc.ShowDialogWait()
    selectedTitleId = str("")
    setPrograms(mc.ListItems())
    setEpisodes(mc.ListItems())
    try:
            setEpisodes(svt.GetLiveEpisodes())
    except Exception, e:
        BPLog("Could not show live episodes: %s" %e, Level.ERROR)
    mc.HideDialogWait()
    BPTraceExit()

def search():
    global selectedTitleId

    BPTraceEnter()
    mc.ShowDialogWait()
    selectedTitleId = str("")
    setPrograms(mc.ListItems())
    setEpisodes(mc.ListItems())
    try:
        searchTerm = mc.GetWindow(14000).GetEdit(110).GetText()
        try:
            searchTerm = searchTerm.decode("utf-8").encode("latin1")
            setEpisodes(svt.SearchEpisodesAndSamples(searchTerm))
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

def populateNextSamplesPage():
    BPTraceEnter()
    mc.ShowDialogWait()

    try:
        if len(selectedTitleId) > 0:
            sampleList = mc.GetWindow(14000).GetList(3001)
            # Remember the item that was focused when the action was initiated
            originallyFocusedItemNo = sampleList.GetFocusedItem()
            list = sampleList.GetItems()
            # This check prevents loading of next page
            # before the page to be loaded is loaded
            # due to ondown triggered twice on the same item (ondown, up, ondown)
            if originallyFocusedItemNo + 1 == len(list):
                # There appears to be a bug in the SVT XML load routine so that
                # the same item is loaded as both the last on page 2 (101-200) and
                # the first on page 3 (201-300)
                newItems = svt.GetNextSamplesPage(selectedTitleId, sampleList)
                if len(newItems) > 0:
                    for newItem in newItems:
                        list.append(newItem)
                    # If the focused item is still the same (the last)
                    # advance to the first newly loaded item
                    # otherwise keep the focused item
                    # if for example the user scrolled up during the load
                    focusedItemNo = sampleList.GetFocusedItem()
                    if focusedItemNo == originallyFocusedItemNo:
                        focusedItemNo = focusedItemNo + 1
                    sampleList.SetItems(list)
                    sampleList.SetFocusedItem(focusedItemNo)
    except Exception, e:
        BPLog("Could not load next sample page. Exception: %s" %(e), Level.ERROR)
    mc.HideDialogWait()
    BPTraceExit()
