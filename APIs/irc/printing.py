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
import __main__

def sendprint( packet ):
	try:
		if packet['command'] == "PONG":
			return # Ingore PONGs
		if __main__.database['globals']['debug']:
			__main__.senddebugprint( packet['raw'], packet['timestamp'] )
		else:
			toprint = ""
			# Don't overwrite a part of packet
			# TODO: Just replace newlines etc; spaces are valid at the ends!
			packetrest = packet['rest'].rstrip()
			user = __main__.database['api']['ircsettings']['nick']
			if packet['command'] == "PRIVMSG":
				locMessage = packetrest.partition( " :" )
				if locMessage[0] in __main__.database['api']['ircsettings']['channels']: #channel message
					if not locMessage[2].startswith( "\x01ACTION" ):
						toprint = "[" + locMessage[0] + "] " + user + ": " + locMessage[2]
					else:
						toprint = "[" + locMessage[0] + "] *" + user + locMessage[2][7:-1]
				else: #PM
					if locMessage[2][0] != "\x01":
						toprint = ">" + locMessage[0] + "<: " + locMessage[2]
					else: #CTCP or ME
						if locMessage[2].startswith( "\x01ACTION" ): #ME
							toprint = ">" + locMessage[0] + "< *" + user + locMessage[2][7:-1]
						else:
							pass #TODO
							#toprint = "Received a CTCP " + locMessage[2][1:-1] + " from " + user
			elif packet['command'] == "PART":
				locMessage = packetrest.partition( " :" )
				toprint = "[" + locMessage[0] + "] " + user + " has left (Part: " + locMessage[2] + ")"
			elif packet['command'] == "JOIN":
				if packetrest[0] != "#": # HACK: Some networks send an extra character here, and some don't...
					packetrest = packetrest[1:]
				toprint = "[" + packetrest + "] " + user + " has joined"
			elif packet['command'] == "QUIT":
				toprint = user + " has quit (Quit: " + packetrest[1:] + ")"
			elif packet['command'] == "NICK":
				toprint = user + " is now known as " + packetrest
			elif packet['command'] == "TOPIC":
				locTopic = packetrest.partition( " :" )
				toprint = "[" + locTopic[0] + "] " + user + " has changed the topic to: " + locTopic[2]
			if toprint != "":
				__main__.sendregularprint( toprint, packet['timestamp'] )
	except: # Really. REALLY.
		__main__.warnprint( "Last sendprint had an exception. Caught, but yeah. Something's wrong on your end." )


def recvprint( packet ):
	try:
		if packet['command'] == "PING":
			return # Ingore PINGs
		if __main__.database['globals']['debug']:
			__main__.recvdebugprint( packet['raw'].rstrip(), packet['timestamp'] )
		else:
			toprint = ""
			# Don't overwrite a part of packet
			# TODO: Just replace newlines etc; spaces are valid at the ends!
			packetrest = packet['rest'].rstrip()
			# We use the user in just about everything here, just get it ahead of time and save some lines of code.
			user = packet['host'].partition( "!" )[0][1:]
			if packet['command'] == "PRIVMSG": # ledeledele
				locMessage = packetrest.partition( " :" )
				if locMessage[0] in __main__.database['api']['ircsettings']['channels']: #channel message
					if not locMessage[2].startswith( "\x01ACTION" ):
						toprint = "[" + locMessage[0] + "] " + user + ": " + locMessage[2]
					else:
						toprint = "[" + locMessage[0] + "] *" + user + locMessage[2][7:-1]
				else: #PM
					if locMessage[2][0] != "\x01":
						toprint = "*" + user + "*: " + locMessage[2]
					else: #CTCP or ME
						if locMessage[2].startswith( "\x01ACTION" ): #ME
							toprint = "*" + user + "* *" + locMessage[2][7:-1]
						else:
							toprint = "Received a CTCP " + locMessage[2][1:-1] + " from " + user
			elif packet['command'] == "PART": # Format PARTs nicely
				locMessage = packetrest.partition( " :" )
				if user != __main__.database['api']['ircsettings']['nick']: # We get our own PARTs, but let sendprint do them.
					toprint = "[" + locMessage[0] + "] " + user + " has left (" + locMessage[2] + ")"
			elif packet['command'] == "JOIN": # Format JOINs nicely too
				if user != __main__.database['api']['ircsettings']['nick']: # We get our own JOINs, but let sendprint do them.
					if packetrest[0] != "#": # HACK: Some networks send an extra character here, and some don't...
						packetrest = packetrest[1:]
					userhost = packet['host'].partition( "!" )[2]
					toprint = "[" + packetrest + "] " + user + " (" + userhost + ") has joined"
			elif packet['command'] == "QUIT":
				toprint = user + " has quit (" + packetrest[1:] + ")"
			elif packet['command'] == "NICK":
				if packetrest != __main__.database['api']['ircsettings']['nick']: # We also get our own NICKs, however it's the packetrest part (newnick) here
					toprint = user + " is now known as " + packetrest
			elif packet['command'] == "KICK":
				locMessage = list( packetrest.partition( " :" ) )
				locMessage[1] = locMessage[0].partition( " " )
				toprint = user + " has kicked " + locMessage[1][2] + " from " + locMessage[1][0] + "(" + locMessage[2] + ")"
			elif packet['command'] == "TOPIC":
				if user != __main__.database['api']['ircsettings']['nick']: # Jeez, we even get our own TOPICs!
					locTopic = packetrest.partition( " :" )
					toprint = "[" + locTopic[0] + "] " + user + " has changed the topic to: " + locTopic[2]
			elif packet['command'] == "MODE":
				modemap = {
					"v" : { "name" : "voice", "priority" : 1 },
					"h" : { "name" : "half-operator", "priority" : 2 },
					"o" : { "name" : "operator", "priority" : 3 },
					"a" : { "name" : "protected", "priority" : 4 },
					"q" : { "name" : "founder", "priority" : 5 } }
				chanRest = packetrest.partition( " " )
				if chanRest[2][0] == "+":
					givetext = " gives "
					tofromtext = " to "
				else:
					givetext = " removes "
					tofromtext = " from "
				modeassigned = pybotutils.strbetween( chanRest[2], chanRest[2][0], " " )
				if len( modeassigned ) == 1: # Only one mode assigned, easy-peasy
					# We could have less code here if we just axe this ==1 part and
					# use the bottom looping version (which would still work fine here),
					# however one assignment is by far the most common codepath, so this
					# is faster most of the time.
					if modeassigned in modemap:
						usergivento = chanRest[2].rpartition( " " )[2]
						toprint = "[" + chanRest[0] + "] " + user + givetext + modemap[modeassigned]['name'] + " status" + tofromtext + usergivento
				else:
					if len( modeassigned ) <= len( modemap ): # Make sure we don't have more modes than we understand
						modesassigned = []
						i = len( modeassigned )
						while i > 0:
							i = i - 1
							modesassigned.append( modeassigned[i] )
						modesassigned.reverse() # I'm too lazy to reverse the loop above. lel.
						usergivento = chanRest[2].rpartition( " " )[2]
						for mode in modesassigned:
							if mode in modemap:
								toprint = "[" + chanRest[0] + "] " + user + givetext + modemap[mode]['name'] + " status" + tofromtext + usergivento
								recvregularprint( toprint, packet['timestamp'] )
						toprint = ""
			if toprint != "":
				__main__.recvregularprint( toprint, packet['timestamp'] )
	except: # Really. REALLY.
		#print( "Unexpected error: ", sys.exc_info()[0] )
		__main__.warnprint( "Last recvprint had an exception. Caught, but yeah. Something's wrong on your end." )
