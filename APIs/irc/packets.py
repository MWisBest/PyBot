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


def makePacket( data, inbound ):
	packet = { "host" : "", "command" : "", "rest" : "", "raw" : data, "timestamp" : 0 }
	
	### SEC-NOTICE: We only send a packet at a time; there should NOT be any newlines in it! ###
	# This is somewhat defensive: sendPacket takes care of this on its own too. #
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
	#if __main__.database['globals']['debug']:
		#print( str( packet ) )
	return packet


def sendPacket( packet, sock, forceDebugPrint ):
	sent = True
	# TODO: Fix this crap
	
	### SEC-NOTICE: We only send a packet at a time; there should NOT be any newlines in it! ###
	# This is somewhat defensive: makePacket should've taken care of this for us already. #
	packet['raw'] = packet['raw'].replace( "\r", "" ).replace( "\n", "" )
	
	bytespacket = ( packet['raw'] + "\r\n" ).encode( errors="ignore" )
	
	length = len( bytespacket )
	amountSent = 0
	while length != amountSent:
		try:
			amountSent += sock.send( bytespacket )
		except:
			sent = False
	# Set the packet's timestamp to the time when we actually finished sending it.
	packet['timestamp'] = time.time()
	if forceDebugPrint:
		if __main__.database['globals']['debug']: # Check this in here rather than with an and up above, this way we don't print debug stuff when debug is off
			__main__.senddebugprint( packet['raw'], packet['timestamp'] )
	else:
		__main__.sendprint( packet )
	if not sent:
		__main__.warnprint( "Last packet did not send successfully. If this persists, check your connection and/or restart the bot." )



def onReboot():
	__main__.sendPacket( __main__.makePacket( "QUIT :PyBot " + __main__.pyBotVersion + ". (Rebooting)" ) )

def onDie():
	__main__.sendPacket( __main__.makePacket( "QUIT :PyBot " + __main__.pyBotVersion + ". (Shutting down)" ) )



def sendMessage( message, whereto ):
	__main__.sendPacket( __main__.makePacket( "PRIVMSG " + whereto + " :" + message ) )

def sendPong( pingpacket ): # PING reply
	pingpacket['command'] = "PONG"
	pingpacket['raw'] = pingpacket['raw'].replace( "PING", "PONG" )
	__main__.sendPacket( pingpacket )

def sendMe( message, whereto ):
	__main__.sendPacket( __main__.makePacket( "PRIVMSG " + whereto + " :\x01ACTION " + message + "\x01" ) )

