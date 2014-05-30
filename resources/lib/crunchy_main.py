# -*- coding: utf-8 -*-
"""
    CrunchyRoll;xbmc
    Copyright (C) 2012 - 2014 Matthew Beacher
    This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""
import sys
import os
import datetime
import urllib
import urllib2
import xbmc
import xbmcgui
import xbmcplugin
import crunchy_json
import re
import time
import xbmcaddon
import shelve
import random, re, string
import json
import gzip
import StringIO
import dateutil.tz, dateutil.relativedelta, dateutil.parser
__settings__ = xbmcaddon.Addon(id='plugin.video.crunchyroll-takeout')
__language__ = __settings__.getLocalizedString



#####################################################################################

class updateArgs:

	def __init__(self, *args, **kwargs):
		for key, value in kwargs.iteritems():
			if value == 'None':
				kwargs[key] = None
			else:
				kwargs[key] = urllib.unquote_plus(kwargs[key])
		self.__dict__.update(kwargs)

class UI:
	
	def __init__(self):
		self.main = Main(checkMode = False)
		xbmcplugin.setContent(int(sys.argv[1]), 'movies')

	def Language(self):
                self.Language = xbmc.Language(os.getcwd())
	
	def endofdirectory(self, sortMethod = 'none'):
		# set sortmethod to something xbmc can use
		if sortMethod == 'title':
			sortMethod = xbmcplugin.SORT_METHOD_LABEL
		elif sortMethod == 'none':
			sortMethod = xbmcplugin.SORT_METHOD_NONE
		elif sortMethod == 'date':
			sortMethod = xbmcplugin.SORT_METHOD_DATE
		#Sort methods are required in library mode.
		xbmcplugin.addSortMethod(int(sys.argv[1]), sortMethod)
		#let xbmc know the script is done adding items to the list.
		dontAddToHierarchy = False
		xbmcplugin.endOfDirectory(handle = int(sys.argv[1]), updateListing = dontAddToHierarchy)
			
	def addItem(self, info, isFolder=True, total_items = 0):
		#Defaults in dict. Use 'None' instead of None so it is compatible for quote_plus in parseArgs
		info.setdefault('url','None')
		info.setdefault('Thumb','None')
		info.setdefault('Fanart_Image', xbmc.translatePath( __settings__.getAddonInfo('fanart') ) )
		info.setdefault('mode','None')
		info.setdefault('count','0')
		info.setdefault('filterx','None')
		info.setdefault('id','None')
		info.setdefault('series_id','None')
		info.setdefault('offset','0')
		info.setdefault('season','1')
		info.setdefault('series_id','0')
		info.setdefault('page_url','None')
		info.setdefault('complete','True')
		info.setdefault('showtype','None')
		info.setdefault('Title','None')
		info.setdefault('year','0')
		info.setdefault('plot','No description available.')
		#print info
		#create params for xbmcplugin module
		u = sys.argv[0]+\
			'?url='+urllib.quote_plus(info['url'])+\
			'&mode='+urllib.quote_plus(info['mode'])+\
			'&name='+urllib.quote_plus(info['Title'])+\
			'&id='+urllib.quote_plus(info['id'])+\
			'&count='+urllib.quote_plus(info['count'])+\
			'&series_id='+urllib.quote_plus(info['series_id'])+\
			'&filterx='+urllib.quote_plus(info['filterx'])+\
			'&offset='+urllib.quote_plus(info['offset'])+\
			'&icon='+urllib.quote_plus(info['Thumb'])+\
			'&complete='+urllib.quote_plus(info['complete'])+\
			'&fanart='+urllib.quote_plus(info['Fanart_Image'])+\
			'&season='+urllib.quote_plus(info['season'])+\
			'&showtype='+urllib.quote_plus(info['showtype'])+\
			'&year='+urllib.quote_plus(info['year'])+\
			'&plot='+urllib.quote_plus(info['plot'])
		#create list item
		#print u
		li=xbmcgui.ListItem(label = info['Title'], thumbnailImage = info['Thumb'])
		li.setInfo( type="Video", infoLabels={ "Title":info['Title'], "Plot":info['plot'], "Year":info['year']})
		li.setProperty( "Fanart_Image", info['Fanart_Image'])
		#for videos, replace context menu with queue and add to favorites
		if not isFolder:
			#li.setProperty("IsPlayable", "true")#let xbmc know this can be played, unlike a folder.
			#add context menu items to non-folder items.
			contextmenu = [('Queue Video', 'Action(Queue)')]
			li.addContextMenuItems( contextmenu )
		#for folders, completely remove contextmenu, as it is totally useless.
		else:
			li.addContextMenuItems([], replaceItems=True)
		#add item to list
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=li, isFolder=isFolder, totalItems=total_items)

	def showMain(self):
                local_string = xbmcaddon.Addon(id='plugin.video.crunchyroll-takeout').getLocalizedString
                change_language = __settings__.getSetting("change_language")
                if crunchy_json.CrunchyJSON().loadShelf() is False:
                        self.addItem({'Title':'Session Failed: Check Login'})
                        self.endofdirectory()
                else:
                        if change_language != "0":
                                crunchy_json.CrunchyJSON().changeLocale()
                        Anime = local_string(50000).encode("utf8")
                        Drama = local_string(50004).encode("utf8")
                        Queue = local_string(50005).encode("utf8")
                        Pop = local_string(50009).encode("utf8")
                        History = local_string(50011).encode("utf8")
                        self.addItem({'Title':Queue, 'mode':'queue'})
                        self.addItem({'Title':History, 'mode':'History'})
                        self.addItem({'Title':Anime, 'mode':'Channels','showtype':'Anime'})
                        self.addItem({'Title':Drama, 'mode':'Channels','showtype':'Drama'})
                        #self.addItem({'Title':Pop, 'mode':'Channels','showtype':'Pop'})
                        self.endofdirectory()

	def channels(self):
                local_string = xbmcaddon.Addon(id='plugin.video.crunchyroll-takeout').getLocalizedString
                popular = local_string(50003).encode("utf8")
                Simulcasts = local_string(50006).encode("utf8")
                Recently_Added = local_string(50002).encode("utf8")
                alpha = local_string(50012).encode("utf8")
                Browse_by_Genre = local_string(50007).encode("utf8")
                seasons = local_string(50010).encode("utf8")
                showtype = self.main.args.showtype
                self.addItem({'Title':popular,          'mode':'list_series', 'showtype':showtype, 'filterx':'popular', 'offset':'0'})
                self.addItem({'Title':Simulcasts,       'mode':'list_series', 'showtype':showtype, 'filterx':'simulcast', 'offset':'0'})
                self.addItem({'Title':Recently_Added,   'mode':'list_series', 'showtype':showtype, 'filterx':'updated', 'offset':'0'})
                self.addItem({'Title':alpha,            'mode':'list_series', 'showtype':showtype, 'filterx':'alpha', 'offset':'0'})
                self.addItem({'Title':Browse_by_Genre,  'mode':'list_categories', 'showtype':showtype, 'filterx':'genre', 'offset':'0'})
                self.addItem({'Title':seasons,          'mode':'list_categories', 'showtype':showtype, 'filterx':'season', 'offset':'0'})
                self.endofdirectory()
                
        def json_list_series(self):
                crunchy_json.CrunchyJSON().list_series(self.main.args.name, self.main.args.showtype, self.main.args.filterx, self.main.args.offset)

        def json_list_cat(self):
                crunchy_json.CrunchyJSON().list_categories(self.main.args.name, self.main.args.showtype, self.main.args.filterx)
                
	def json_list_collection(self):
		crunchy_json.CrunchyJSON().list_collections(self.main.args.series_id, self.main.args.name, self.main.args.count, self.main.args.icon, self.main.args.fanart)
		
	def json_list_media(self):
		crunchy_json.CrunchyJSON().list_media(self.main.args.id, self.main.args.filterx, self.main.args.count, self.main.args.complete, self.main.args.season, self.main.args.fanart)

	def json_History(self):
		crunchy_json.CrunchyJSON().History()

	def queue(self):
                crunchy_json.CrunchyJSON().Queue()
		
	def startVideo(self):
		crunchy_json.CrunchyJSON().startPlayback(self.main.args.name, self.main.args.url, self.main.args.id, self.main.args.icon)

	def Fail(self):
                local_string = xbmcaddon.Addon(id='plugin.video.crunchyroll-takeout').getLocalizedString
                badstuff = local_string(70007).encode("utf8")
		self.addItem({'Title':badstuff,'mode':'none'})
		print "Crunchyroll takeout --> crunchy_main.py checkMode fall through"
		self.endofdirectory()

class Main:

	def __init__(self, checkMode = True):
                crunchy_json.CrunchyJSON().loadShelf()
		self.parseArgs()
		if checkMode:
			self.checkMode()
                   
                                
	def parseArgs(self):
		# call updateArgs() with our formatted argv to create the self.args object
		if (sys.argv[2]):
			exec "self.args = updateArgs(%s')" % (sys.argv[2][1:].replace('&', "',").replace('=', "='"))
		else:
			# updateArgs will turn the 'None' into None.
			# Don't simply define it as None because unquote_plus in updateArgs will throw an exception.
			# This is a pretty ugly solution
			self.args = updateArgs(mode = 'None', url = 'None', name = 'None')

	def checkMode(self):
		mode = self.args.mode
		if mode is None:
			UI().showMain()
		elif mode == 'Channels':
			UI().channels()
		elif mode == 'list_series':
			UI().json_list_series()
		elif mode == 'list_categories':
			UI().json_list_cat()
		elif mode == 'list_coll':
			UI().json_list_collection()
		elif mode == 'list_media':
			UI().json_list_media()
		elif mode == 'History':
			UI().json_History()
		elif mode == 'queue':
			UI().queue()
                elif mode == 'videoplay':
			UI().startVideo()
                else:
                        UI().Fail()

		

