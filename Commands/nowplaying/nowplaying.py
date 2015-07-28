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
import __main__, requests

info = { "names" : [ "nowplaying", "np", "lastfm" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		res = requests.get( "http://ws.audioscrobbler.com/2.0/user/" + message + "/recenttracks.xml?limit=1" )
		txt = __main__.fixHTMLChars( res.text )
		artist = __main__.strbetween( txt, "<artist>", "</artist>" )
		song = __main__.strbetween( txt, "<name>", "</name>" )
		album = __main__.strbetween( txt, "<album>", "</album>" )
		
		if album != "":
			albumtext = " from the album " + album
		else:
			albumtext = ""
		
		if "<track nowplaying=\"true\">" in txt:
			nowplaying = " is listening "
		else:
			nowplaying = " last listened "
		if song != "":
			__main__.sendMessage( message + nowplaying + "to " + song + " by " + artist + albumtext, channel )
		else:
			__main__.sendMessage( message + " was not found.", channel )
		return True
	except:
		return False
