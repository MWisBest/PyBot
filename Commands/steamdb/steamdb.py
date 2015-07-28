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

info = { "names" : [ "steamcalc", "steamdb" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		res = requests.get( "https://steamdb.info/calculator/?player=" + message )
		playername = __main__.strbetween( res.text, "<title>", " · " )
		if playername != "Error":
			construct = playername + ": "
			table = __main__.strbetween( res.text, "<p><br>[list]", "[/list]</p>" )
			worth = __main__.strbetween( table, "[*][b]Worth:[/b] ", "</p>" )
			if worth != "":
				construct = construct + worth
			owned = __main__.strbetween( table, "<p>[*][b]Games owned:[/b] ", "</p>" )
			notplayed = __main__.strbetween( table, "<p>[*][b]Games not played:[/b] ", " [i](" )
			if owned != "" and notplayed != "":
				played = str( int( owned ) - int( notplayed ) )
				construct = construct + " | " + played + "/" + owned + " Games Played/Owned"
			__main__.sendMessage( construct, channel )
			return True
		else:
			__main__.sendMessage( message + " was not found.", channel )
			return False
		return False
	except:
		return False
