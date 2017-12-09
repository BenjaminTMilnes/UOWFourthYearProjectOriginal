# Three-Dimensional Object
#
# This is a container class for three-dimensional objects.
#
# Last Modified 2013.01.13 22:24
#

import ThreeVector

class ThreeDimensionalObject:
	
	def __init__(self, X1 = 0, X2 = 0, Y1 = 0, Y2 = 0, Z1 = 0, Z2 = 0):
		
		self.X1 = X1
		self.X2 = X2
		
		self.Y1 = Y1
		self.Y2 = Y2
		
		self.Z1 = Z1
		self.Z2 = Z2
		
	def Contains(self, Point):
		
		IsContained = False
		
		if ((Point.X > self.X1) and (Point.X < self.X2) and (Point.Y > self.Y1) and (Point.Y < self.Y1) and (Point.Z > self.Z1) and (Point.Z < self.Z1)):
			IsContained = True
		
		return IsContained
		
