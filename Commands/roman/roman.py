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
import __main__, re

info = { "names" : [ "roman" ], "access" : 0, "version" : 1 }

romanNumeralMap = ( ( "M",  1000 ), ( "CM", 900 ), ( "D",  500 ), ( "CD", 400 ), ( "C",  100 ), ( "XC", 90 ), ( "L",  50 ), ( "XL", 40 ), ( "X",  10 ), ( "IX", 9 ), ( "V",  5 ), ( "IV", 4 ), ( "I",  1 ) )
romanNumeralPattern = re.compile( r"^M{0,249}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$" )

def command( message, user, channel ):
	try:
		result = ""
		if message.isdigit() and "." not in message: # Numeric, convert to roman numerals
			number = int( message )
			if 250000 > number > 0:
				for ( numeral, integer ) in romanNumeralMap:
					while number >= integer:
						result = result + numeral
						number = number - integer
			else:
				result = "Can't be less than 1, and I'm not going over 249,999 either!"
		elif romanNumeralPattern.search( message ):
			intsult = 0
			index = 0
			for ( numeral, integer ) in romanNumeralMap:
				while message[index:index+len(numeral)] == numeral:
					intsult = intsult + integer
					index = index + len( numeral )
			result = str( intsult )
		else:
			result = "I only accept integers and valid roman numerals from 1 to 249,999."
		__main__.sendMessage( result, channel )
		return True
	except:
		return False
