# Geometry
#
# This is a container class for vectors and volumes.
#
# Last Modified 2013.01.16 22:11
#


import math


class TwoVector:
	
	def __init__(This, X = 0, Y = 0):
		
		This.X = float(X)
		This.Y = float(Y)
		
	def Modulus(This):
		
		M = math.sqrt(This.X * This.X + This.Y * This.Y)
		
		return M


class ThreeVector:
	
	def __init__(This, X = 0, Y = 0, Z = 0):
		
		This.X = float(X)
		This.Y = float(Y)
		This.Z = float(Z)
		
	def Modulus(This):
		
		M = math.sqrt(This.X * This.X + This.Y * This.Y + This.Z * This.Z)
		
		return M

def ScalarProduct(Vector1, Vector2):
	
	Scalar1 = Vector1.X * Vector2.X + Vector1.Y * Vector2.Y + Vector1.Z * Vector2.Z
	
	return Scalar1

def FindAngle(Vector1, Vector2):
	
	Theta1 = math.acos((ScalarProduct(Vector1, Vector2)) / (Vector1.Modulus() * Vector2.Modulus())) * 360 / (2 * math.pi)
	
	return Theta1


class FourVector:
	
	def __init__(This, T = 0, X = 0, Y = 0, Z = 0):
		
		This.T = float(T)
		This.X = float(X)
		This.Y = float(Y)
		This.Z = float(Z)
		
	def SpatialModulus(This):
		
		M = math.sqrt(This.X * This.X + This.Y * This.Y + This.Z * This.Z)
		
		return M
		
	def InvariantModulus(This):
		
		IM = 0
		
		if (This.T > This.SpatialModulus()):
			# Avoid trying to compute the square-root of negative numbers
			
			IM = math.sqrt(This.T * This.T - This.X * This.X - This.Y * This.Y - This.Z * This.Z)
				
		return IM


class ThreeDimensionalObject:
	
	def __init__(This, X1 = 0, X2 = 0, Y1 = 0, Y2 = 0, Z1 = 0, Z2 = 0):
		
		This.X1 = X1
		This.X2 = X2
		
		This.Y1 = Y1
		This.Y2 = Y2
		
		This.Z1 = Z1
		This.Z2 = Z2
		
	def Contains(This, Point):
		
		IsContained = False
		
		if ((Point.X > This.X1) and (Point.X < This.X2) and (Point.Y > This.Y1) and (Point.Y < This.Y1) and (Point.Z > This.Z1) and (Point.Z < This.Z1)):
			IsContained = True
		
		return IsContained
		


