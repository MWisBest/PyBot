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

info = { "names" : [ "dinner", "supper" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	txt = requests.get( "http://whatthefuckshouldimakefordinner.com/" ).text
	meal = fixHTMLChars( strbetween( txt, "\" target=\"_blank\">", "</a></dt>" ) )
	url = fixHTMLChars( strbetween( txt, "<dt><a href=\"", "\" target=\"_blank\">" ) )
	if meal != "" and url != "":
		__main__.sendMessage( meal + " - " + url, recvfrom )
	else:
		__main__.sendMessage( "You will starve!", recvfrom )
	return True
