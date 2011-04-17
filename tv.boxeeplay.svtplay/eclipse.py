import svtplay, content, utilities

#===============================================================================
#
#===============================================================================
def printcat():
    items = svtplay.getCategories()
    print len(items)

def printprograms():
    items = svtplay.getPrograms('/c/96251/barn') #barda
    print len(items)

    
printprograms()

