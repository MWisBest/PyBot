###########################################################################
## PyBot                                                                 ##
## Copyright (C) 2016, Kyle Repinski                                     ##
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
import __main__, base64

def inputSettings():
	__main__.database['api']['ircsettings']['network']  = input( "Please enter the address of the IRC network you want to connect to.\n" )
	__main__.database['api']['ircsettings']['port']     = int( input( "Please enter the port while you're at it!\n" ) )
	__main__.database['api']['ircsettings']['nick']     = input( "Please enter a valid (NO STUPID SYMBOLS) IRC nick for your bot.\n" ).replace( " ", "_" ).replace( ".", "_" ).replace( ",", "_" )
	__main__.database['api']['ircsettings']['password'] = base64.b85encode( ( input( "Please enter your bot's NickServ password if required, otherwise leave this blank.\n" ) ).encode( "utf-8" ), pad=True )
	__main__.database['api']['ircsettings']['channels'] = [ input( "Please enter the initial channel that your bot will be joining.\n" ) ]
