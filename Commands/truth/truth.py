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
	message = message.strip()
	lineToSend = ""
	pathprefix = os.path.dirname( os.path.realpath( __file__ ) ) + os.sep
	if " f" in message:
		with open( pathprefix + "nick_female.txt", "r" ) as nick_femaletxt:
			lineToSend = random.choice( nick_femaletxt.readlines() )
		lineToSend = lineToSend.replace( "$2", message.partition( " " )[0] )
	elif " m" in message:
		with open( pathprefix + "nick_male.txt", "r" ) as nick_maletxt:
			lineToSend = random.choice( nick_maletxt.readlines() )
		lineToSend = lineToSend.replace( "$2", message.partition( " " )[0] )
	elif "m" in message:
		with open( pathprefix + "self_male.txt", "r" ) as self_maletxt:
			lineToSend = random.choice( self_maletxt.readlines() )
		lineToSend = lineToSend.replace( "$nick", user )
	elif "f" in message:
		with open( pathprefix + "self_female.txt", "r" ) as self_femaletxt:
			lineToSend = random.choice( self_femaletxt.readlines() )
		lineToSend = lineToSend.replace( "$nick", user )
	if lineToSend != "":
		__main__.sendMessage( lineToSend, channel )
	elif message == "":
		__main__.sendMessage( "Specify gender by using f or m. Example: truth m", channel )
	return True
