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
import __main__, base64, socket, termcolor, threading

info = { "pretty_name" : "IRC", "version" : 1 }

CAPs = { "server" : [], "client" : ( "sasl" ), "enabled" : [], "actuallyUseThisCrap" : True }

apiHandledPackets = [ "PING", "CAP" ]


def connect():
	# something something ping timeout
	__main__.sock.settimeout( 245 )
	termcolor.cprint( "Connecting to: " + __main__.database['api']['ircsettings']['network'] + ":" + str( __main__.database['api']['ircsettings']['port'] ), "magenta" )
	
	connected = False
	while not connected:
		try:
			__main__.sock.connect( ( __main__.database['api']['ircsettings']['network'], __main__.database['api']['ircsettings']['port'] ) )
			connected = True
		except socket.timeout:
			print( "Timeout error! Retrying..." )
	
	termcolor.cprint( "Connected.", "magenta", attrs=['bold'] )
	termcolor.cprint( "Logging in...", "magenta" )


def login():
	if CAPs['actuallyUseThisCrap']:
		__main__.sendPacket( __main__.makePacket( "CAP LS" ), forceDebugPrint=True )
	__main__.sendPacket( __main__.makePacket( "NICK " + __main__.database['api']['ircsettings']['nick'] ), forceDebugPrint=True )
	__main__.sendPacket( __main__.makePacket( "USER " + __main__.database['api']['ircsettings']['nick'] + " " + __main__.database['api']['ircsettings']['nick'] + " " + __main__.database['api']['ircsettings']['network'] + " :" + __main__.database['api']['ircsettings']['nick'] ), forceDebugPrint=True )
	return not CAPs['actuallyUseThisCrap']


def join():
	# Auth should (try) to be done before join.
	# It's not realistic to expect that to happen with NickServ/PM-based auth however,
	# but let's give it a little head start at least.
	pw = ( base64.b85decode( __main__.database['api']['ircsettings']['pw'] ) ).decode( "utf-8" )
	if pw != "" and "sasl" not in CAPs['enabled']:
		__main__.sendPacket( __main__.makePacket( "PRIVMSG NickServ :IDENTIFY " + pw ), forceDebugPrint=True )
	
	__main__.sendPacket( __main__.makePacket( "JOIN " + ",".join( __main__.database['api']['ircsettings']['channels'] ) ), forceDebugPrint=True )
	return True


def handleAPIPacket( packet ):
	if packet['command'] == "PING":
		# Make a shallow copy of the packet to avoid overwriting something.
		pingpacket = dict( packet )
		pingpacket['command'] = "PONG"
		pingpacket['raw'] = pingpacket['raw'].replace( "PING", "PONG" )
		__main__.sendPacket( pingpacket )
	elif packet['command'] == "CAP":
		handleCAPs( packet )


def handleCAPs( packet ):
	if not CAPs['actuallyUseThisCrap']:
		return False
	if __main__.database['globals']['debug']:
		print( "Handling CAP: " + str( packet ) )
	if " LS :" in packet['rest']:
		CAPs['server'] = packet['rest'].partition( " LS :" )[2].split()
		for cap in CAPs['server']:
			if cap in CAPs['client']:
				CAPs['enabled'].append( cap )
		if CAPs['enabled']:
			__main__.sendPacket( __main__.makePacket( "CAP REQ :" + " ".join( CAPs['enabled'] ) ) )
			return True
	elif " ACK :" in packet['rest']:
		CAPs['enabled'] = packet['rest'].partition( " ACK :" )[2].split()
		if "sasl" in CAPs['enabled']:
			__main__.sendPacket( __main__.makePacket( "AUTHENTICATE PLAIN" ) )
			data = __main__.sock.recv( 512 ).decode( errors="ignore" )
			pw = ( base64.b85decode( __main__.database['api']['ircsettings']['pw'] ) ).decode( "utf-8" )
			__main__.sendPacket( __main__.makePacket( "AUTHENTICATE " + (base64.b64encode( '\0'.join( (__main__.database['api']['ircsettings']['nick'], __main__.database['api']['ircsettings']['nick'], pw) ).encode( "utf-8" ) )).decode( "utf-8" ) ) )
			data = __main__.sock.recv( 2048 ).decode( errors="ignore" )
			__main__.sendPacket( __main__.makePacket( "CAP END" ) )
			__main__.loggedIn = True
			return True
	return False


def mainThread():
	while True:
		try:
			data = __main__.sock.recv( 8192 ).decode( errors="ignore" )
			if len( data ) > 2:	# Don't parse small stuff
				if data.count( "\n" ) <= 1:
					data = __main__.makePacket( data, inbound=True )
					__main__.recvprint( data )
					threading.Thread( target=__main__.handlePackets( data ) ).start()
					# Voodoo magic: if API handles packet, wait for next packet to do channel join.
					if data['command'] in __main__.API.apiHandledPackets:
						__main__.API.handleAPIPacket( data )
					elif ( not __main__.chanJoined ) and ( __main__.loggedIn ) and ( not "NOTICE" in data['raw'] ):
						threading.Thread( target=__main__.chanJoin() ).start()
				else: # More than 1 packet sent, most likely start connection
					data = data.splitlines()
					for x in data:
						x = __main__.makePacket( x, inbound=True )
						if __main__.database['globals']['debug']:
							__main__.recvprint( x )
						# Voodoo magic: if API handles packet, wait for next packet to do channel join.
						if x['command'] in __main__.API.apiHandledPackets:
							__main__.API.handleAPIPacket( x )
						elif ( not __main__.chanJoined ) and ( __main__.loggedIn ) and ( not "NOTICE" in x['raw'] ):
							threading.Thread( target=__main__.chanJoin() ).start()
		except socket.timeout:
			__main__.errorprint( "Timeout! Attempting to reconect..." )
			__main__.rebooted = 1
			__main__.init()
		except KeyboardInterrupt:
			__main__.sock.close()
			exit()
