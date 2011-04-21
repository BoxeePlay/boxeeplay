import svtplay
import mc
import logger
from urllib import quote_plus, urlencode
from logger import BPLog,BPTraceEnter,BPTraceExit

def dialogQuality():
    BPTraceEnter()
    config = mc.GetLocalConfig()
    selection = mc.ShowDialogSelect("V�lj kvalitet p� s�ndningen:", ["HD-kvalitet, 720p, 2400 kbs", "H�g kvalitet, 1400 kbs","Medelkvalitet, 850 kbs","L�g kvalitet, 340 kbs"])
    config.SetValue("quality",selection)
    BPTraceExit()

def focusCategory():
    BPTraceEnter()
    control = mc.GetActiveWindow().GetControl(1000)
    control.SetFocus()
    BPTraceExit()

def listPrograms(url):
    BPTraceEnter(url)
    mc.ShowDialogWait()
    list = mc.GetActiveWindow().GetList(2000)
    items = svtplay.getPrograms(url)
    list.SetItems(items)
    list.Refresh()
    list.SetFocus()
    mc.HideDialogWait()
    BPTraceExit(url)
    
def listEpisodes():
    BPTraceEnter()
    listP = mc.GetActiveWindow().GetList(2000)
    focused = listP.GetItem(listP.GetFocusedItem()) 
    url = focused.GetPath()
    ptitle = focused.GetLabel()

    if (focused.GetProperty('type')=='programpage'):
        listPrograms(focused.GetPath())
        return

    mc.GetActiveWindow().GetList(2000).SetSelected(listP.GetFocusedItem(), True)
    
    mc.ShowDialogWait()
    itemList = mc.ListItems()
    url = url.replace('http:','rss:')
    
    if (focused.GetProperty('type')=='startitem'):
        items = svtplay.getStartEpisodes(url)
    else:
        #url = svtplay.getProgramRSS(url)
        items = mc.GetDirectory(url)
    
    mc.HideDialogWait()
    
    if (len(items)>0):
        mc.GetActiveWindow().GetList(3001).SetItems(items)


    #for item in mc.GetActiveWindow().GetList(3001).GetItems():
    BPTraceExit()
    
def activeButton(numb):
    BPTraceEnter(numb)
    window = mc.GetWindow(14000)
    #window.GetToggleButton(1001).SetSelected(False)
    window.GetToggleButton(1002).SetSelected(False)
    window.GetToggleButton(1003).SetSelected(False)
    window.GetToggleButton(1004).SetSelected(False)
    window.GetToggleButton(1005).SetSelected(False)
    window.GetToggleButton(1006).SetSelected(False)
    window.GetToggleButton(1007).SetSelected(False)
    window.GetToggleButton(1008).SetSelected(False)
    window.GetToggleButton(numb).SetSelected(True)
    BPTraceExit(numb)

def redefineVideos():
    BPTraceEnter()
    listP = mc.GetActiveWindow().GetList(2000)
    focused = listP.GetItem(listP.GetFocusedItem()) 
    ptitle = focused.GetLabel()
    items = mc.GetActiveWindow().GetList(3001).GetItems()
    #Trockla genom listan och s�tt bilder!
    for item in items:
        item = svtplay.defineVideo(item)
        item.SetLabel(item.GetLabel().replace(ptitle+" - ",""))
    BPTraceExit()
    
def home():
    BPTraceEnter()
    activeButton(1002)
    listPrograms('/c/96251/barn')
    list = mc.GetActiveWindow().GetList(2000)
    list.SetFocusedItem(0)
    listEpisodes()
    BPTraceExit()

def playVideo():
    BPTraceEnter()
    listP = mc.GetActiveWindow().GetList(3001)
    focused = listP.GetItem(listP.GetFocusedItem())
    svtplay.playItem(focused)
    BPTraceExit()

