#! /usr/bin/python3
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
import socket, sys, os, pickle, threading, random, platform, time, io, base64, importlib

# Version check.
pyversion = platform.python_version_tuple()
if int( pyversion[0] ) < 3:
	print( "Anything lower than Python 3.4 isn't supported, UPGRADE OR DIE." )
	exit()
elif int( pyversion[0] ) == 3 and int( pyversion[1] ) < 4:
	print( "PyBot requires Python 3.4 or higher. Sorry!" )
	exit()


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
away = False
slowConnect = False
pyBotVersion = "Beta"
sock = socket.socket()
## GLOBALS ##
#############


#####################
## MODULAR IMPORTS ##
# This is a pretty clever way to make the bot modular/extensible. :)
def importFolder( foldername, dictaddedto="", headervar=".info" ):
	folderpath = os.path.dirname( os.path.realpath( __file__ ) ) + os.sep + foldername + os.sep
	sys.path.insert( 1, folderpath )
	for modulefolder in os.listdir( folderpath ):
		if os.path.isdir( folderpath + modulefolder + os.sep ):
			try:
				exec( "global " + modulefolder + "\nimport " + modulefolder ) # as much as I hate exec, i cant find another way to do this!
				if dictaddedto != "":
					exec( "global " + dictaddedto + "dict\n" + dictaddedto + "dict[modulefolder] = " + modulefolder + headervar )
			except Exception as err:
				print( "Failed to import: " + modulefolder )
				try: # We might not have imported pybotutils yet
					print( pybotutils.getExceptionTraceback( err ) )
				except:
					print( str( err ) )

# Current required modules are:
# - colorama
# - requests
# - termcolor
# The idea is to distribute them with the bot directly to avoid the user having to install them with pip,
# however should any author request their module to be removed and require users to install with pip I will respect that.
importFolder( "Modules" )

# Utilities is meant to distinguish between a 'homegrown' module and a module written by somebody else.
# Current required utilities are:
# - pybotutils
importFolder( "Utilities" )

# APIs refer to different chat systems that can be connected to in a simple, modular manner.
apidict = {}
API = {}
importFolder( "APIs", dictaddedto="api", headervar="" )

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
errorprint = lambda x: termcolor.cprint( x.replace( "\r", "" ), "red", attrs=['bold'] )
warnprint = lambda x: termcolor.cprint( x.replace( "\r", "" ), "yellow", attrs=['bold'] )
## CONSOLE OUTPUT SETUP ##
##########################


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
	global API, database, databaseName
	with open( databaseName, "rb" ) as pybotfile:
		with io.BytesIO( pybotfile.read() ) as pybotfilebytes:
			database = ( PyBotUnpickler( pybotfilebytes ) ).load()
	API = apidict[database['api']['system']]

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
	if database['version'] == 2: # Upgrade to version 3
		# Version 3 changes:
		# - ['botInfo']['password'] is now stored in base85 format rather than plaintext.
		#     This doesn't provide any real security, but it prevents some noob from
		#     just opening the database in a text editor and seeing the password.
		database['botInfo']['password'] = base64.b85encode( database['botInfo']['password'].encode( "utf-8" ), pad=True )
		database['version'] = 3
		saveDatabase()
	if database['version'] == 3: # Upgrade to version 4
		# Version 4 changes:
		# - Modular API system
		database['api'] = {}
		database['api']['system'] = "irc" # default to IRC
		database['api']['ircsettings'] = {}
		database['api']['ircsettings']['channels'] = database['botInfo']['chanels']
		database['api']['ircsettings']['nick']     = database['botInfo']['nick']
		database['api']['ircsettings']['pw']       = database['botInfo']['password']
		database['api']['ircsettings']['network']  = database['botInfo']['network']
		database['api']['ircsettings']['port']     = database['botInfo']['port']
		del database['botInfo']['channels']
		del database['botInfo']['nick']
		del database['botInfo']['password']
		del database['botInfo']['network']
		del database['botInfo']['port']
		database['version'] = 4
		saveDatabase()
except IOError: # Create pybot.pickle on first start
	#, "network" : "", "port" : 0, "channels" : []
	database = { "api"        : { "system" : "irc", "ircsettings" : { "channels" : [], "nick" : "", "pw" : base64.b85encode( "".encode( "utf-8" ), pad=True ), "network" : "", "port" : -1 } },
				 "accessList" : {},
				 "globals"    : { "cc" : "!", "reverse" : False, "debug" : False },
				 "version"    : 4 }
	print( colorama.Fore.CYAN )
	temp = ""
	while temp not in apidict.keys():
		temp = input( "Please select an API from the following: " + str( list( apidict.keys() ) ) + "\n" )
	database['api']['system'] = temp
	API = apidict[temp]
	API.inputSettings()
	devel = input( "Please enter your Nick so the bot will listen to you.\n" )
	database['accessList'][devel] = 4
	print( colorama.Fore.WHITE )
	saveDatabase()
