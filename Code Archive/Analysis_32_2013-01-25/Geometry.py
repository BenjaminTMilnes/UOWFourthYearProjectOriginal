# Geometry
#
# This is a container class for four-component vectors.
#
# Last Modified 2013.01.16 22:11
#

import math

class FourVector:
	
	def __init__(self, T = 0, X = 0, Y = 0, Z = 0):
		
		self.T = float(T)
		self.X = float(X)
		self.Y = float(Y)
		self.Z = float(Z)
		
	def SpatialModulus(self):
		
		M = math.sqrt(self.X * self.X + self.Y * self.Y + self.Z * self.Z)
		
		return M
		
	def InvariantModulus(self):
		
		IM = 0
		
		if (self.T > self.SpatialModulus()):
			# Avoid trying to compute the square-root of negative numbers
			
			IM = math.sqrt(self.T * self.T - self.X * self.X - self.Y * self.Y - self.Z * self.Z)
				
		return IM


class ThreeVector:
	
	def __init__(self, X = 0, Y = 0, Z = 0):
		
		self.X = float(X)
		self.Y = float(Y)
		self.Z = float(Z)
		
	def Modulus(self):
		
		M = math.sqrt(self.X * self.X + self.Y * self.Y + self.Z * self.Z)
		
		return M

def ScalarProduct(Vector1, Vector2):
	
	Scalar1 = Vector1.X * Vector2.X + Vector1.Y * Vector2.Y + Vector1.Z * Vector2.Z
	
	return Scalar1

def FindAngle(Vector1, Vector2):
	
	Theta1 = math.acos((ScalarProduct(Vector1, Vector2)) / (Vector1.Modulus() * Vector2.Modulus())) * 360 / (2 * math.pi)
	
	return Theta1
	
	

