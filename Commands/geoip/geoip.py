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

info = { "names" : [ "geoip" ], "access" : 0, "version" : 1 }

def command( message, user, channel ):
	try:
		if message == "" or message == " ":
			__main__.sendMessage( "Usage: geoip [ip.add.re.ss/domain.name]", channel )
			return True
		res = requests.get( "http://freegeoip.net/json/" + message )
		ip = __main__.strbetween( res.text, "\"ip\":\"", "\"," )
		latitude = __main__.strbetween( res.text, "\"latitude\":", ",\"" )
		longitude = __main__.strbetween( res.text, "\"longitude\":", ",\"" )
		#countryCode = __main__.strbetween( res.text, "\"country_code\":\"", "\"," )
		countryName = __main__.strbetween( res.text, "\"country_name\":\"", "\"," )
		#regionCode = __main__.strbetween( res.text, "\"region_code\":\"", "\"," )
		regionName = __main__.strbetween( res.text, "\"region_name\":\"", "\"," )
		city = __main__.strbetween( res.text, "\"city\":\"", "\"," )
		#zipcode = __main__.strbetween( res.text, "\"zipcode\":\"", "\"," )
		if ip != "": # IP has to be there if there was any useful info
			toSend = "IP: " + ip
			if city != "" and countryName != "" and regionName != "":
				toSend = toSend + " | Location: "
				if city != "":
					toSend = toSend + city + ", "
				if regionName != "":
					toSend = toSend + regionName + ", "
				if countryName != "":
					toSend = toSend + countryName
			if latitude != "" and longitude != "":
				toSend = toSend + " | Coordinates: " + latitude + "," + longitude
			if toSend == "IP: " + ip + " | Coordinates: 38,-97": # This is a bullshit result
				toSend = message + " was not found."
			__main__.sendMessage( toSend, channel )
		else:
			__main__.sendMessage( message + " was not found.", channel )
		return True
	except:
		return False
