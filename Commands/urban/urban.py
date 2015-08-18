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
from pybotutils import fixHTMLCharsAdvanced, googlshort, strbetween

info = { "names" : [ "urban", "ud", "rurban" ], "access" : 0, "version" : 2 }

def command( command, message, user, recvfrom ):
	try:
		link = "http://www.urbandictionary.com/"
		if command != "rurban":
			link += "define.php?term=" + message
		else:
			link += "random.php"
		txt = requests.get( link ).text
		definition = fixHTMLCharsAdvanced( strbetween( txt, "<div class='meaning'>\n", "\n</div>" ) )
		word = fixHTMLCharsAdvanced( strbetween( txt, "<title>Urban Dictionary: ", "</title>" ) )
		if definition != "" and word != "":
			toSend = word + ": " + definition
			if len( toSend ) >= 370: # This is roughly the longest message I've been able to send.
				shortLink = googlshort( "http://www.urbandictionary.com/define.php?term=" + word ) # Get a short link here in order to send as much as possible
				toCutOff = len( shortLink ) # Get the length of said link to make room for it
				toSend = toSend[0:(366-toCutOff)] # Using 436 here to allow room for "... " of course
				toSend = toSend.rpartition( " " )[0] # In order to make sure it doesn't cut off in the middle of a word
				toSend += "... " + shortLink # Finally finishing it off
			__main__.sendMessage( toSend, recvfrom )
			return True
		else:
			if "<i>" + message + "</i> isn't defined.<br/>Can you define it?" in txt:
				__main__.sendMessage( message + " isn't defined.", recvfrom )
				return True
			else:
				__main__.sendMessage( "There was a problem. Fix your shit.", recvfrom )
				return False
		return False
	except:
		return False
