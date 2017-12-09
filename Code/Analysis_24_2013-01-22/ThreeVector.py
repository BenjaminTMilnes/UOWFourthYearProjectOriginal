# Three-Vector
#
# This is a container class for three-component vectors.
#
# Modified 2013.01.13 22:21
# Last Modified 2013.01.13 22:45
#

import math

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
	
	Theta1 = math.asin((ScalarProduct(Vector1, Vector2)) / (Vector1.Modulus() * Vector2.Modulus())) * 360 / (2 * math.pi)
	
	return Theta1
	
	
