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

info = { "names" : [ "horoscope", "zodiac", "sign", "horo" ], "access" : 0, "version" : 1 }

signs = [ "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces" ]

def command( message, user, recvfrom ):
	message = message.strip().lower()
	if message in signs:
		txt = requests.get( "http://www.astrology.com/horoscope/daily/" + message + ".html" ).text
		horoscope = fixHTMLCharsAdvanced( strbetween( txt, "<div class=\"page-horoscope-text\">", "</div>" ) )
		if horoscope != "":
			__main__.sendMessage( horoscope, recvfrom )
		else:
			__main__.sendMessage( message + "'s sign not found today. :(", recvfrom )
	elif message == "":
		__main__.sendMessage( "Usage: horoscope [sign]", recvfrom )
	else:
		__main__.sendMessage( "Invalid sign. Valid signs: " + (", ".join( signs )), recvfrom )
	return True
