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
import socket, sys, os, pickle, threading, random, html.parser, platform, time, io, base64, importlib

# Version check.
pyversion = platform.python_version_tuple()
if int( pyversion[0] ) < 3:
	print( "Anything lower than Python 3.4 isn't supported, UPGRADE OR DIE." )
	exit()
elif int( pyversion[0] ) == 3 and int( pyversion[1] ) < 4:
	print( "PyBot requires Python 3.4 or higher. Sorry!" )
	exit()


## This is used pretty much everywhere you can think of, so I'll just put it up top. ##
# TODO: Switch everything to use pybotutils
def strbetween( s, first, last ):
	try:
		start = s.index( first ) + len( first )
		return s[start:s.index( last, start )]
	except:
		return ""


#####################
## MODULAR IMPORTS ##
# This is a pretty clever way to make the bot modular/extensible. :)
def importFolder( foldername, dictaddedto="" ):
	folderpath = os.path.dirname( os.path.realpath( __file__ ) ) + os.sep + foldername + os.sep
	sys.path.insert( 1, folderpath )
	for modulefolder in os.listdir( folderpath ):
		if os.path.isdir( folderpath + modulefolder + os.sep ):
			try:
				exec( "global " + modulefolder + "\nimport " + modulefolder ) # as much as I hate exec, i cant find another way to do this!
				if dictaddedto != "":
					exec( "global " + dictaddedto + "dict\n" + dictaddedto + "dict[modulefolder] = " + modulefolder + ".info" )
			except:
				print( "Failed to import: " + modulefolder )

# Current required modules are:
# - colorama
# - requests
# - termcolor
# The idea is to distribute them with the bot directly to avoid the user having to install them with pip,
# however should any author request their module to be removed and require users to install with pip I will respect that.
importFolder( "Modules" )

# Utilities is meant to distinguish between a 'homegrown' module and a module written by somebody else.
importFolder( "Utilities" )

# Commands are run on request, e.x. "!fml"
commanddict = {}
importFolder( "Commands", dictaddedto="command" )

# Handlers take every raw packet and do whatever they want with it.
handlerdict = {}
importFolder( "Handlers", dictaddedto="handler" )
## MODULAR IMPORTS ##
#####################


##########################
## CONSOLE OUTPUT SETUP ##
colorama.init()

senddebugprint = lambda x, y: termcolor.cprint( "[" + time.strftime( "%H:%M:%S", time.localtime( y ) ) + " ->>] " + x, "cyan" )
recvdebugprint = lambda x, y: termcolor.cprint( "[" + time.strftime( "%H:%M:%S", time.localtime( y ) ) + " <<-] " + x, "green" )
sendregularprint = lambda x, y: termcolor.cprint( "[" + time.strftime( "%H:%M:%S", time.localtime( y ) ) + "] " + x, "cyan" )
recvregularprint = lambda x, y: termcolor.cprint( "[" + time.strftime( "%H:%M:%S", time.localtime( y ) ) + "] " + x, "green" )
errorprint = lambda x: termcolor.cprint( x.replace( "\r", "" ).replace( "\n", "" ), "red", attrs=['bold'] )
warnprint = lambda x: termcolor.cprint( x.replace( "\r", "" ).replace( "\n", "" ), "yellow", attrs=['bold'] )
## CONSOLE OUTPUT SETUP ##
##########################


#############
## GLOBALS ##
# TODO: Stop using the global scope so much...
database = {}
# Allow custom database filename.
# This allows one PyBot install to run on multiple servers (needs separate db for each).
if len( sys.argv ) >= 2 and sys.argv[1].startswith( "pybot" ) and sys.argv[1].endswith( "pickle" ):
	databaseName = sys.argv[1]
else:
	databaseName = "pybot.pickle"
rebooted = 0
loggedIn = False
chanJoined = False
chanJoinDelay = 0
away = False
slowConnect = True
pyBotVersion = "Beta"
eightBallResponses = [ "It is certain.", "Not a chance!", "Unclear. Try asking again?", "I think you already know the answer to that!", "Stop asking me questions! :@", "It's possible.", "Doubtful." ]
CAPs = { "server" : [], "client" : ( "sasl" ), "enabled" : [], "actuallyUseThisCrap" : True }
## GLOBALS ##
#############


##############################################################
## CUSTOM PICKLE CLASS TO PREVENT UNPICKLING ARBITRARY CODE ##
safe_builtins = {
	'range',
	'complex',
	'set',
	'frozenset',
	'slice',
}

class PyBotUnpickler( pickle.Unpickler ):
	def find_class( self, module, name ):
		# Only allow safe classes from builtins.
		if module == "builtins" and name in safe_builtins:
			return getattr( builtins, name )
		# Forbid everything else
		raise pickle.UnpicklingError( "global '%s.%s' is forbidden" % ( module, name ) )
## CUSTOM PICKLE CLASS TO PREVENT UNPICKLING ARBITRARY CODE ##
##############################################################

