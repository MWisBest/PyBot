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

info = { "names" : [ "currency", "curr", "money", "exchange" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		message = message.split( " " )
		amount = message[0]
		codeFrom = message[1]
		codeTo = message[2]
		res = requests.get( "http://www.mobilecurrencyconverter.com/index.php?cur_n=" + amount + "&cur_f=" + codeFrom + "&cur_t=" + codeTo + "&cur_s=major&a=Y" )
		rate = __main__.fixHTMLChars( __main__.strbetween( res.text, "</font><br/><font class=\"cr_cv1\">(", ")</font>" ) )
		if "  " in rate:
			while "  " in rate:
				rate = rate.replace( "  ", " " )
		rate = rate.strip()
		if rate != "" and rate != "1 = 0.00":
			__main__.sendMessage( rate, channel )
		else:
			__main__.sendMessage( "No conversion found, make sure you write the proper currency code.", channel )
		return True
	except:
		return False
