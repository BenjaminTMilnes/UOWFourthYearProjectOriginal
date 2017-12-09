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
				
	def Direction(This):
		
		TwoVector1 = TwoVector()
		
		if not (This.Modulus() == 0):
		
			TwoVector1.X = This.X / This.Modulus()
			TwoVector1.Y = This.Y / This.Modulus()
		
		return TwoVector1
	
	def InvertDirection(This):
		
		This.X = - This.X
		This.Y = - This.Y
		
	def __add__(This, Other):
		
		TwoVector1 = TwoVector()
		
		TwoVector1.X = This.X + Other.X
		TwoVector1.Y = This.Y + Other.Y
		
		return TwoVector1
		
	def __sub__(This, Other):
		
		TwoVector1 = TwoVector()
		
		TwoVector1.X = This.X - Other.X
		TwoVector1.Y = This.Y - Other.Y
		
		return TwoVector1


class ThreeVector:
	
	def __init__(This, X = 0, Y = 0, Z = 0):
		
		This.X = float(X)
		This.Y = float(Y)
		This.Z = float(Z)
		
	def Modulus(This):
		
		M = math.sqrt(This.X * This.X + This.Y * This.Y + This.Z * This.Z)
		
		return M
				
	def Direction(This):
		
		ThreeVector1 = ThreeVector()
		
		if not (This.Modulus() == 0):
		
			ThreeVector1.X = This.X / This.Modulus()
			ThreeVector1.Y = This.Y / This.Modulus()
			ThreeVector1.Z = This.Z / This.Modulus()
		
		return ThreeVector1
	
	def InvertDirection(This):
		
		This.X = - This.X
		This.Y = - This.Y
		This.Z = - This.Z
		
	def __add__(This, Other):
		
		ThreeVector1 = ThreeVector()
		
		ThreeVector1.X = This.X + Other.X
		ThreeVector1.Y = This.Y + Other.Y
		ThreeVector1.Z = This.Z + Other.Z
		
		return ThreeVector1
		
	def __sub__(This, Other):
		
		ThreeVector1 = ThreeVector()
		
		ThreeVector1.X = This.X - Other.X
		ThreeVector1.Y = This.Y - Other.Y
		ThreeVector1.Z = This.Z - Other.Z
		
		return ThreeVector1

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
		
	def SpatialDirection(This):
		
		FourVector1 = FourVector()
		
		if not (This.SpatialModulus() == 0):
		
			FourVector1.X = This.X / This.SpatialModulus()
			FourVector1.Y = This.Y / This.SpatialModulus()
			FourVector1.Z = This.Z / This.SpatialModulus()
		
		return FourVector1
	
	def InvertSpatialDirection(This):
		
		This.X = - This.X
		This.Y = - This.Y
		This.Z = - This.Z
		
	def E(This):		
		return This.T
		
	def MX(This):		
		return This.X
		
	def MY(This):		
		return This.Y
		
	def MZ(This):		
		return This.Z
		
	def __add__(This, Other):
		
		FourVector1 = FourVector()
		
		FourVector1.T = This.T + Other.T
		FourVector1.X = This.X + Other.X
		FourVector1.Y = This.Y + Other.Y
		FourVector1.Z = This.Z + Other.Z
		
		return FourVector1
		
	def __sub__(This, Other):
		
		FourVector1 = FourVector()
		
		FourVector1.T = This.T - Other.T
		FourVector1.X = This.X - Other.X
		FourVector1.Y = This.Y - Other.Y
		FourVector1.Z = This.Z - Other.Z
		
		return FourVector1
				
		


class ThreeDimensionalObject:
	
	def __init__(This, X1 = 0, X2 = 0, Y1 = 0, Y2 = 0, Z1 = 0, Z2 = 0):
		
		This.X1 = X1
		This.X2 = X2
		
		This.Y1 = Y1
		This.Y2 = Y2
		
		This.Z1 = Z1
		This.Z2 = Z2
		
	def Contains(This, X, Y, Z):
		
		IsContained = False
		
		if ((X > This.X1) and (X < This.X2) and (Y > This.Y1) and (Y < This.Y2) and (Z > This.Z1) and (Z < This.Z2)):
			IsContained = True
		
		return IsContained
		