##################################################
## FUNCTIONS TO SAVE AND LOAD THE DATABASE FILE ##
def loadDatabase():
	global database, databaseName
	with open( databaseName, "rb" ) as pybotfile:
		with io.BytesIO( pybotfile.read() ) as pybotfilebytes:
			database = ( PyBotUnpickler( pybotfilebytes ) ).load()

def saveDatabase():
	global database, databaseName
	with open( databaseName, "wb" ) as pybotfile:
		pickle.dump( database, pybotfile, protocol=pickle.HIGHEST_PROTOCOL )
## FUNCTIONS TO SAVE AND LOAD THE DATABASE FILE ##
##################################################

###############################
## Load up the database ASAP ##
try:
	loadDatabase()
	if database['version'] == 1: # Upgrade to version 2
		# Version 2 changes:
		# - ['botInfo']['channel'] is replaced with ['botInfo']['channels']
		#     We now support the bot being in multiple channels at the same time!
		database['botInfo']['channels'] = []
		database['botInfo']['channels'].append( database['botInfo']['channel'] )
		del database['botInfo']['channel']
		database['version'] = 2
		saveDatabase()
	if database['version'] == 2:
		# Version 3 changes:
		# - ['botInfo']['password'] is now stored in base85 format rather than plaintext.
		#     This doesn't provide any real security, but it prevents some noob from
		#     just opening the database in a text editor and seeing the password.
		database['botInfo']['password'] = base64.b85encode( database['botInfo']['password'].encode( "utf-8" ), pad=True )
		database['version'] = 3
		saveDatabase()
except IOError: # Create pybot.pickle on first start
	database = { "accessList" : {}, "botInfo" : { "nick" : "", "password" : base64.b85encode( "".encode( "utf-8" ), pad=True ), "network" : "", "port" : 0, "channels" : [] }, "globals" : { "cc" : "!", "reverse" : False, "debug" : False }, "version" : 3 }
	print( colorama.Fore.CYAN )
	database['botInfo']['network'] = input( "Please enter the address of the IRC network you want to connect to.\n" )
	database['botInfo']['port'] = int( input( "Please enter the port while you're at it!\n" ) )
	database['botInfo']['nick'] = input( "Please enter a valid (NO STUPID SYMBOLS) IRC nick for your bot.\n" ).replace( " ", "_" ).replace( ".", "_" ).replace( ",", "_" )
	database['botInfo']['password'] = base64.b85encode( ( input( "Please enter your bot's NickServ password if required, otherwise leave this blank.\n" ) ).encode( "utf-8" ), pad=True )
	database['botInfo']['channels'] = [ input( "Please enter the initial channel that your bot will be joining.\n" ) ]
	devel = input( "Please enter your Nick so the bot will listen to you.\n" )
	database['accessList'][devel] = 4
	print( colorama.Fore.WHITE )
	saveDatabase()
## Load up the database ASAP ##
###############################


###########################
## FORMAT CONSOLE OUTPUT ##
def sendprint( packet ):
	try:
		if packet['command'] == "PONG":
			return # Ingore PONGs
		if database['globals']['debug']:
			senddebugprint( packet['raw'], packet['timestamp'] )
		else:
			toprint = ""
			# Don't overwrite a part of packet
			# TODO: Just replace newlines etc; spaces are valid at the ends!
			packetrest = packet['rest'].rstrip()
			user = database['botInfo']['nick']
			if packet['command'] == "PRIVMSG":
				locMessage = packetrest.partition( " :" )
				if locMessage[0] in database['botInfo']['channels']: #channel message
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
				sendregularprint( toprint, packet['timestamp'] )
	except: # Really. REALLY.
		warnprint( "Last sendprint had an exception. Caught, but yeah. Something's wrong on your end." )

