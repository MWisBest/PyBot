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
import __main__, requests, threading
from pybotutils import fixHTMLCharsAdvanced, strbetween

info = { "names" : [ "g", "google" ], "access" : 0, "version" : 1 }

def command( message, user, recvfrom ):
	# There is a lot of shit. Cut off as much as possible before sending it to the HTML parser in an effort to speed up parsing
	datlongtext = strbetween( requests.get( "http://www.google.com/search?q=" + message ).text, " id=\"resultStats\">", "</html>" )
	datlongtext = datlongtext.replace( "<b>", "" ).replace( "</b>", "" ).replace( "<em>", "" ).replace( "</em>", "" ) # Get rid of bolds, this tends to be used just to highlight the keyword searched
	resultOneUnparsed = strbetween( datlongtext, "<h3 class=\"r\">", "</h3>" ) # The link and result text come between this
	datlongtext = datlongtext.replace( "<h3 class=\"r\">" + resultOneUnparsed + "</h3>", "" ) # Now that we got the first one, get rid of it to find the next one
	resultTwoUnparsed = strbetween( datlongtext, "<h3 class=\"r\">", "</h3>" )
	datlongtext = datlongtext.replace( "<h3 class=\"r\">" + resultTwoUnparsed + "</h3>", "" )
	resultThreeUnparsed = strbetween( datlongtext, "<h3 class=\"r\">", "</h3>" )
	datlongtext = datlongtext.replace( "<h3 class=\"r\">" + resultThreeUnparsed + "</h3>", "" )
	# Great, now we've got the three results isolated. Let's parse them!
	resultOneLink = strbetween( resultOneUnparsed, "<a href=\"/url?q=", "&amp;sa=U" )
	resultTwoLink = strbetween( resultTwoUnparsed, "<a href=\"/url?q=", "&amp;sa=U" )
	resultThreeLink = strbetween( resultThreeUnparsed, "<a href=\"/url?q=", "&amp;sa=U" )
	resultOneText = strbetween( resultOneUnparsed, "\">", "</a>" )
	resultTwoText = strbetween( resultTwoUnparsed, "\">", "</a>" )
	resultThreeText = strbetween( resultThreeUnparsed, "\">", "</a>" )
	if resultOneLink != "" and resultOneText != "":
		__main__.sendMessage( htmlCleaner( resultOneText ) + " - " + htmlCleaner( resultOneLink ), recvfrom )
	if resultTwoLink != "" and resultTwoText != "":
		threading.Timer( 0.5, __main__.sendMessage, args=( htmlCleaner( resultTwoText ) + " - " + htmlCleaner( resultTwoLink ), recvfrom ) ).start()
	if resultThreeLink != "" and resultThreeText != "":
		threading.Timer( 1.0, __main__.sendMessage, args=( htmlCleaner( resultThreeText ) + " - " + htmlCleaner( resultThreeLink ), recvfrom ) ).start()
	return True


def htmlCleaner( link ): # Remove or replace any special characters
	link = fixHTMLCharsAdvanced( link ) # Start with the usual stuff
	link = link.replace( "%3F", "?" )
	link = link.replace( "%3D", "=" )
	return link
