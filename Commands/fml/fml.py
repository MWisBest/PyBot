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
from pybotutils import fixHTMLChars, strbetween

info = { "names" : [ "fml", "fmylife" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	try:
		thefml = requests.get( "http://www.fmylife.com/random" ).text
		thefml = strbetween( thefml, "<p class=\"content\">", "</p>" )
		thefml = strbetween( thefml, ">", "</a>" )
		thefml = fixHTMLChars( thefml )
		if thefml == "":
			thefml = "Today, PyBot couldn't find an FML. FML"
		__main__.sendMessage( thefml, recvfrom )
		return True
	except:
		return False