def recvprint( packet ):
	try:
		if packet['command'] == "PING":
			return # Ingore PINGs
		if database['globals']['debug']:
			recvdebugprint( packet['raw'].rstrip(), packet['timestamp'] )
		else:
			toprint = ""
			# Don't overwrite a part of packet
			# TODO: Just replace newlines etc; spaces are valid at the ends!
			packetrest = packet['rest'].rstrip()
			# We use the user in just about everything here, just get it ahead of time and save some lines of code.
			user = packet['host'].partition( "!" )[0][1:]
			if packet['command'] == "PRIVMSG": # ledeledele
				locMessage = packetrest.partition( " :" )
				if locMessage[0] in database['botInfo']['channels']: #channel message
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
				if user != database['botInfo']['nick']: # We get our own PARTs, but let sendprint do them.
					toprint = "[" + locMessage[0] + "] " + user + " has left (" + locMessage[2] + ")"
			elif packet['command'] == "JOIN": # Format JOINs nicely too
				if user != database['botInfo']['nick']: # We get our own JOINs, but let sendprint do them.
					if packetrest[0] != "#": # HACK: Some networks send an extra character here, and some don't...
						packetrest = packetrest[1:]
					userhost = packet['host'].partition( "!" )[2]
					toprint = "[" + packetrest + "] " + user + " (" + userhost + ") has joined"
			elif packet['command'] == "QUIT":
				toprint = user + " has quit (" + packetrest[1:] + ")"
			elif packet['command'] == "NICK":
				if packetrest != database['botInfo']['nick']: # We also get our own NICKs, however it's the packetrest part (newnick) here
					toprint = user + " is now known as " + packetrest
			elif packet['command'] == "KICK":
				locMessage = list( packetrest.partition( " :" ) )
				locMessage[1] = locMessage[0].partition( " " )
				toprint = user + " has kicked " + locMessage[1][2] + " from " + locMessage[1][0] + "(" + locMessage[2] + ")"
			elif packet['command'] == "TOPIC":
				if user != database['botInfo']['nick']: # Jeez, we even get our own TOPICs!
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
				modeassigned = strbetween( chanRest[2], chanRest[2][0], " " )
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
				recvregularprint( toprint, packet['timestamp'] )
	except: # Really. REALLY.
		#print( "Unexpected error: ", sys.exc_info()[0] )
		warnprint( "Last recvprint had an exception. Caught, but yeah. Something's wrong on your end." )
## FORMAT CONSOLE OUTPUT ##
###########################


###########
## UTILS ##
# TODO: Move some of these to pybotutils
def makePacket( data, inbound=False ):
	packet = { "host" : "", "command" : "", "rest" : "", "raw" : data, "timestamp" : 0 }
	data = data.replace( "\r", "" ).replace( "\n", "" )
	if inbound:
		datalist = data.split( ' ', maxsplit=2 )
		packet['timestamp'] = time.time()
	else:
		datalist = data.split( ' ', maxsplit=1 )
	# In the event we go to the elif, avoid running len a second time.
	listlength = len( datalist )
	if listlength == 3:
		# Generally the case for most received packets.
		packet['host'] = datalist[0]
		packet['command'] = datalist[1]
		packet['rest'] = datalist[2]
	elif listlength == 2:
		# Most outbound packets, as well as PING inbound packets.
		packet['command'] = datalist[0]
		packet['rest'] = datalist[1]
	# only other possibility is listlength is 1.
	# in that case we leave everything blank and let stuff parse the raw packet only.
	#if database['globals']['debug']:
		#print( str( packet ) )
	return packet

def sendPacket( packet, forceDebugPrint=False ):
	global sock
	sent = True
	# TODO: Fix this crap
	bytespacket = ( packet['raw'] + "\r\n" ).encode( errors="ignore" )
	length = len( bytespacket )
	amountSent = 0
	while length != amountSent:
		try:
			amountSent = amountSent + sock.send( bytespacket )
		except:
			sent = False
	# Set the packet's timestamp to the time when we actually finished sending it.
	packet['timestamp'] = time.time()
	if forceDebugPrint:
		if database['globals']['debug']: # Check this in here rather than with an and up above, this way we don't print debug stuff when debug is off
			senddebugprint( packet['raw'], packet['timestamp'] )
	else:
		sendprint( packet )
	if not sent:
		warnprint( "Last packet did not send successfully. If this persists, check your connection and/or restart the bot." )

def reboot():
	global sock, pyBotVersion
	sendPacket( makePacket( "QUIT :PyBot " + pyBotVersion + ". (Rebooting)" ) )
	sock.shutdown( socket.SHUT_RDWR )
	sock.close()
	python = sys.executable
	os.execl( python, python, * sys.argv )

def reconnect():
	global rebooted
	rebooted = 1
	init()

def die():
	global sock, pyBotVersion
	sendPacket( makePacket( "QUIT :PyBot " + pyBotVersion + ". (Shutting Down)" ) )
	sock.shutdown( socket.SHUT_RDWR )
	sock.close()
	exit()

def fixHTMLChars( toFix ):
	h = html.parser.HTMLParser()
	toFix = toFix.replace( "&nbsp;", " " ) # Rather than have a weird character, use a regular fkin space
	return h.unescape( toFix )

def fixHTMLCharsAdvanced( toFix ):
	h = html.parser.HTMLParser()
	toFix = toFix.replace( "&nbsp;", " " ) # Rather than have a weird character, use a regular fkin space
	toFix = h.unescape( toFix )
	# replace linebreaks with spaces
	toFix = toFix.replace( "<br/>", " " ).replace( "\n", " " ).replace( "\r", " " )
	if "<a href=" in toFix:
		toFix = toFix.replace( "</a>", "" )
		while "<a href=" in toFix:
			toReplace = strbetween( toFix, "<a href=", ">" )
			toFix = toFix.replace( "<a href=" + toReplace + ">", "" )
	while "  " in toFix: # We don't want two or more spaces used for breaks
		toFix = toFix.replace( "  ", " " )
	return toFix