## Load up the database ASAP ##
###############################


###########################
## FORMAT CONSOLE OUTPUT ##
def sendprint( packet ):
	global API
	API.sendprint( packet )

def recvprint( packet ):
	global API
	API.recvprint( packet )
## FORMAT CONSOLE OUTPUT ##
###########################


###########
## UTILS ##
# TODO: Move some of these to pybotutils
def makePacket( data, inbound=False ):
	global API
	return API.makePacket( data, inbound )

def sendPacket( packet, forceDebugPrint=False ):
	global API, sock
	API.sendPacket( packet, sock, forceDebugPrint )

def reboot():
	global API, sock, pyBotVersion
	API.onReboot()
	sock.shutdown( socket.SHUT_RDWR )
	sock.close()
	os.execl( sys.executable, sys.executable, * sys.argv )

def reconnect():
	global rebooted
	rebooted = 1
	init()

def die():
	global API, sock, pyBotVersion
	API.onDie()
	sock.shutdown( socket.SHUT_RDWR )
	sock.close()
	exit()
## UTILS ##
###########


#########################
## MAIN PACKET HANDLER ##
def handlePackets( packet ):
	global API, database
	runThroughHandlers = True # If WE handle a packet here, the handlers shouldn't.
	if API.isMessage( packet ):
		user = API.getMessageUser( packet )
		locfrom = API.getMessageLoc( packet )
		message = API.getMessageText( packet )
		myAccess = getAccessLevel( user )
		if len( message ) > 1 and message[0] == database['globals']['cc'] and myAccess >= 0:
			message = message[1:]
			args = list( message.partition( " " ) )
			args[0] = args[0].lower()
			if args[0] == "cmdto" and myAccess >= 2:
				argssplit = args[2].split( " ", maxsplit=2 )
				if len( argssplit ) >= 2 and "" not in argssplit:
					locfrom = argssplit[0]
					args[0] = argssplit[1].lower()
					if len( argssplit ) == 3:
						args[2] = argssplit[2]
					else:
						args[2] = ""
				else:
					sendMessage( "Usage: cmdto [location] [command] <args>", locfrom )
					return
			if args[0] == "say":
				if args[2] != "":
					sendMessage( args[2], locfrom )
				else:
					sendMessage( "Usage: say [message]", locfrom )
			elif args[0] == "me":
				# NOTE: sendMe actually works with an empty message
				sendMe( args[2], locfrom )
			elif args[0] == "ping":
				sendMessage( "pong!", locfrom )
			elif args[0] == "pong":
				sendMessage( "FUCK YOU! ONLY I PONG!", locfrom )
			elif args[0] == "help":
				sendMessage( "https://github.com/MWisBest/PyBot", locfrom )
			elif args[0] == "access":
				accessHandler( args[2], user, locfrom )
			elif args[0] == "ban" and myAccess >= 2:
				banUser( args[2], user, locfrom )
			elif args[0] == "unban" and myAccess >= 2:
				unbanUser( args[2], locfrom )
			elif args[0] == "kick" and myAccess >= 2:
				kickUser( args[2], user, locfrom )
			elif args[0] == "away" and myAccess >= 2:
				toggleAway( args[2], locfrom )
			elif args[0] == "reverse" and myAccess >= 2:
				toggleReverse( args[2], locfrom )
			elif args[0] == "bot" and myAccess >= 2:
				editBotInfo( args[2], locfrom )
			elif args[0] == "cc" and myAccess >= 2:
				commandChar( args[2], locfrom )
			elif args[0] in ["channel", "channels"] and myAccess >= 3:
				changeChannel( args[2], locfrom )
			elif args[0] == "packet" and myAccess >= 3:
				sendPacket( makePacket( args[2] ) )
			elif args[0] == "die" and myAccess >= 3:
				die()
			elif args[0] == "reboot" and myAccess >= 3:
				reboot()
			elif args[0] == "debug" and myAccess >= 4:
				changeDebug( args[2], locfrom )
			elif args[0] in ["import", "reimport"] and myAccess >= 4:
				reimportModule( args[2], locfrom )
			elif args[0] == "exec" and myAccess >= 4 and database['globals']['debug']:
				try:
					exec( args[2] )
				except Exception as err:
					# who knows what the hell we're trying here...
					# chances are somebody is fucking up if they use exec in the first place
					errorprint( "Unexpected error: " + message )
					warnprint( pybotutils.getExceptionTraceback( err ) )
					sendMessage( "Yeah, you had an issue in there somewhere.", locfrom )
			else:
				externalCommands( args[0], args[2], user, locfrom, myAccess )
			runThroughHandlers = False
	if runThroughHandlers: # Try all the external handlers then.
		externalHandlers( packet )

