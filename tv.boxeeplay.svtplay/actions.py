import mc
import svtmc as svt
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

def initiate():
    BPTraceEnter()
    loadCategories()
    programs = mc.GetWindow(14000).GetList(2000).GetItems()
    if len(programs) == 0:
        BPLog("No programs in program listing. Loading defaults.", Level.DEBUG)
        loadPrograms()
        loadEpisodes()
    else:
        mc.GetWindow(14000).GetList(1000).SetFocus()
    BPTraceExit()

def loadCategories():
    BPTraceEnter()
    mc.ShowDialogWait()
    target = mc.GetWindow(14000).GetList(1000)
    target.SetItems(svt.GetCategories())
    target.Refresh()
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
    except:
        BPLog("Laddning av program misslyckades", Level.ERROR)
        cId = -1
        programs = mc.ListItems() #Empty..
    setPrograms(programs)
    mc.HideDialogWait()
    BPLog("Finished loading programs in category %s." %cId, Level.DEBUG)
    BPTraceExit()

def loadEpisodes():
    BPTraceEnter()
    mc.ShowDialogWait()
    pList = mc.GetWindow(14000).GetList(2000)
    try:
        pItem = pList.GetItem(pList.GetFocusedItem())
        pId   = svt.GetTitleId(pItem)
        episodes = svt.GetEpisodes(pId)
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
    target.SetFocus()
    BPTraceExit()

def setEpisodes(items):
    BPTraceEnter()
    target = mc.GetWindow(14000).GetList(3001)
    target.SetItems(items)
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
            setEpisodes(svt.SearchEpisodes(searchTerm))
        except Exception, e:
            BPLog("Could not search for %s: %s" %(searchTerm, e), Level.ERROR)
    except Exception, e:
        BPLog("Could not search: %s" %e, Level.ERROR)
    mc.HideDialogWait()
    BPTraceExit()

def playVideo():
    BPTraceEnter()
    l = mc.GetWindow(14000).GetList(3001)
    item = l.GetItem(l.GetFocusedItem())
    mc.GetPlayer().Play(item)
    BPTraceExit()
