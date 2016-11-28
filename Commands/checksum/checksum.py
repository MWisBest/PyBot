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
import __main__, hashlib

info = { "names" : [ "hash", "checksum" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	mpart = message.partition( " " )
	alg = mpart[0]
	data = mpart[2]
	
	# There's this other 'sha' besides 'sha1' which produces different results than 'sha1'
	# 99.99% of users will actually mean 'sha1' when they say 'sha'
	if alg.lower() == "sha":
		alg = "sha1"
	
	# The most often used algorithms are the guaranteed ones (which are listed in lowercase). Check there first to avoid a delay.
	# Sometimes lowercase version is in 'available' but not uppercase, check that here as well.
	if alg.lower() in hashlib.algorithms_guaranteed or alg.lower() in hashlib.algorithms_available:
		__main__.sendMessage( str( hashlib.new( alg.lower(), data.encode() ).hexdigest() ), recvfrom )
		return True
	elif alg in hashlib.algorithms_available:
		__main__.sendMessage( str( hashlib.new( alg, data.encode() ).hexdigest() ), recvfrom )
		return True
	elif alg.lower() == "help":
		# Get a compact, non-duplicating list of available algorithms.
		otheralgs = hashlib.algorithms_available.copy()
		for entry in otheralgs.copy():
			if (entry.lower() in hashlib.algorithms_guaranteed) or (not entry.islower() and entry.lower() in otheralgs) or (entry.lower() == "sha"):
				otheralgs.remove( entry )
		alglist = sorted( hashlib.algorithms_guaranteed, key=str.lower ) + sorted( otheralgs, key=str.lower )
		__main__.sendMessage( "Available algorithms: " + ", ".join( alglist ), recvfrom )
	else:
		__main__.sendMessage( "Usage: hash [algorithm] [data]. See 'hash help' for algorithms.", recvfrom )
	return False
