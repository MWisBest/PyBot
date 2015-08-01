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

info = { "names" : [ "zipcode", "zipinfo", "zip" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		res = requests.get( "http://www.zip-info.com/cgi-local/zipsrch.exe?ac=ac&tz=tz&zip=" + message + "&Go=Go" )
		txt = __main__.fixHTMLChars( res.text )
		city = __main__.strbetween( txt, "</th></tr><tr><td align=center>", "</font>" )
		state = __main__.strbetween( txt, "</font></td><td align=center>", "</font></td><td align=center>" )
		acode = __main__.strbetween( txt, "<td align=center>" + message + "</font></td><td align=center>", "</font>" )
		timezone = __main__.strbetween( txt, acode + "</font></td><td align=center>", "</font></td><td align=center>Yes</font></td></tr></table>" )

		if zip != "":
			__main__.sendMessage( "Zip: " + message + " | City: " + city + " | State: " + state + " | Area Code: " + acode + " | Time Zone: " + timezone, channel )
		else:
			__main__.sendMessage( message + " was not found.", channel )
		return True
	except:
		return False
