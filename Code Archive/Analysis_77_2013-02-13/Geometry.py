# Geometry
#
# This is a container class for vectors and volumes.
#
# Last Modified 2013.01.16 22:11
#


import math


class TwoVector:
	
	def __init__(This, X = None, Y = None):
		
		This.X = X
		This.Y = Y
		
	def Modulus(This):
		
		M = 0
		
		if (not (This.X == None) and not (This.Y == None)):
			M = math.sqrt(This.X * This.X + This.Y * This.Y)			
		
		return M
				
	def Direction(This):
		
		TwoVector1 = TwoVector()
		
		if (not (This.Modulus() == 0) and not (This.X == None) and not (This.Y == None)):
		
			TwoVector1.X = This.X / This.Modulus()
			TwoVector1.Y = This.Y / This.Modulus()
		
		return TwoVector1
	
	def InvertDirection(This):
		
		if (not (This.X == None) and not (This.Y == None)):
			This.X = - This.X
			This.Y = - This.Y
		
	def __add__(This, Other):
		
		TwoVector1 = TwoVector()
		
		if (not (This.X == None) and not (This.Y == None) and not (Other.X == None) and not (Other.Y == None)):
			TwoVector1.X = This.X + Other.X
			TwoVector1.Y = This.Y + Other.Y
		
		return TwoVector1
		
	def __sub__(This, Other):
		
		TwoVector1 = TwoVector()
		
		if (not (This.X == None) and not (This.Y == None) and not (Other.X == None) and not (Other.Y == None)):
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
	
	def ToTwoVector(This):
		
		TwoVector1 = TwoVector()
		
		TwoVector1.X = This.X
		TwoVector1.Y = This.Y
		
		return TwoVector1

def ScalarProduct(Vector1, Vector2):
	
	Scalar1 = Vector1.X * Vector2.X + Vector1.Y * Vector2.Y + Vector1.Z * Vector2.Z
	
	return Scalar1

def FindAngle(Vector1, Vector2):
	
	Theta1 = math.acos((ScalarProduct(Vector1, Vector2)) / (Vector1.Modulus() * Vector2.Modulus())) * 360 / (2 * math.pi)
	
	return Theta1

def WithinLocality(Point1, Point2, LocalityLimit):
	
	WithinLocality = False
	
	if ((math.fabs(Point1.X - Point2.X) < LocalityLimit) and (math.fabs(Point1.Y - Point2.Y) < LocalityLimit) and (math.fabs(Point1.Z - Point2.Z) < LocalityLimit)):
		WithinLocality = True
		
	return WithinLocality

def AverageLocation(FourVector1, FourVector2):
	
	AverageFourVector1 = FourVector()
	
	AverageFourVector1.T = float(FourVector1.T + FourVector2.T) / 2
	AverageFourVector1.X = float(FourVector1.X + FourVector2.X) / 2
	AverageFourVector1.Y = float(FourVector1.Y + FourVector2.Y) / 2
	AverageFourVector1.Z = float(FourVector1.Z + FourVector2.Z) / 2
	
	return AverageFourVector1


class FourVector:
	
	def __init__(This, T = 0, X = 0, Y = 0, Z = 0):
		
		This.T = float(T)
		This.X = float(X)
		This.Y = float(Y)
		This.Z = float(Z)
	
	def Modulus(This):
		
		return This.SpatialModulus()
	
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
	
	def ToThreeVector(This):
		
		ThreeVector1 = ThreeVector()
		
		ThreeVector1.X = This.X
		ThreeVector1.Y = This.Y
		ThreeVector1.Z = This.Z
		
		return ThreeVector1


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
		
