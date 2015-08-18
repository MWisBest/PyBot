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
import __main__, html.parser

def strbetween( s, first, last ):
	try:
		start = s.index( first ) + len( first )
		return s[start:s.index( last, start )]
	except:
		return ""


def fixHTMLChars( toFix ):
	toFix = toFix.replace( "&nbsp;", " " ) # Rather than have a weird character, use a regular fkin space
	return html.parser.HTMLParser().unescape( toFix )

def fixHTMLCharsAdvanced( toFix ):
	toFix = toFix.replace( "&nbsp;", " " ) # Rather than have a weird character, use a regular fkin space
	toFix = html.parser.HTMLParser().unescape( toFix )
	# replace linebreaks with spaces
	toFix = toFix.replace( "<br/>", " " ).replace( "\n", " " ).replace( "\r", " " )
	if "<a href=" in toFix:
		toFix = toFix.replace( "</a>", "" )
		while "<a href=" in toFix:
			toReplace = strbetween( toFix, "<a href=", ">" )
			toFix = toFix.replace( "<a href=" + toReplace + ">", "" )
	while "  " in toFix: # We don't want two or more spaces used for breaks
		toFix = toFix.replace( "  ", " " )
	return toFix
