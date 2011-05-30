import mc
import tvseries
import time
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

def initiate():
    BPTraceEnter()
    if len(mc.GetWindow(14000).GetList(1000).GetItems()) == 0:
        BPLog("No programs in program listing. Loading defaults.", Level.DEBUG)
        loadChannels()
        time.sleep(0.001) #Äckelfulhack
        loadPrograms()
        loadEpisodes()
    BPTraceExit()

def loadChannels():
    BPTraceEnter()
    mc.ShowDialogWait()
    target = mc.GetWindow(14000).GetList(1000)
    target.SetItems(tvseries.GetChannels())
    mc.HideDialogWait()
    BPLog("Successfully loaded all channels.", Level.DEBUG)
    BPTraceExit()

def loadPrograms():
    BPTraceEnter()
    mc.ShowDialogWait()
    cList = mc.GetWindow(14000).GetList(1000)
    try:
        cItem = cList.GetItem(cList.GetFocusedItem())
        cUrl   = tvseries.GetSeriesUrlForChannel(cItem)
        programs = tvseries.GetSeries(cUrl)
    except Exception, e:
        BPLog("Laddning av program misslyckades: %s" %e, Level.ERROR)
        cId = -1
        programs = mc.ListItems() #Empty..
    setPrograms(programs)
    mc.HideDialogWait()
    BPLog("Finished loading programs in channel %s." %cUrl, Level.DEBUG)
    BPTraceExit()

def loadEpisodes():
    BPTraceEnter()
    mc.ShowDialogWait()
    pList = mc.GetWindow(14000).GetList(2000)
    try:
        pItem = pList.GetItem(pList.GetFocusedItem())
        pUrl   = tvseries.GetEpisodesUrlForSerie(pItem)
        episodes = tvseries.GetEpisodes(pUrl)
    except:
        BPLog("Laddning av avsnitt misslyckades.", Level.ERROR)
        pUrl = -1
        episodes = mc.ListItems() #Empty
    setEpisodes(episodes)
    mc.HideDialogWait()
    BPLog("Finished loading episodes for serie %s." %pUrl, Level.DEBUG)
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

def search():
    BPTraceEnter()
    mc.ShowDialogWait()
    setPrograms(mc.ListItems())
    setEpisodes(mc.ListItems())
    try:
        searchTerm = mc.GetWindow(14000).GetEdit(110).GetText()
        try:
            searchTerm = searchTerm.decode("utf-8").encode("latin1")
            setPrograms(tvseries.SearchSeries(searchTerm))
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
    BPTraceEnter()
    l = mc.GetWindow(14000).GetList(3001)
    item = l.GetItem(l.GetFocusedItem())
    BPLog("Playing clip \"%s\" with path \"%s\"." %(item.GetLabel(), item.GetPath()))
    mc.GetPlayer().Play(item)
    BPTraceExit()
