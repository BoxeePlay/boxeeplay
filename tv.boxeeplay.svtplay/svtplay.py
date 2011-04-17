# coding=utf-8
import mc,urllib2, urllib, re, sys, os, time
import content, utilities
from urllib import quote_plus, urlencode

def getStart():
	data = utilities.getData(content.baseurl)
	ul = re.compile('<ul class="navigation playerbrowser[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)[0]
	types = re.compile('<li class="[^"]*">\W+<a href="([^"]+)"[^>]*>([^<]+)').findall(ul, re.DOTALL)
    
	items = []
	for url,title in types:
		c1 = content.videoitem()
		c1.name = utilities.decodeHtmlEntities(title)
		c1.url = url
		c1.type = 'startitem'
		items.append(c1)
        
	return items    

def getStartEpisodes(url):
	data = utilities.getData(content.baseurl+'/'+url)
	uls = re.compile('<ul class="list {pagenum:[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)[0]
	lis = re.compile('<li class="[^"]*">\W+<a href="([^"]+)" title="([^"]+)"').findall(uls, re.DOTALL)
	items = itemList = mc.ListItems()
	for url,title in lis:
		mc.LogInfo('**************** '+title+'   -   '+content.baseurl+url )
		i = mc.ListItem(mc.ListItem.MEDIA_VIDEO_CLIP)
		i.SetLabel(title)
		i.SetPath(content.baseurl+url)
		i.SetProperty("url", content.baseurl+url)
		items.append(i)
	return items


def getCategories():
	data = utilities.getData(content.baseurl+'/kategorier')
	ul = re.compile('<ul class="list category-list[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)[0]
	categories = re.compile('<li class="[^"]*">\W+<div class="container">\W*<a href="([^"]+)"[^>]*>\W*<img[^>]+src="([^"]+)[^>]+>\W*<span class="bottom"></span>\W*<span class="[^"]*">([^>]+)</span>').findall(ul, re.DOTALL)
    
	items = []
	for curl, image, title in categories:
		c1 = content.videoitem()
		c1.name = utilities.decodeHtmlEntities(title)
		c1.url = curl
		c1.image = image
		c1.level = 'category'
		c1.type = 'folder'
		items.append(c1)
        
	return items    

def getProgramRSS(url):
	data = utilities.getData(content.baseurl+url)
	ref = re.compile('<link rel="alternate" href="([^"]+)"').findall(data, re.DOTALL)
	return ref[0]
    
def getPrograms(url):
    data = utilities.getData(content.baseurl+url)
    uls = re.compile('<ul class="list[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)
    #pagecount = int(re.compile('<ul class="list {pagenum:(\d+)[^"]*">[\W\w]+?</ul>').findall(data, re.DOTALL)[0])
    items = []
    for ul in uls:
		programs = re.compile('<li class="[^"]*"\W*>\W+<a href="([^"]+)"[^>]+title="([^"]*)"[^>]+>\W+<img[^>]+src="[^"]+[^>]+>\W+(<!--[^/]+/span -->\W+){0,1}<span[^>]*>([^<]+)</span>').findall(ul, re.DOTALL)
		for purl, desc, x, title in programs:
			c1 = content.videoitem()
			c1.url = purl
			c1.name = title
			c1.desc = desc
			items.append(c1)
    return items
	
def getEpisodes(url):
	data = utilities.getData(content.baseurl+url)
	uls = re.compile('<link rel="alternate" href="([^"]+)"').findall(data, re.DOTALL)
	items = []
	for ul in uls:
		data = utilities.getData(ul)
		programs = re.compile('<item>\W*<title>([^"]+)</title>\W*<link>([^"]+)</link>').findall(data, re.DOTALL)
		for title, purl in programs:
			#data = getData(purl)
			#videolink = re.compile('dynamicStreams=url:([^,]+),').findall(data, re.DOTALL)[0]
			#addListItem(videolink, videolink, "", 'video')
			data = utilities.getData(purl)
			image=re.compile('<meta property="og:image" content="([^"]+)"').findall(data, re.DOTALL)[0]
			c1 = content.videoitem()
			c1.name = utilities.decodeHtmlEntities(title)
			c1.url = purl
			c1.image = image
			c1.level = 'video'
			c1.type = 'video'
			items.append(c1)
	return items

def getImageUrl(data):
	uls = re.compile('<meta property="og:image" content="([^"]+)"').findall(data, re.DOTALL)
	return uls[0]

def getVideoUrl(data):
	try:
		video = re.compile('<video id="httpStreaming-video" width="640" height="360" src="([^"]+)"').findall(data, re.DOTALL)
		return video[0]
	except:
		return ''
	
def getDescription(data):
	desc = re.compile('<meta property="og:description" content="([^"]+)"').findall(data, re.DOTALL) 
	return desc[0]

def defineVideo(item):
	data = utilities.getData(item.GetPath())
	img = getImageUrl(data)
	desc = getDescription(data)
	video = getVideoUrl(data)
	item.SetDescription(desc)
	item.SetThumbnail(img)
	item.SetContentType('video/x-flv')
	
	play = re.compile('dynamicStreams=url:(.*?)\.mp4', re.DOTALL + re.IGNORECASE).search(str(data)).group(1)
	domain = re.compile('^(.*?)/kluster', re.DOTALL + re.IGNORECASE).search(str(play)).group(1)
	id = re.compile('_definst_/(.*?)$', re.DOTALL + re.IGNORECASE).search(str(play)).group(1)
	url = 'http://boxeeplay.tv/flowplayer/index.html?net=' + str(domain) + '&id=mp4:' + str(id) + '.mp4'
	
	mc.LogInfo('******** URL = '+url)
	
	item.SetPath(url)
	item.SetProperty('url',url)
	#item.SetDomain('boxeeplay.tv')
	#item.SetJSactions(quote_plus('http://bartsidee.nl/boxee/apps/js/flow.js'))
	
	return item

def play(listitem):
	#data = getData(url)
	#videolink = re.compile('pathflv=([^&]+)').findall(data, re.DOTALL)[0]
	
	#item=xbmcgui.ListItem(name, iconImage='', thumbnailImage='')
	#item.setInfo(type="Video", infoLabels={ "Title": name})
	
   #my_stream = {
   #'url':      listitem.GetPath(),
   #'quality':  'A',
   #'title':    listitem.GetLabel()
   #}
   
   #playHlsStream(my_stream)	
	
	player = mc.GetPlayer()
	player.Play(listitem)
	#mc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(videolink, item)
	
		
		