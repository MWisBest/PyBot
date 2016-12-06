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
import __main__, ast, operator, pybotutils

#################################################################
## THIS COMMAND IS BASED ON http://stackoverflow.com/a/9558001 ##
#################################################################

# Access is limited to Trusted users until this function is verified to be safe (probably never)
info = { "names" : [ "calc", "calculator" ], "access" : 1, "version" : 1 }

# Constants to adjust calculation limits.
POW_LEFT_MAX    = 1 << 63
POW_RIGHT_MAX   = 1 << 10
SHIFT_RIGHT_MAX = 1 <<  6


class OperatorError( Exception ):
	"""Exception raised for unsupported calculation operands.
	
	Attributes:
		node -- node in which the error occurred
	"""
	def __init__( self, node ):
		self.node = node

class UnsafeOperatorError( Exception ):
	"""Exception raised for unsafe calculation values.
	
	Attributes:
		message -- error message
	"""
	def __init__( self, message ):
		self.message = message


def safeLShift( left, right ):
	if abs( right ) > SHIFT_RIGHT_MAX:
		raise UnsafeOperatorError( "'<< X' cannot exceed " + str( SHIFT_RIGHT_MAX ) )
	return operator.__lshift__( left, right )

def safeRShift( left, right ):
	if abs( right ) > SHIFT_RIGHT_MAX:
		raise UnsafeOperatorError( "'>> X' cannot exceed " + str( SHIFT_RIGHT_MAX ) )
	return operator.__rshift__( left, right )

def safePow( left, right ):
	if abs( right ) > POW_RIGHT_MAX:
		raise UnsafeOperatorError( "'** X' cannot exceed " + str( POW_RIGHT_MAX ) )
	elif abs( left ) > POW_LEFT_MAX:
		raise UnsafeOperatorError( "'X **' cannot exceed " + str( POW_LEFT_MAX ) )
	return operator.__pow__( left, right )


op_map = {
	ast.Add  : operator.__add__,          # +
	ast.Sub  : operator.__sub__,          # -
	ast.Mult : operator.__mul__,          # *
	ast.Div  : operator.__truediv__,      # /
	ast.FloorDiv : operator.__floordiv__, # //
	ast.Mod : operator.__mod__,           # %
	ast.Pow : safePow,                    # **: WARNING: POTENTIALLY UNSAFE
	ast.BitAnd : operator.__and__,        # &
	ast.BitOr : operator.__or__,          # |
	ast.BitXor : operator.__xor__,        # ^
	ast.Invert : operator.__invert__,     # ~
	ast.LShift : safeLShift,              # <<: WARNING: POTENTIALLY UNSAFE
	ast.RShift : safeRShift,              # >>: WARNING: POTENTIALLY UNSAFE
	ast.UAdd : operator.pos,              # e.g. +100
	ast.USub : operator.neg               # e.g. -100
}

def calculate( message ):
	return calc_( ast.parse( message, mode="eval" ).body )

def calc_( node ):
	if isinstance( node, ast.Num ):
		return node.n
	elif isinstance( node, ast.BinOp ):
		if type( node.op ) in op_map:
			return op_map[type( node.op )]( calc_( node.left ), calc_( node.right ) )
	elif isinstance( node, ast.UnaryOp ):
		if type( node.op ) in op_map:
			return op_map[type( node.op )]( calc_( node.operand ) )
	else:
		# Unknown node instance, TypeError
		raise TypeError( node )
	# Was known instance, but invalid operator
	raise OperatorError( node )


def command( message, user, recvfrom ):
	try:
		try:
			ret = str( calculate( message ) )
		except UnsafeOperatorError as unsafe_err:
			ret = "Unsafe operation: " + unsafe_err.message
		except OperatorError as op_err:
			ret = "Unsupported operator: " + op_err.node.op.__class__.__name__
		except (SyntaxError, TypeError):
			ret = "Invalid syntax."
		except ZeroDivisionError:
			ret = "Not Chuck Norris: Cannot Divide By Zero!"
		except:
			ret = "Unknown error occurred."
		
		if ret == "":
			ret = "Fix your shit."
		elif len( ret ) > 100:
			ret = "That's wayyyy too many digits bro."
		__main__.sendMessage( ret, recvfrom )
		return True
	except Exception as err:
		__main__.errorprint( "calc error!" )
		__main__.warnprint( pybotutils.getExceptionTraceback( err ) )
	return False
