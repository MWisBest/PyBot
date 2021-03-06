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
from pybotutils import fixHTMLCharsAdvanced, strbetween

info = { "names" : [ "insult" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	insult = fixHTMLCharsAdvanced( strbetween( requests.get( "http://www.randominsults.net/" ).text, "<strong><i>", "</i></strong>" ) )
	if insult != "":
		__main__.sendMessage( message + ": " + insult, recvfrom )
	else:
		__main__.sendMessage( "There was a problem. Fix your shit.", recvfrom )
	return True
