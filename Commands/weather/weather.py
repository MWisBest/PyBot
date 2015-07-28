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

info = { "names" : [ "weather", "w" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		# .co.uk works with both UK and USA. .com does not!
		wbpostfix = ".co.uk"
		#splitmessage = message.split( ' ', maxsplit=1 )
		#if len( splitmessage ) == 2:
		#	if len( splitmessage[0] ) == 3 and len( splitmessage[1] ) == 3:
		#		wbpostfix = ".co.uk"
		res = requests.get( "http://weather.weatherbug" + wbpostfix + "/Common/SearchResults.html?loc=" + message + "&is_search=true&nav_section=1&loc_country=WORLD&zcode=z6286&submit=GO" )
		try:
			location = __main__.fixHTMLCharsAdvanced( __main__.strbetween( res.text, "\r\n<div class=\"boxhdr\">", "</h2>" ) ).replace( "  ", "" ).replace( "<h2>", "" ).strip() # Oh god this is ugly. so very ugly.
			farTemp = __main__.fixHTMLChars( __main__.strbetween( res.text, "<div><strong><span id=\"divTemp\" class=\"entry-title\">", "&deg;F</span></strong>" ) ) #Fahrenheit
			celTemp = str( round( ( float( farTemp ) - 32 ) * 5 / 9, 1 ) ) #celsius
			humidity = __main__.fixHTMLChars( __main__.strbetween( res.text, "<span id=\"divHumidity\" class=\"strong-value\">", "</span></div>" ) )
			feelsLikeLabel = __main__.fixHTMLChars( __main__.strbetween( res.text, "<span id=\"spanFeelsLikeLabel\">", "</span>" ) )
			feelsLikeF = __main__.fixHTMLChars( __main__.strbetween( res.text, "<span id=\"divFeelsLike\" class=\"strong-value\">", "&deg;F</span></div>" ) )
			feelsLikeC = str( round( ( float( feelsLikeF ) - 32 ) * 5 / 9, 1 ) ) #celsius
			rain = __main__.fixHTMLChars( __main__.strbetween( res.text, "<span id=\"divRain\" class=\"strong-value\">", "</span></div>" ) )
			gust = __main__.fixHTMLChars( __main__.strbetween( res.text, "<span id=\"divGust\" class=\"strong-value\">", "</span></div>" ) )
			if farTemp != "":
				toSend = location + " | Temperature: " + farTemp + "°F/" + celTemp + "°C"
				if humidity != "":
					toSend = toSend + " | Humidity: " + humidity
				if feelsLikeLabel != "" and feelsLikeF != "":
					toSend = toSend + " | " + feelsLikeLabel + ": " + feelsLikeF + "°F/" + feelsLikeC + "°C"
				if rain != "":
					toSend = toSend + " | Rain: " + rain
				if gust != "":
					toSend = toSend + " | Gust: " + gust
				__main__.sendMessage( toSend, channel )
				return True
		except:
			pass
		__main__.sendMessage( message + " was not found.", channel )
		return False
	except:
		return False
