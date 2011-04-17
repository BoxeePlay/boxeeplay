import svtplay
import mc
from urllib import quote_plus, urlencode

def focusCategory():
    control = mc.GetActiveWindow().GetControl(1000)
    control.SetFocus()

def listPrograms(url):
    list = mc.GetActiveWindow().GetList(2000)
    items = svtplay.getPrograms(url)
    fillListWithItems(items,list)
    list.SetFocus()
    list.SetFocusedItem(0)
    
def listEpisodes():

    listP = mc.GetActiveWindow().GetList(2000)
    focused = listP.GetItem(listP.GetFocusedItem()) 
    url = focused.GetProperty("url")
    ptitle = focused.GetLabel()
    
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
    
    mc.GetActiveWindow().GetList(3001).SetItems(items)
    mc.GetActiveWindow().GetList(3001).SetFocusedItem(0)
    mc.GetActiveWindow().GetList(3001).SetFocus()


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

def fillListWithItems(items,list):
    itemList = mc.ListItems()
    
    for item in items:
        i = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
        i.SetLabel(item.name)
        #i.SetPath(item.url)
        i.SetProperty("type", item.type)
        i.SetProperty("url", item.url)
        i.SetThumbnail(item.image)
        itemList.append(i)
        
    list.SetItems(itemList)

def playRTMP():
    url = "rtmp://fl11.c91005.cdn.qbrick.com/91005/_definst_/kluster/20110321/PG-1132930-012A-BARDA2009-01-mp4-e-v1.mp4"
    mc.ShowDialogNotification(url)
    listItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
    listItem.SetPath(url)
    listItem.SetLabel('My Test Video')
    listItem.SetContentType('application/vnd.apple.mpegurl')
    mc.GetPlayer().Play(listItem)
    
    
def redefineVideos():
    listP = mc.GetActiveWindow().GetList(2000)
    focused = listP.GetItem(listP.GetFocusedItem()) 
    ptitle = focused.GetLabel()
    items = mc.GetActiveWindow().GetList(3001).GetItems()
    #Trockla genom listan och sätt bilder!
    for item in items:
        item = svtplay.defineVideo(item)
        item.SetLabel(item.GetLabel().replace(ptitle+" - ",""))
    
    #mc.GetActiveWindow().GetList(3001).SetItems(items)

def home():
    activeButton(1001)
    list = mc.GetActiveWindow().GetList(2000)
    fillListWithItems(svtplay.getStart(),list)

    
    