## UTILS ##
###########


#########################
## MAIN PACKET HANDLER ##
def handlePackets( packet ):
	global database
	ranThroughHandler = False # HACK: Call handlers once and only once!
	if packet['command'] == "PRIVMSG":
		channelmsg = ((packet['rest'])[0] == "#")
		if True: #" PRIVMSG " + channel + " :" in packet: # Channel Message
			privmsginfo = packet['rest'].split( " :", maxsplit=1 )
			user = strbetween( packet['host'], ":", "!" )
			if channelmsg:
				locfrom = privmsginfo[0]
			else:
				locfrom = user
			# Some commands (such as hash) NEED to parse extra spaces at the end of the message.
			# TODO: Find a more elegant way that works for everybody.
			message = privmsginfo[1].lstrip()
			myAccess = getAccessLevel( user )
			if len( message ) > 1 and message[0] == database['globals']['cc'] and myAccess >= 0:
				message = message[1:]
				args = list( message.partition( " " ) )
				args[0] = args[0].lower()
				#args = tuple( args )
				if args[0] == "say":
					sendMessage( args[2], locfrom, theuser=user, bypass=False )
				elif args[0] == "me":
					sendMe( args[2], locfrom )
				elif args[0] == "sayto":
					sendMessage( args[2].partition( " " )[2], args[2].partition( " " )[0], theuser=user, bypass=False )
				elif args[0] == "meto":
					sendMe( args[2].partition( " " )[2], args[2].partition( " " )[0] )
				elif args[0] == "ono":
					sendMessage( "\u270B", locfrom )
				elif args[0] == "die" and myAccess >= 3:
					die()
				elif args[0] in ["8", "8b", "8ball"]:
					handleEightBall( user, locfrom )
				elif args[0] == "ban" and myAccess >= 2:
					banUser( args[2], user, locfrom )
				elif args[0] == "unban" and myAccess >= 2:
					unbanUser( args[2], locfrom )
				elif args[0] == "kick" and myAccess >= 2:
					kickUser( args[2], user, locfrom )
				elif args[0] == "away" and myAccess >= 2:
					toggleAway( args[2], locfrom )
				elif args[0] == "reboot" and myAccess >= 3:
					reboot()
				elif args[0] == "add" and myAccess >= 3:
					addUser( args[2], locfrom, user )
				elif args[0] == "remove" and myAccess >= 3:
					removeUser( args[2], locfrom, user )
				elif args[0] == "acclist":
					listUsers( locfrom )
				elif args[0] == "debug" and myAccess >= 3:
					changeDebug( args[2], locfrom )
				elif args[0] == "reverse" and myAccess >= 2:
					toggleReverse( args[2], locfrom )
				elif args[0] == "bot" and myAccess >= 2:
					editBotInfo( args[2], locfrom )
				elif args[0] == "cc" and myAccess >= 2:
					commandChar( args[2], locfrom )
				elif args[0] == "packet" and myAccess >= 3:
					sendPacket( makePacket( args[2] ) )
				elif args[0] in ["channel", "channels"] and myAccess >= 3:
					changeChannel( args[2], locfrom )
				elif args[0] == "ping":
					sendMessage( "pong!", locfrom )
				elif args[0] == "pong":
					sendMessage( "FUCK YOU! ONLY I PONG!", locfrom )
				elif args[0] in ["import", "reimport"] and myAccess >= 4:
					reimportModule( args[2], locfrom )
				elif args[0] == "exec" and myAccess >= 4 and database['globals']['debug']:
					try:
						exec( args[2] )
					except: # who knows what the hell we're trying here, chances are somebody is fucking up if they even bother trying to use exec in the first place
						print( "Unexpected error: " + str( sys.exc_info() ) )
						sendMessage( "Yeah, you had an issue in there somewhere.", locfrom )
# From this point and beyond, all commands should be the external ones
				else: # see if it's in the command dict
					try: # who knows what kind of shit people have in their commands folder
						commandkeys = commanddict.keys()
						for key in commandkeys:
							try: # so we can continue through the loop on fuck ups
								if args[0] in commanddict[key]['names'] and myAccess >= commanddict[key]['access']:
									if commanddict[key]['version'] == 1:
										eval( key + ".command( args[2], user, locfrom )" ) # I hate exec, but this should be secure enough
									elif commanddict[key]['version'] == 2:
										# Version 2 adds sending the command used to the command too.
										# This allows a merge of 'rurban' and 'urban' for example.
										eval( key + ".command( args[0], args[2], user, locfrom )" )
									return # We don't need to keep iterating if we got what we need.
							except: # fix your shit
								continue # lets just keep going then.
					except: # like i said.
						return # get out of here.
			elif not ranThroughHandler: # Unfortunately, there exists the possibility that an external handler wants access at this too. Run through them if this wasn't a cc message.
				externalHandlers( packet )
				ranThroughHandler = True
		elif not ranThroughHandler: # Try all the external handlers then.
			externalHandlers( packet )
			ranThroughHandler = True
	elif packet['command'] == "PING":
		# Reply with PONG!
		# Keep this at the bottom; response time for this is lowest priority
		sendPong( packet )

