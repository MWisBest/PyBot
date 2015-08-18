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
import __main__, time
from pybotutils import strbetween

info = { "access" : 0, "packets" : [ "PRIVMSG" ], "version" : 2 }

def handle( packet ):
	try:
		if packet['rest'][0] != "#": # just parsing PM messages here
			message = packet['rest'].split( " :", maxsplit=1 )[1].strip()
			if message[0] != "\x01" and message[-1] != "\x01": # CTCPs tend to use this, derp
				return False
			user = strbetween( packet['host'], ":", "!" )
			if __main__.getAccessLevel( user ) < 0:
				return False # Get out of here banned loser!
			message = message[1:-1] # Just chop off the \x01s now
			toSend = ""
			if message == "VERSION":
				toSend = "NOTICE " + user + " :\x01VERSION PyBot " + __main__.pyBotVersion + ".\x01"
			elif message == "TIME":
				toSend = "NOTICE " + user + " :\x01TIME " + time.strftime( "%a %b %d %X" ) + "\x01"
			elif message.startswith( "PING " ):
				toSend = "NOTICE " + user + " :\x01" + message + "\x01"
			if toSend != "":
				__main__.sendPacket( __main__.makePacket( toSend ) )
				return True
		return False
	except:
		return False