def externalCommands( cmdused, message, user, recvfrom, accessLevel ):
	global commanddict
	for key in commanddict.keys():
		try: # so we can continue through the loop on fuck ups
			if cmdused in commanddict[key]['names'] and accessLevel >= commanddict[key]['access']:
				if commanddict[key]['version'] == 1:
					# I hate eval, but this should be secure enough
					eval( key + ".command( message, user, recvfrom )" )
				elif commanddict[key]['version'] == 2:
					# Version 2 adds sending the command used to the command too.
					# This allows a merge of 'rurban' and 'urban' for example.
					eval( key + ".command( cmdused, message, user, recvfrom )" )
				# We don't need to keep iterating if we got what we need;
				# Let the caller know we succeeded.
				return True
		except Exception as err: # fix your shit
			errorprint( "Error in command: " + key )
			warnprint( pybotutils.getExceptionTraceback( err ) )
			continue # lets just keep going then.
	# Let the caller know we failed to find a matching command.
	return False

def externalHandlers( packet ):
	global handlerdict
	for key in handlerdict.keys():
		try: # so we can continue through the loop on fuck ups
			if packet['command'] in handlerdict[key]['packets']:
				# I hate eval, but this should be secure enough
				eval( key + ".handle( packet )" )
		except: # fix your shit
			continue # lets just keep going then.
## MAIN PACKET HANDLER ##
#########################


#################
## SEND STUFFS ##
def sendMessage( message, whereto ):
	global API, database
	if database['globals']['reverse']:
		message = message[::-1]
	API.sendMessage( message, whereto )

def sendMe( message, whereto ):
	global API, database
	if database['globals']['reverse']:
		message = message[::-1]
	API.sendMe( message, whereto )
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
				code += name + "." + name + " = importlib.reload( " + name + "." + name + " )\n"
				code += name + " = importlib.reload( " + name + " )\n"
			else:
				# ...if it's NOT a reimport, we can just use the regular import statement and we're good to go.
				code += "import " + name + "\n"
			code += type + "dict[name] = " + name + ".info\n"
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
	except Exception as err:
		sendMessage( "Error occurred trying to import module!", recvfrom )
		errorprint( "Error occurred importing: " + args[1] )
		warnprint( pybotutils.getExceptionTraceback( err ) )
		return False
	sendMessage( "Usage: reimport [command/handler] [name]", recvfrom )
	return False

def changeDebug( message, recvfrom ):
	global database
	message = message.lower().strip()
	
	if message == "": # Toggle it in this case
		database['globals']['debug'] = not database['globals']['debug']
	elif message == "on" or message == "true":
		database['globals']['debug'] = True
	elif message == "off" or message == "false":
		database['globals']['debug'] = False
	else:
		sendMessage( "Usage: debug <on/true/off/false>", recvfrom )
		return False

	# NOTE: This function is hard to follow. The basic idea is this:
	#       If we've fallen through this far, we didn't send the usage message.
	#       So, rather than call saveDatabase and sendMessage in each of the
	#       three valid, non-usage cases, just handle it all at once here.
	if database['globals']['debug']:
		sendMessage( "Debugging: enabled.", recvfrom )
	else:
		sendMessage( "Debugging: disabled.", recvfrom )
	saveDatabase()
	return True
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
	global away, database
	# TODO: API
	if database['api']['system'] != "irc":
		return
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
def accessHandler( args, user, recvfrom ):
	args = args.partition( " " )
	myAccess = getAccessLevel( user )
	if args[0] in ["list", "add", "remove"]:
		if args[0] == "list":
			return accessListUsers( recvfrom )
		elif args[0] == "add" and myAccess >= 3:
			return accessAddUser( args[2], user, recvfrom )
		elif args[0] == "remove" and myAccess >= 3:
			return accessRemoveUser( args[2], user, recvfrom )
		else:
			sendMessage( "You don't have permission to do that!", recvfrom )
			return False
	else:
		sendMessage( "Usage: access [list/add/remove] <args>", recvfrom )
		return False

def accessListUsers( recvfrom ):
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
		thelist += "[BotDev], ".join( sorted( botdevs, key=str.lower ) ) + "[BotDev], "
	if len( developers ) > 0:
		thelist += "[Developer], ".join( sorted( developers, key=str.lower ) ) + "[Developer], "
	if len( supports ) > 0:
		thelist += "[Support], ".join( sorted( supports, key=str.lower ) ) + "[Support], "
	if len( trusteds ) > 0:
		thelist += "[Trusted], ".join( sorted( trusteds, key=str.lower ) ) + "[Trusted], "
	if len( banneds ) > 0:
		thelist += "[Banned], ".join( sorted( banneds, key=str.lower ) ) + "[Banned], "
	
	# Chop off extra comma if necessary
	if thelist[-2:] == ", ":
		thelist = thelist[:-2]
	
	# Make sure we're actually sending something
	if len( thelist ) <= 0:
		sendMessage( "Access list appears to be empty!", recvfrom )
		return False
	else:
		sendMessage( thelist, recvfrom )
		return True

