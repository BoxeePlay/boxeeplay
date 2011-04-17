import svtplay
import mc
from urllib import quote_plus, urlencode

def focusCategory():
    control = mc.GetActiveWindow().GetControl(1000)
    control.SetFocus()

def listPrograms(url):
    mc.ShowDialogWait()
    list = mc.GetActiveWindow().GetList(2000)
    items = svtplay.getPrograms(url)
    list.SetItems(items)
    list.Refresh()
    list.SetFocus()
    mc.HideDialogWait()
    
def listEpisodes():


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
        url = svtplay.getProgramRSS(url)
        items = mc.GetDirectory(url)
    
    #Trockla genom listan och sätt bilder!
    for item in items:
        item.SetLabel(item.GetLabel().replace(ptitle+" - ",""))
        item = svtplay.defineVideo(item)
    
    mc.HideDialogWait()
    
    if (len(items)>0):
        mc.GetActiveWindow().GetList(3001).SetItems(items)
        mc.GetActiveWindow().GetList(3001).SetFocusedItem(0)
        mc.GetActiveWindow().GetList(3001).SetFocus()

    mc.GetActiveWindow().GetList(2000).SetFocusedItem(1000)

    #for item in mc.GetActiveWindow().GetList(3001).GetItems():
    
def activeButton(numb):
    window = mc.GetWindow(14000)
    window.GetToggleButton(1001).SetSelected(False)
    window.GetToggleButton(1002).SetSelected(False)
    window.GetToggleButton(1003).SetSelected(False)
    window.GetToggleButton(1004).SetSelected(False)
    window.GetToggleButton(1005).SetSelected(False)
    window.GetToggleButton(1006).SetSelected(False)
    window.GetToggleButton(1007).SetSelected(False)
    window.GetToggleButton(1008).SetSelected(False)
    window.GetToggleButton(numb).SetSelected(True)

def redefineVideos():
    listP = mc.GetActiveWindow().GetList(2000)
    focused = listP.GetItem(listP.GetFocusedItem()) 
    ptitle = focused.GetLabel()
    items = mc.GetActiveWindow().GetList(3001).GetItems()
    #Trockla genom listan och sätt bilder!
    for item in items:
        item = svtplay.defineVideo(item)
        item.SetLabel(item.GetLabel().replace(ptitle+" - ",""))
    
def home():
    activeButton(1001)
    list = mc.GetActiveWindow().GetList(2000)
    items = svtplay.getStart()
    list.SetItems(items)
    list.SetFocus()
    list.SetFocusedItem(0)
    listEpisodes()
    redefineVideos()
    
    


