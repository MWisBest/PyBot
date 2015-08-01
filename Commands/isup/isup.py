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

info = { "names" : [ "isitdown", "isup" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		res = requests.get( "http://isup.me/" + message )
		status = __main__.fixHTMLChars( __main__.strbetween( res.text, "<div id=\"container\">", "<p>" ) ).strip()
		#status = __main__.fixHTMLChars( __main__.strbetween( res.text, "target=\"_blank\">", "</div>" ) ).replace( "</a>", "" )
		href = __main__.strbetween( status, "<a href=\"", "class=\"domain\">" )
		status = status.replace( "<a href=\"" + href + "class=\"domain\">", "" )
		status = status.replace( "</a>", "" ).replace( "</span>", "" ).replace( "  ", " " )
		if status != "":
			__main__.sendMessage( status, channel )
		else:
			__main__.sendMessage( "Something went wrong.", channel )
		return True
	except:
		return False
