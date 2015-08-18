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
from pybotutils import strbetween

info = { "names" : [ "geoip" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	try:
		if message == "" or message == " ":
			__main__.sendMessage( "Usage: geoip [ip.add.re.ss/domain.name]", recvfrom )
			return True
		txt = requests.get( "http://freegeoip.net/json/" + message ).text
		ip = strbetween( txt, "\"ip\":\"", "\"," )
		latitude = strbetween( txt, "\"latitude\":", ",\"" )
		longitude = strbetween( txt, "\"longitude\":", ",\"" )
		#countryCode = strbetween( txt, "\"country_code\":\"", "\"," )
		countryName = strbetween( txt, "\"country_name\":\"", "\"," )
		#regionCode = strbetween( txt, "\"region_code\":\"", "\"," )
		regionName = strbetween( txt, "\"region_name\":\"", "\"," )
		city = strbetween( txt, "\"city\":\"", "\"," )
		#zipcode = strbetween( txt, "\"zipcode\":\"", "\"," )
		if ip != "": # IP has to be there if there was any useful info
			toSend = "IP: " + ip
			if city != "" and countryName != "" and regionName != "":
				toSend += " | Location: "
				if city != "":
					toSend += city + ", "
				if regionName != "":
					toSend += regionName + ", "
				if countryName != "":
					toSend += countryName
			if latitude != "" and longitude != "":
				toSend += " | Coordinates: " + latitude + "," + longitude
			if toSend == "IP: " + ip + " | Coordinates: 38,-97": # This is a bullshit result
				toSend = message + " was not found."
			__main__.sendMessage( toSend, recvfrom )
		else:
			__main__.sendMessage( message + " was not found.", recvfrom )
		return True
	except:
		return False
