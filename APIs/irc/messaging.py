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
import __main__, pybotutils


def isMessage( packet ):
	if packet['command'] == "PRIVMSG":
		return True
	return False

def getMessageUser( packet ):
	return pybotutils.strbetween( packet['host'], ":", "!" )

def getMessageLoc( packet ):
	if ((packet['rest'])[0] == "#"): # channel message
		return packet['rest'].split( " :", maxsplit=1 )[0]
	return getMessageUser( packet )

def getMessageText( packet ):
	# TODO:
	# Some commands (such as hash) NEED to parse extra spaces at the end of the message.
	# Find a more elegant way that works for everybody.
	return packet['rest'].split( " :", maxsplit=1 )[1].lstrip()
