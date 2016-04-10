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
import __main__, requests
from pybotutils import fixHTMLCharsAdvanced, strbetween

info = { "names" : [ "currency", "curr" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	try:
		message = message.split( " " )
		if len( message ) != 3 or not message[0].isdigit():
			__main__.sendMessage( "Usage: currency [amount] [from] [to]", recvfrom )
		else:
			txt = requests.get( "http://www.fxexchangerate.com/m/converter-" + message[0] + "-" + message[1] + "-to-" +  message[2] + ".html" ).text
			from1 = fixHTMLCharsAdvanced( strbetween( txt, "<title>Converter ", " To" ) )
			to1= fixHTMLCharsAdvanced( strbetween( txt, "Bid Price: ", "</div>" ) )
			toname= fixHTMLCharsAdvanced( strbetween( txt, "To ", " - FX Exchange Rate</title>" ) )
			updated= fixHTMLCharsAdvanced( strbetween( txt, "Updated:: ",  "</div>" ) )
			if from1 != "" and " = 0 " not in from1:
				__main__.sendMessage( from1 + " = " + to1 + " " + toname + " :: Last Updated: " + updated , recvfrom )
				return True
			else:
				__main__.sendMessage( "Conversion unsuccessful! Make sure to use proper currency codes.", recvfrom )
		return False
	except:
		return False
