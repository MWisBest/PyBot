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
import __main__, json, requests
from pybotutils import strbetween

info = { "names" : [ "paste", "kdepaste", "pastebin", "kdepaste", "pastie" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	try:
		json_data = { "title" : recvfrom, "data" : message, "language" : "text", "expire" : "31536000", "private" : "true" }
		txt = requests.post( "https://paste.kde.org/api/json/create", data=json_data ).text
		pasteid = strbetween( txt, "\"id\": \"", "\"," )
		pastehash = strbetween( txt, "\"hash\": \"", "\"" )
		if pasteid != "" and pastehash != "":
			__main__.sendMessage( "https://paste.kde.org/" + pasteid + "/" + pastehash, recvfrom )
		else:
			if "antispam" in txt:
				__main__.sendMessage( "Paste filtered by anti-spam filter! Try something else.", recvfrom )
			else:
				__main__.sendMessage( "Paste unsuccessful. Try again later!", recvfrom )
		return True
	except:
		return False