def externalHandlers( packet ):
	try: # who knows what's gonna happen in this.
		handlerkeys = handlerdict.keys()
		for key in handlerkeys:
			try: # so we can continue through the loop on fuck ups
				eval( key + ".handle( packet )" ) # I hate exec, but this is all I can do dammit.
			except: # fix your shit
				continue # lets just keep going then.
	except: # oh fuck this.
		return # bye!
## MAIN PACKET HANDLER ##
#########################


#################
## SEND STUFFS ##
def sendMessage( message, whereto, theuser=None, bypass=True ):
	global database
	if database['globals']['reverse']:
		message = message[::-1]
	sendPacket( makePacket( "PRIVMSG " + whereto + " :" + message ) )

def sendPong( pingpacket ): # PING reply
	pingpacket['command'] = "PONG"
	pingpacket['raw'] = pingpacket['raw'].replace( "PING", "PONG" ).replace( "\r", "" ).replace( "\n", "" )
	sendPacket( pingpacket )

def sendMe( message, whereto ):
	global database
	if database['globals']['reverse']:
		message = message[::-1]
	sendPacket( makePacket( "PRIVMSG " + whereto + " :\x01ACTION " + message + "\x01" ) )
## SEND STUFFS ##
#################


##################
## BOTDEV STUFF ##
def reimportModule( args, recvfrom ):
	global commanddict, handlerdict
	try:
		# defining this function locally avoids a ton of code duplication.
		def doImport( type, name, reimport=True ):
			code = "global " + type + "dict, " + name + "\n"
			# Most likely case is reimport...
			if reimport:
				# ...in which case we'll need to importlib.reload.
				# Here's how importing PyBot's modular stuff (e.x. Commands, Handlers) works (at bootup):
				# 1. We add the relevant folder (in this case Commands) to sys.path like so:
				#    sys.path.insert( 1, os.path.dirname( os.path.realpath( __file__ ) ) + os.sep + "Commands" + os.sep )
				# 2. We take the list of the folder names inside the Commands folder and run "import (foldername)" for each of them.
				#    That works like this:
				#        each of those folders in the Commands folder has two files: __init__.py, and (foldername).py
				#        the __init__.py contains only this: "from .(foldername) import *"
				# What happens though is we actually end up with TWO modules: foldername (--> __init__.py), and foldername.foldername (--> foldername.py)
				# Problem? Doing "foldername = importlib.reload( foldername )" doesn't reload the 'foldername.foldername' module, which is what we actually want to reload!!
				# Fortunately, we can take care of that ourselves by first doing "foldername.foldername = importlib.reload( foldername.foldername )" and THEN reload foldername.
				code = code + name + "." + name + " = importlib.reload( " + name + "." + name + " )\n"
				code = code + name + " = importlib.reload( " + name + " )\n"
			else:
				# ...if it's NOT a reimport, we can just use the regular import statement and we're good to go.
				code = code + "import " + name + "\n"
			code = code + type + "dict[name] = " + name + ".info\n"
			exec( code )
		
		# TODO: If command/handler isn't provided, and the module is already in either commanddict or handlerdict, autodetermine 'args[0]'
		args = args.split( " " )
		if len( args ) >= 2 and len( args[1] ) >= 1:
			args[0] = args[0].lower()
			if args[0] in ["command", "handler"]:
				if args[1] in sys.modules:
					if args[1] in commanddict or args[1] in handlerdict:
						# Reimport already existing command/handler
						doImport( args[0], args[1] )
						sendMessage( "Reimported " + args[0] + ": " + args[1], recvfrom )
						return True
					else:
						# This else can only happen in one of two scenarios:
						# 1. The command or handler imported OK before, but adding its info dict to the command/handler dict failed.
						# 2. We have a name conflict, for example some dumbass tried to make a command named "sys"
						# If there's an args[2] containing "force" then we'll assume the person knows the problem was #1.
						# However, we won't ADVERTISE that we support using "force"; it should only be used by people who know how
						# reimportModule works, and if you know how it works you know you can use force in this situation.
						if len( args ) >= 3 and args[2].lower() == "force":
							doImport( args[0], args[1] )
							sendMessage( "FORCEFULLY reimported the \"" + args[1] + "\" module and added it as a " + args[0] + " despite it not previously being in the " + args[0] + "dict!", recvfrom )
							return True
						else:
							sendMessage( "Module \"" + args[1] + "\" is already imported but isn't in the " + args[0] + "dict! Aborting!", recvfrom )
							return False
				else:
					# If it's not an already loaded module, then do a standard import rather than a reimport.
					doImport( args[0], args[1], reimport=False )
					sendMessage( "Imported NEW " + args[0] + ": " + args[1], recvfrom )
					return True
	except:
		sendMessage( "Error occurred trying to import module!", recvfrom )
		return False
	sendMessage( "Usage: reimport [command/handler] [name]", recvfrom )
	return False

