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
import sys, traceback

def getExceptionTraceback( exc ):
	test = sys.exc_info()
	ret = ""
	if test and test[2]:
		for formatted in traceback.format_exception( type( exc ), exc, test[2] ):
			ret += str( formatted )
	else:
		ret = str( traceback.format_exception_only( type( exc ), exc )[-1] )
	return ret
