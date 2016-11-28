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
import __main__, pybotutils, requests, os

def googlshort( link ):
	try:
		# TODO: Why do we need to do this every time...
		with open( "Utilities" + os.sep + "pybotutils" + os.sep + "googlapikey.txt", "r" ) as apikeyfile:
			GOOGL_API_KEY = apikeyfile.read()
		if not link.startswith( "http://goo.gl/" ) and not link.startswith( "https://goo.gl/" ):
			json_data = "{\n\t\"longUrl\" : \"" + link + "\"\n}"
			theheaders = { "content-type" : "application/json" }
			res = requests.post( "https://www.googleapis.com/urlshortener/v1/url?key=" + GOOGL_API_KEY, data=json_data, headers=theheaders )
			return pybotutils.strbetween( res.text, "\"id\": \"", "\"" )
		else:
			res = requests.get( "https://www.googleapis.com/urlshortener/v1/url?key=" + GOOGL_API_KEY + "&shortUrl=" + link )
			return pybotutils.strbetween( res.text, "\"longUrl\": \"", "\"" )
	except:
		return ""