def changeDebug( message, recvfrom ):
	global database
	message = message.lower().strip()
	if message == "": # Toggle it in this case
		database['globals']['debug'] = not database['globals']['debug']
		if database['globals']['debug']:
			sendMessage( "Debugging: enabled.", recvfrom )
		else:
			sendMessage( "Debugging: disabled.", recvfrom )
		saveDatabase()
		return True
	elif message == "on" or message == "true":
		database['globals']['debug'] = True
		sendMessage( "Debugging: enabled.", recvfrom )
		saveDatabase()
		return True
	elif message == "off" or message == "false":
		database['globals']['debug'] = False
		sendMessage( "Debugging: disabled.", recvfrom )
		saveDatabase()
		return True
	sendMessage( "Usage: debug <on/true/off/false>", recvfrom )
	return False
## BOTDEV STUFF ##
##################


############################
## MISC BUILT-IN COMMANDS ##
def commandChar( args, recvfrom ):
	global database
	if len( args ) == 1:
		database['globals']['cc'] = args
		sendMessage( "Command character changed to: " + args, recvfrom )
		saveDatabase()
		return True
	sendMessage( "Usage: cc [X]", recvfrom )
	return False

def handleEightBall( theuser, recvfrom ):
	global eightBallResponses
	random.shuffle( eightBallResponses )
	sendMessage( theuser + ": " + random.choice( eightBallResponses ), recvfrom )

def toggleReverse( args, recvfrom ):
	global database
	args = args.lower().strip()
	# Flip it with empty args
	if args == "":
		database['globals']['reverse'] = not database['globals']['reverse']
		if database['globals']['reverse']:
			sendMessage( "Reverse: Enabled.", recvfrom )
		else:
			sendMessage( "Reverse: Disabled.", recvfrom )
		saveDatabase()
		return True
	elif args == "on" or args == "true":
		database['globals']['reverse'] = True
		sendMessage( "Reverse: Enabled.", recvfrom )
		saveDatabase()
		return True
	elif args == "off" or args == "false":
		database['globals']['reverse'] = False
		sendMessage( "Reverse: Disabled.", recvfrom )
		saveDatabase()
		return True
	sendMessage( "Usage: reverse <on/true/off/false>", recvfrom )
	return False

def toggleAway( message, recvfrom ):
	global away
	if not away:
		sendMessage( "Going Away. Reason: " + message, recvfrom )
		sendPacket( makePacket( "AWAY " + message ), forceDebugPrint=True )
		away = True
	else:
		sendMessage( "Back.", recvfrom )
		sendPacket( makePacket( "AWAY" ), forceDebugPrint=True )
		away = False
## MISC BUILT-IN COMMANDS ##
############################


########################
## PERMISSIONS STUFFS ##
def addUser( args, recvfrom, user ):
	global database
	args = args.partition( " " )
	if args[0] != "" and args[2] != "":
		currentAccess = getAccessLevel( args[0] )
		myAccess = getAccessLevel( user )
		if currentAccess == 4 and myAccess < 4:
			sendMessage( "You are not allowed to change the rank of a BOTDEV!", recvfrom )
			return False
		
		if args[2].lower() == "botdev":
			if myAccess >= 4:
				requestedAccess = 4
				requestedAccessText = "BOTDEV."
			else:
				sendMessage( "Insufficient permissions to add a BOTDEV!", recvfrom )
				return False
		elif args[2].lower() == "dev" or args[2].lower() == "developer":
			requestedAccess = 3
			requestedAccessText = "DEVELOPER."
		elif args[2].lower() == "support":
			requestedAccess = 2
			requestedAccessText = "SUPPORT."
		elif args[2].lower() == "trusted":
			requestedAccess = 1
			requestedAccessText = "TRUSTED."
		elif args[2].lower() == "banned":
			requestedAccess = -1
			requestedAccessText = "BANNED."
		else:
			sendMessage( "Unknown rank requested.", recvfrom )
			return False
		
		if currentAccess == requestedAccess:
			sendMessage( args[0] + " is already " + requestedAccessText, recvfrom )
			return False
		
		if currentAccess == 0:
			change = " was added as "
		else:
			change = " was changed to "
		
		database['accessList'][args[0]] = requestedAccess
		sendMessage( args[0] + change + requestedAccessText, recvfrom )
		saveDatabase()
		return True
	sendMessage( "Usage: add [nick] [rank]", recvfrom )
	return False

