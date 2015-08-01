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

info = { "names" : [ "dinner", "supper" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		res = requests.get( "http://whatthefuckshouldimakefordinner.com/" )
		meal = __main__.fixHTMLChars( __main__.strbetween( res.text, "\" target=\"_blank\">", "</a></dt>" ) )
		url = __main__.fixHTMLChars( __main__.strbetween( res.text, "<dt><a href=\"", "\" target=\"_blank\">" ) )
		if meal != "":
			__main__.sendMessage( meal + " - " + url, channel )
		else:
			__main__.sendMessage( "You will starve!", channel )
		return True
	except:
		return False
