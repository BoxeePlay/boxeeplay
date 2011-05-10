import mc
import logger
from logger import BPLog, Level

__author__ = 'Pehrsons'

class Browser:
    def __init__(self):
        self.Left = 0  #amount
        self.Right = 0 #amount
        self.Main = -1 #index
        self.Controls = []
        self.Items = []
        self.CurrentItem = None
        self.Ready = (len(self.Left) > 0)\
                 and (len(self.Right) > 0)\
                 and (self.Main is not None)\
                 and (self.Items is not None)

    def RegisterMain(self, windowId, controlId):
        self.Main = self.Left
        self.Controls.insert(self.Main, (windowId, controlId))

    def RegisterLeft(self, windowId, controlIds):
        if not self.Left:
            if self.Main > -1:
                self.Main += len(controlIds)
            self.Controls.insert(0,map(lambda c: (windowId,c), controlIds))
        else:
            BPLog("Left registration with already set left controls")

    def RegisterRight(self, windowId, controlIds):
        if not self.Right:
            if self.Main > -1:
                self.Main += len(controlIds)
            self.Controls.append(map(lambda c: (windowId,c), controlIds))
        else:
            BPLog("Right registration with already set right controls")

    def SetItems(self, items):
        if len(items) > 0:
            self.Items = items
            self.CurrentItem = 0

    def MoveLeft(self):
        Move(True)

    def MoveRight(self):
        Move(False)

    def Move(self, left):
        if self.CurrentItem is not None:
            if left:
                dir = -1
            else:
                dir = 1
            item = self.CurrentItem - self.Left + dir
            for wc in self.Controls:
                self.SetControl(wc, self.Items[item])
                item += 1
        else:
            BPLog("Attempt to move but list items were not set.",Level.ERROR)

    def SetControl(self, (w,c), item):
        try:
            win = mc.GetWindow(w)
            img = win.GetImage(c+1) # Large Image Control
            img.SetTexture(item.GetIcon())
            lbl = win.GetLabel(c+2) # Label Control
            lbl.SetLabel(item.GetLabel())
            desc = win.GetLabel(c+3) # Label Control
            desc.SetLabel(item.GetDescription())
        except Exception, e:
            BPLog("Error when setting control", Level.ERROR)