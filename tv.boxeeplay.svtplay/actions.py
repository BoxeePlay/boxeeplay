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
    target = mc.GetWindow(14000).GetList(2000)
    try:
        cItem = cList.GetItem(cList.GetFocusedItem())
        cId   = svt.GetCategoryId(cItem)
        programs = svt.GetTitles(cId)
    except:
        BPLog("Laddning av program misslyckades", Level.ERROR)
        cId = -1
        programs = mc.ListItems() #Empty..
    target.SetItems(programs)
    target.SetFocus()
    mc.HideDialogWait()
    BPLog("Finished loading programs in category %s." %cId, Level.DEBUG)
    BPTraceExit()

def loadEpisodes():
    BPTraceEnter()
    mc.ShowDialogWait()
    pList = mc.GetWindow(14000).GetList(2000)
    target = mc.GetWindow(14000).GetList(3001)
    try:
        pItem = pList.GetItem(pList.GetFocusedItem())
        pId   = svt.GetTitleId(pItem)
        episodes = svt.GetEpisodes(pId)
    except:
        BPLog("Laddning av avsnitt misslyckades.", Level.ERROR)
        pId = -1
        episodes = mc.ListItems() #Empty
    target.SetItems(episodes)
    target.SetFocus()
    mc.HideDialogWait()
    BPLog("Finished loading episodes in category %s." %pId, Level.DEBUG)
    BPTraceExit()