def accessAddUser( args, user, recvfrom ):
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
	sendMessage( "Usage: access add [nick] [rank]", recvfrom )
	return False

def accessRemoveUser( args, user, recvfrom ):
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
	sendMessage( "Usage: access remove [nick]", recvfrom )
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
# TODO: Check NickServ registration on command users so we can implement these things here:
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
	# TODO: API
	if database['api']['system'] != "irc":
		return False
	if args != "":
		# TODO: Stop making lists of tuples just to modify a value in it.
		args = list( args.partition( " " ) )
		args[0] = args[0].lower()
		# TODO: Make sure a nick change is actually successful
		if args[0] == "nick":
			args[2] = args[2].replace( " ", "_" )
			sendPacket( makePacket( "NICK " + args[2] ) )
			database['api']['ircsettings']['nick'] = args[2]
			saveDatabase()
			return True
		elif args[0] == "reset":
			args[2] = "PyBot"
			sendPacket( makePacket( "NICK " + args[2] ) )
			database['api']['ircsettings']['nick'] = args[2]
			saveDatabase()
			return True
	sendMessage( "Usage: bot [nick/reset] <value>", recvfrom )
	return False

def changeChannel( chan, recvfrom ):
	global database
	# TODO: API
	if database['api']['system'] != "irc":
		return False
	if chan != "":
		# TODO: Stop making lists of tuples just to modify a value in it.
		chan = list( chan.partition( " " ) )
		chan[0] = chan[0].lower()
		if chan[0] == "add":
			database['api']['ircsettings']['channels'].append( chan[2] )
			sendPacket( makePacket( "JOIN " + chan[2] ) )
			saveDatabase()
			return True
		elif chan[0] == "remove":
			database['api']['ircsettings']['channels'].remove( chan[2] )
			sendPacket( makePacket( "PART " + chan[2] + " :Channel removed!" ) )
			saveDatabase()
			return True
		elif chan[0] == "list":
			sendMessage( ", ".join( sorted( database['api']['ircsettings']['channels'], key=str.lower ) ), recvfrom )
			return True
	sendMessage( "Usage: channels [add/remove/list] <channel>", recvfrom )
	return False
## BOT  INFOEDITING  END ##
###########################


##############
## CORE BOT ##
def login():
	global API, loggedIn, slowConnect
	if slowConnect:
		time.sleep( 2 )
	loggedIn = API.login()

def chanJoin():
	global API, chanJoined, slowConnect
	if slowConnect:
		time.sleep( 2 )
	chanJoined = API.join()

def init():
	global API, sock, loggedIn, chanJoined, rebooted
	if rebooted != 0:
		sock.shutdown( socket.SHUT_RDWR )
		sock.close()
		sock = socket.socket()
		chanJoined = False
		loggedIn = False
	
	API.connect()
	login()


init()	# Bot initiates here


def main():
	global API, sock, database, loggedIn, chanJoined, rebooted
	while True:
		try:
			data = sock.recv( 8192 ).decode( errors="ignore" )
			if len( data ) > 2:	# Don't parse small stuff
				if data.count( "\n" ) <= 1:
					data = makePacket( data, inbound=True )
					recvprint( data )
					threading.Thread( target=handlePackets( data ) ).start()
					# Voodoo magic: if API handles packet, wait for next packet to do channel join.
					if data['command'] in API.apiHandledPackets:
						API.handleAPIPacket( data )
					elif ( not chanJoined ) and ( loggedIn ) and ( not "NOTICE" in data['raw'] ):
						threading.Thread( target=chanJoin() ).start()
				else: # More than 1 packet sent, most likely start connection
					data = data.splitlines()
					for x in data:
						x = makePacket( x, inbound=True )
						if database['globals']['debug']:
							recvprint( x )
						# Voodoo magic: if API handles packet, wait for next packet to do channel join.
						if x['command'] in API.apiHandledPackets:
							API.handleAPIPacket( x )
						elif ( not chanJoined ) and ( loggedIn ) and ( not "NOTICE" in x['raw'] ):
							threading.Thread( target=chanJoin() ).start()
		except socket.timeout:
			errorprint( "Timeout! Attempting to reconect..." )
			rebooted = 1
			init()
		except KeyboardInterrupt:
			sock.close()
			exit()


mainThread = threading.Thread( target=main(), daemon=False, name="[PyBot] Main Thread" )
mainThread.start()
#main()
## CORE BOT ##
##############
