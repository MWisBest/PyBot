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
from pybotutils import fixHTMLChars

info = { "names" : [ "haveibeenpwned", "pwned", "hacked" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	try:
		txt = requests.get( "https://haveibeenpwned.com/api/breachedaccount/" + message ).text
		txt.replace( "[", "" ).replace( "]", "" ).replace( "\"", "" ).replace( ",", ", " )
		txt.replace('","',", ")
		if txt != "":
				__main__.sendMessage( message + " has been pwned on: " + txt, recvfrom )
		else:
			__main__.sendMessage( message + " seems to be safe!", recvfrom )
		return True
	except:
		return False
