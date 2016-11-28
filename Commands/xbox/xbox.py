###########################################################################
## PyBot                                                                 ##
## Copyright (C) 2015, Kyle Repinski                                     ##
## Copyright (C) 2015, Andres Preciado (Glitch)                          ##
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
from pybotutils import fixHTMLChars, strbetween

info = { "names" : [ "xbox", "xb" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	txt = requests.get( "https://live.xbox.com/en-US/Profile?gamertag=" + message ).text
	gamerscore = fixHTMLChars( strbetween( txt, "<div class=\"gamerscore\">", "</div>" ) )
	lastseen = fixHTMLChars( strbetween( txt, "<div class=\"presence\">", "</div>" ) )
	gamertag = fixHTMLChars( strbetween( txt, "<title>", "&#39;s Profile" ) ) #get proper case of gamertag
	if gamerscore != "":
		__main__.sendMessage( gamertag + " :: Status: " + lastseen + " :: Gamerscore: " + gamerscore, recvfrom )
	else:
		__main__.sendMessage( message + " was not found.", recvfrom )
	return True