def removeUser( args, recvfrom, user ):
	global database
	if args != "":
		currentAccess = getAccessLevel( args )
		if currentAccess == 0:
			sendMessage( args + " is not added yet.", recvfrom )
			return False
		else:
			userAccess = getAccessLevel( user )
			if ( currentAccess != 4 ) or ( userAccess == 4 and user != args ):
				del database['accessList'][args]
				sendMessage( args + " was removed.", recvfrom )
				saveDatabase()
				return True
			else:
				sendMessage( "You are not allowed to remove a BOTDEV!", recvfrom )
				return False
	sendMessage( "Usage: remove [nick]", recvfrom )
	return False

def listUsers( recvfrom ):
	global database
	botdevs = []
	developers = []
	supports = []
	trusteds = []
	banneds = []
	for user in database['accessList']:
		if database['accessList'][user] == 4:
			botdevs.append( user )
		elif database['accessList'][user] == 3:
			developers.append( user )
		elif database['accessList'][user] == 2:
			supports.append( user )
		elif database['accessList'][user] == 1:
			trusteds.append( user )
		elif database['accessList'][user] == -1:
			banneds.append( user )
	
	thelist = ""
	
	# Check that there's at least one entry, otherwise we end up with an extra e.x. "[Trusted], " without a user to match it
	if len( botdevs ) > 0:
		thelist = thelist + "[BotDev], ".join( sorted( botdevs, key=str.lower ) ) + "[BotDev], "
	if len( developers ) > 0:
		thelist = thelist + "[Developer], ".join( sorted( developers, key=str.lower ) ) + "[Developer], "
	if len( supports ) > 0:
		thelist = thelist + "[Support], ".join( sorted( supports, key=str.lower ) ) + "[Support], "
	if len( trusteds ) > 0:
		thelist = thelist + "[Trusted], ".join( sorted( trusteds, key=str.lower ) ) + "[Trusted], "
	if len( banneds ) > 0:
		thelist = thelist + "[Banned], ".join( sorted( banneds, key=str.lower ) ) + "[Banned], "
	
	# Chop off extra comma if necessary
	if thelist[-2:] == ", ":
		thelist = thelist[:-2]
	
	# Make sure we're actually sending something
	if len( thelist ) > 0:
		sendMessage( thelist, recvfrom )
		return True
	
	sendMessage( "Access list appears to be empty!", recvfrom )
	return False

def getAccessLevel( user ):
	global database
	access = 0
	if user in database['accessList']:
		access = database['accessList'][user]
	return access
## PERMISSIONS STUFFS ##
########################


###############
## OP STUFFS ##
def banUser( info, user, recvfrom ):
	sendMessage( "NYI", recvfrom )
	return False

def kickUser( info, user, recvfrom ):
	sendMessage( "NYI", recvfrom )
	return False

def unbanUser( user, recvfrom ):
	sendMessage( "NYI", recvfrom )
	return False
## OP STUFFS ##
###############


###########################
## BOT INFOEDITING BEGIN ##
def editBotInfo( args, recvfrom ):
	global database
	if args != "":
		# TODO: Stop making lists of tuples just to modify a value in it.
		args = list( args.partition( " " ) )
		args[0] = args[0].lower()
		# TODO: Make sure a nick change is actually successful
		if args[0] == "nick":
			args[2] = args[2].replace( " ", "_" )
			sendPacket( makePacket( "NICK " + args[2] ) )
			database['botInfo']['nick'] = args[2]
			saveDatabase()
			return True
		elif args[0] == "reset":
			args[2] = "PyBot"
			sendPacket( makePacket( "NICK " + args[2] ) )
			database['botInfo']['nick'] = args[2]
			saveDatabase()
			return True
	sendMessage( "Usage: bot [nick/reset] <value>", recvfrom )
	return False

def changeChannel( chan, recvfrom ):
	global database
	if chan != "":
		# TODO: Stop making lists of tuples just to modify a value in it.
		chan = list( chan.partition( " " ) )
		chan[0] = chan[0].lower()
		if chan[0] == "add":
			database['botInfo']['channels'].append( chan[2] )
			sendPacket( makePacket( "JOIN " + chan[2] ) )
			saveDatabase()
			return True
		elif chan[0] == "remove":
			database['botInfo']['channels'].remove( chan[2] )
			sendPacket( makePacket( "PART " + chan[2] + " :Channel removed!" ) )
			saveDatabase()
			return True
		elif chan[0] == "list":
			sendMessage( ", ".join( sorted( database['botInfo']['channels'], key=str.lower ) ), recvfrom )
			return True
	sendMessage( "Usage: channels [add/remove/list] <channel>", recvfrom )
	return False
## BOT  INFOEDITING  END ##
###########################


##############
## CORE BOT ##
def login():
	global database, loggedIn, slowConnect, CAPs
	if slowConnect:
		time.sleep( 2 )
	if CAPs['actuallyUseThisCrap']:
		sendPacket( makePacket( "CAP LS" ), forceDebugPrint=True )
	sendPacket( makePacket( "NICK " + database['botInfo']['nick'] ), forceDebugPrint=True )
	sendPacket( makePacket( "USER " + database['botInfo']['nick'] + " " + database['botInfo']['nick'] + " " + database['botInfo']['network'] + " :" + database['botInfo']['nick'] ), forceDebugPrint=True )
	loggedIn = True

