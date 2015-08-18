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
from pybotutils import strbetween

info = { "names" : [ "wotd", "wordoftheday" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	try:
		thewotd = strbetween( requests.get( "http://dictionary.reference.com/wordoftheday/" ).text, "<title>Get the Word of the Day - ", " |" )
		if thewotd == "":
			thewotd = "fail"
		__main__.sendMessage( "Word of the Day: " + thewotd, recvfrom )
		return True
	except:
		return False
