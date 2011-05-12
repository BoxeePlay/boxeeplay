#encoding:utf-8
#author:Mats Boisen
#project:boxeeplay
#repository:https://bitbucket.org/hesapesa/boxeeplay
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/license/GPL/2.0/)

import mc
from urllib import quote_plus
import tv4xml
from logger import BPLog,BPTraceEnter,BPTraceExit,Level

def GetCategories() :
    return tv4xml.GetCategories()

def GetCategoryId(item) :
    return item.GetProperty("id")

def GetTitles(id) :
    return tv4xml.GetTitles(id)

def GetTitleId(item) :
    return item.GetProperty("id")

def GetEpisodes(id) :
    return tv4xml.GetEpisodes(id)

def GetSamples(id) :
    #TODO Create Get Samples
    return 0

def SearchEpisodes(searchTerm) :
    #TODO Create search
    return mc.ListItems()

def SearchSamples(searchTerm) :
    #TODO Create Search
    return mc.ListItems()

def DumpAllEpisodes():
    BPTraceEnter()
    categories = GetCategories()
    for category in categories:
        categoryId = GetCategoryId(category)
        titles = GetTitles(categoryId)
        for title in titles:
            titleId = GetTitleId(title)
            episodes = GetEpisodes(titleId)
    BPTraceExit()

def DumpAllSamples():
    BPTraceEnter()
    categories = GetCategories()
    for category in categories:
        categoryId = GetCategoryId(category)
        titles = GetTitles(categoryId)
        for title in titles:
            titleId = GetTitleId(title)
            episodes = GetSamples(titleId)
    BPTraceExit()
