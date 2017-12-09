# Selections
#
# This class represents the selections we wish to make on the data for a particular event.
#
# Modified: 2013.01.28 09:24
#

class Selections:
	
	def __init__(This):
		
		This.NReconstructedObjectsIsMoreThan0 = False
		This.NTPCNodesIsMoreThan18 = False
		This.NReconstructedProtonsIsMoreThan0 = False
		This.NReconstructedProtonsIs1 = False
		This.ProtonTrackIsFirstInDetector = False
		This.ProtonTrackStartsInFGD = False
		This.NReconstructedObjectsIsLessThan00 = False
		This.NECReconstructedPhotonsIsMoreThan0 = False
		This.MinimumPhotonAngleIsLessThan00 = False
		This.InvariantMass = False

	def Redetermine(This):
		
		This.NumberOfReconstructedObjectsIsMoreThan0
