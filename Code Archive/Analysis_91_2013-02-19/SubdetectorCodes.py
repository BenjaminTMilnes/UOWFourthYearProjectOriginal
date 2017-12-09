########################################################################################################################
####
#### SUBDETECTOR CODES
####
########################################################################################################################

P0D = 6 # Pi-0 Detector

TPC1 = 1 # Time Projection Chambers
TPC2 = 2
TPC3 = 3

FGD1 = 4 # Fine-Grained Detectors
FGD2 = 5

TEC = 9 # Tracker Electromagnetic Calorimeter
DSEC = 7 # Down-Stream Electromagnetic Calorimeter

SMRD = 8 # Side Muon Range Detector

Subdetectors = {}

Subdetectors["P0D"] = str(P0D)
Subdetectors["TPC1"] = str(TPC1)
Subdetectors["TPC2"] = str(TPC2)
Subdetectors["TPC3"] = str(TPC3)
Subdetectors["FGD1"] = str(FGD1)
Subdetectors["FGD2"] = str(FGD2)
Subdetectors["TEC"] = str(TEC)
Subdetectors["DSEC"] = str(DSEC)
Subdetectors["SMRD"] = str(SMRD)

# Transitional:

Subdetectors["DSECal"] = str(DSEC)
Subdetectors["TrackerECal"] = str(TEC)

#

FGDs = {}

FGDs["1"] = FGD1
FGDs["2"] = FGD2

TPCs = {}

TPCs["1"] = TPC1
TPCs["2"] = TPC2
TPCs["3"] = TPC3
