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
import __main__, os, random

info = { "names" : [ "truth" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		message = message.strip()
		if " f" in message:	
			lineToSend = random.choice( open( "Commands" + os.sep + "truth" + os.sep + "nick_female.txt", "r" ).readlines() )
			lineToSend = lineToSend.replace( "$2", message.partition( " " )[0] )
			__main__.sendMessage( lineToSend, channel )
		elif " m" in message:
			lineToSend = random.choice( open( "Commands" + os.sep + "truth" + os.sep + "nick_male.txt", "r" ).readlines() )
			lineToSend = lineToSend.replace( "$2", message.partition( " " )[0] )
			__main__.sendMessage( lineToSend, channel )
		elif "m" in message:
			lineToSend = random.choice( open( "Commands" + os.sep + "truth" + os.sep + "self_male.txt", "r" ).readlines() )
			lineToSend = lineToSend.replace( "$nick", user )
			__main__.sendMessage( lineToSend, channel )
		elif "f" in message:
			lineToSend = random.choice( open( "Commands" + os.sep + "truth" + os.sep + "self_female.txt", "r" ).readlines() )
			lineToSend = lineToSend.replace( "$nick", user )
			__main__.sendMessage( lineToSend, channel )
		if message == "":
			__main__.sendMessage( "Specify gender by using f or m. Example: truth m", channel )
		return True
	except:
		return False
