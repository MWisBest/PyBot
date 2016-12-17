###########################################################################
## PyBot                                                                 ##
## Copyright (C) 2015, Kyle Repinski                                     ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
###########################################################################
import __main__, re, threading, urllib.request####, requests ### see below urlopen stuff
from pybotutils import fixHTMLCharsAdvanced, strbetween

info = { "access" : 0, "packets" : [ "PRIVMSG" ], "apis" : [ "irc" ], "version" : 3 }

urlregex = re.compile( r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:[a-z]{2,13})(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:[a-z]{2,13})\b/?(?!@))))" )
linkdata = ""

def handle( packet ):
	try:
		if packet['rest'][0] == "#": # just parsing channel messages here
			user = strbetween( packet['host'], ":", "!" )
			if __main__.getAccessLevel( user ) < 0:
				return False # Get out of here banned loser!
			msgsplit = packet['rest'].split( " :", maxsplit=1 )
			channel = msgsplit[0]
			splitmessage = msgsplit[1].split( " " )
			titleFound = False
			for totest in splitmessage:
				if urlregex.search( totest ): # great, we found a URL!
					if not totest.startswith( "http" ): # We need this at the start for some damn reason
						totest = "http://" + totest
					try: # who knows what we got sent to
						tosend = ""
						if "imgur.com" in totest:
							tosend = imgur( totest )
						elif "youtube.com" in totest or "youtu.be" in totest:
							tosend = youtube( totest )
						else:
							tosend = normalLink( totest )
						tosend = tosend.replace( "google", "Google" ).replace( "Google", "\x02\x03" + "02,00G\x03" + "04,00o\x03" + "08,00o\x03" + "02,00g\x03" + "03,00l\x03" + "04,00e\x03\x02" )
						if tosend != "":
							__main__.sendMessage( tosend, channel )
							titleFound = True
					except:
						continue
			return titleFound
		return False
	except:
		return False


def fetchLinkDataThread( link ):
	global linkdata
	try:
		linkdata = urllib.request.urlopen( link ).read().decode( "utf-8", errors="replace" )
	except:
		linkdata = ""

def fetchLinkData( link, timeout=4.5 ):
	global linkdata
	try:
		linkdata = ""
		p = threading.Thread( target=fetchLinkDataThread, args=( link, ), daemon=True, name="[PyBot] URL Fetcher" )
		p.start()
		p.join( timeout )
		if p.is_alive():
			p.terminate()
			return ""
		return linkdata
	except:
		return ""


# Fetch the page's normal title.
def normalLink( link ):
	try:
		ourdata = fetchLinkData( link )
		if ourdata == "":
			return ""
		# Some places have decided 'hey lets use whitespaces in titles for no particular reason'; fuck them
		urlstitle = strbetween( ourdata, "<title>", "</title>" ).strip()
		if urlstitle != "":
			return "\x02URL:\x02 " + fixHTMLCharsAdvanced( urlstitle )
		elif "<TITLE>" in ourdata:
			# fuckin pricks using caps can fuck off, seriously fuck them too
			urlstitle = strbetween( ourdata, "<TITLE>", "</TITLE>" ).strip() # see above
			if urlstitle != "":
				return "\x02URL:\x02 " + fixHTMLCharsAdvanced( urlstitle )
		return ""
	except:
		return ""

# Used as a 'goto'
class BreakoutException( Exception ):
	pass

# Custom processing: Imgur
def imgur( link ):
	try:
		# chop off prefix for now, so we get "imgur.com" instead of "i.imgur.com"
		imgurlink = link[link.find( "imgur.com" ):]
		
		# If it's this short, assume plain imgur page
		if len( imgurlink ) < 11:
			raise BreakoutException
		
		# If the link ends with a file extension, remove it.
		linkpart = imgurlink.rpartition( "." )
		if not linkpart[2].startswith( "com" ):
			imgurlink = linkpart[0]
		
		# If it's not a gallery link, try to make it one so we can get stats.
		if not "gallery" in imgurlink:
			if "account/favorites/" in imgurlink:
				imgurlink = imgurlink.replace( "account/favorites/", "" )
			linkpart = imgurlink.partition( "/" )
			imgurlink = linkpart[0] + "/gallery/" + linkpart[2]
		
		# gotta start with http for urlopen
		imgurlink = "http://" + imgurlink
		# fetch page
		ourdata = fetchLinkData( imgurlink, 3.75 )
		if ourdata == "":
			return ""
		
		# chop off excess area so we only search the relevant parts of the page
		# this makes us kind of vulnerable to page changes, but it really speeds things up, so it's a worthy compromise.
		# don't check if this is empty, we'll find that out later; speed priority is for the majority case: a proper gallery post.
		tosearch = strbetween( ourdata, "widgetFactory.mergeConfig('gallery',", "</script>" )
		
		ups = strbetween( tosearch, ",\"ups\":", ",\"" )
		downs = strbetween( tosearch, ",\"downs\":", ",\"" )
		if ups == "" or downs == "":
			raise BreakoutException
		# try and get points.
		#points = format( int( strbetween( tosearch, ",\"points\":", ",\"" ) ), "," )
		# If we can't, just gtfo
		#if points == "":
		#	raise BreakoutException
		
		# try and get views.
		views = format( int( strbetween( tosearch, ",\"views\":", ",\"" ) ), "," )
		# again, if we can't, just gtfo
		if views == "":
			raise BreakoutException
		
		# NOTE: This gets something that does not match the actual title...
		## try and get 'official' title.
		##title = fixHTMLCharsAdvanced( strbetween( tosearch, ",\"title\":\"", "\",\"" ) )
		# INSTEAD: Grab what the browser uses.
		title = fixHTMLCharsAdvanced( strbetween( ourdata, "<meta property=\"og:title\" content=\"", "\"/>" ) )
		
		
		# and again, if we can't, just gtfo
		if title == "":
			raise BreakoutException
		
		
		return "\x02\x03" + "09,01Imgur\x03:\x02 \"" + title + "\" | " + ups + "U/" + downs + "D | " + views + " views"
	except: # Handle it like a normal link?
		return normalLink( link )

def youtube( link ):
	try:
		# Preserve initial link var for BreakoutException
		youtubelink = link
		
		ourdata = fetchLinkData( youtubelink, 3.75 )
		
		title = fixHTMLCharsAdvanced( strbetween( ourdata, "<meta itemprop=\"name\" content=\"", "\">" ) )
		
		views = format( int( strbetween( ourdata, "<meta itemprop=\"interactionCount\" content=\"", "\">" ) ), "," )
		if views == "":
			raise BreakoutException
		
		return "\x02\x03" + "01,00You\x03" + "00,04Tube\x03:\x02 \"" + title + "\"" + " | Views: " + views
	except: # Handle it like a normal link?
		return normalLink( link )
