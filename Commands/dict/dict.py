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
import __main__, requests

info = { "names" : [ "dict", "define", "dictionary", "definition" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		res = requests.get( "http://dictionary.reference.com/browse/" + message )
		wordCased = __main__.fixHTMLChars( __main__.strbetween( res.text, "<meta name=\"description\" content=\"", " definition, " ) )
		if wordCased != "":
			definition = __main__.fixHTMLChars( __main__.strbetween( res.text, "<meta name=\"description\" content=\"" + wordCased + " definition, ", " See more.\"/>" ) )
			if definition != "":
				__main__.sendMessage( message + ": " + definition, channel )
			else:
				__main__.sendMessage( message + " was not found.", channel )
		else:
			__main__.sendMessage( message + " was not found.", channel )
		return True
	except:
		return False