def handleCAPs( packet ):
	global CAPs, database, sock
	if database['globals']['debug']:
		print( "Handling CAP: " + str( packet ) )
	if " LS :" in packet['rest']:
		CAPs['server'] = packet['rest'].partition( " LS :" )[2].split()
		for cap in CAPs['server']:
			if cap in CAPs['client']:
				CAPs['enabled'].append( cap )
		if CAPs['enabled']:
			sendPacket( makePacket( "CAP REQ :" + " ".join( CAPs['enabled'] ) ) )
			return True
	elif " ACK :" in packet['rest']:
		CAPs['enabled'] = packet['rest'].partition( " ACK :" )[2].split()
		if "sasl" in CAPs['enabled']:
			sendPacket( makePacket( "AUTHENTICATE PLAIN" ) )
			data = sock.recv( 512 ).decode( errors="ignore" )
			password = ( base64.b85decode( database['botInfo']['password'] ) ).decode( "utf-8" )
			sendPacket( makePacket( "AUTHENTICATE " + (base64.b64encode( '\0'.join( (database['botInfo']['nick'], database['botInfo']['nick'], password) ).encode( "utf-8" ) )).decode( "utf-8" ) ) )
			data = sock.recv( 2048 ).decode( errors="ignore" )
			sendPacket( makePacket( "CAP END" ) )
			return True
	return False

def chanJoin():
	global database, chanJoined, chanJoinDelay, slowConnect, CAPs
	if slowConnect:
		time.sleep( 2 )
	chanJoinDelay = chanJoinDelay + 2
	if chanJoinDelay >= 1: #whatever
		# Auth should (try) to be done before join.
		# It's not realistic to expect that to happen with NickServ/PM-based auth however,
		# but let's give it a little head start at least.
		password = ( base64.b85decode( database['botInfo']['password'] ) ).decode( "utf-8" )
		if password != "" and "sasl" not in CAPs['enabled']:
			sendPacket( makePacket( "PRIVMSG NickServ :IDENTIFY " + password ), forceDebugPrint=True )
		
		sendPacket( makePacket( "JOIN " + ",".join( database['botInfo']['channels'] ) ), forceDebugPrint=True )
		chanJoined = True

def init():
	global database, sock, loggedIn, chanJoined, chanJoinDelay, rebooted
	if rebooted != 0:
		sock.shutdown( socket.SHUT_RDWR )
		sock.close()
		chanJoined = False
		loggedIn = False
		chanJoinDelay = -1
	
	print( "Connecting to: " + database['botInfo']['network'] + ":" + str( database['botInfo']['port'] ) )
	
	connected = False
	while not connected:
		try:
			sock = socket.socket()
			sock.connect( ( database['botInfo']['network'], database['botInfo']['port'] ) )
			connected = True
		except TimeoutError:
			print( "Timeout error! Retrying..." )
	
	print( "Connected." )
	print( "Logging in..." )
	login()


init()	# Bot initiates here


def main():
	global sock, database, loggedIn, chanJoined, chanJoinDelay, slowConnect, CAPs
	while True:
		try:
			data = sock.recv( 8192 ).decode( errors="ignore" )
			if len( data ) > 2:	# Don't parse small stuff
				if data.count( "\n" ) > 1:	# More than 1 packet sent, most likely start connection
					data = data.splitlines()
					for x in data:
						x = makePacket( x, inbound=True )
						if database['globals']['debug']:
							recvprint( x )
						if x['command'] == "PING": # Some servers send this in the connection process, take care of that here... bastards
							sendPong( x )
						elif x['command'] == "CAP" and CAPs['actuallyUseThisCrap']:
							handleCAPs( x )
						elif ( not chanJoined ) and ( loggedIn ) and ( not "NOTICE" in x['raw'] ):
							if slowConnect:
								joinThread = threading.Thread( target=chanJoin() )
								joinThread.start()
							else:
								chanJoin()
				else:
					data = makePacket( data, inbound=True )
					recvprint( data )
					if data['command'] == "CAP" and CAPs['actuallyUseThisCrap']:
						handleCAPs( data )
					else:
						threading.Thread( target=handlePackets( data ) ).start()
						#handlePackets( data )
						if ( not chanJoined ) and ( loggedIn ) and ( not "NOTICE" in data['raw'] ):
							if slowConnect:
								joinThread = threading.Thread( target=chanJoin() )
								joinThread.start()
							else:
								chanJoin()
		#except OSError:
		#	errorprint( "Error! Attempting to reconect..." )
		#	rebooted = 1
		#	init()
		except KeyboardInterrupt:
			sock.close()
			exit()


#mainThread = threading.Thread( target=main(), daemon=False, name="[PyBot] Main Thread" )
#mainThread.start()
main()
## CORE BOT ##
##############
