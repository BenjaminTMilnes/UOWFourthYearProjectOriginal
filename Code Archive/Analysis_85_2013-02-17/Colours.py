########################################################################################################################
####
#### COLOURS
####
#### This module contains constants and functions for controlling the colour-content of charts.
#### 
#### At the moment the random colours functionality doesn't exist; it may not be necessary. The
#### module contains artificial constants for the colours, which are copied into dictionaries
#### so that they can be looped over. There is a function which can give you a dictionary of
#### colour numbers based on a list of references you give it, which can be used to associated
#### particles or processes with colours consistently.
#### 
#### Modified 2013.02.11 11:55 - 13:16, Completed
#### Modified 2013.02.11 16:27, Completed
#### 
########################################################################################################################


import random


########################################################################################################################

White = 0
Black = 1
Red = 2
Lime = 3
Azure = 4
Yellow = 5
Pink = 6
Turquoise = 7
Green = 8
Blue = 9
DarkGrey = 12
Grey = 14
LightGrey = 17
Stone = 27
Brown = 28
Mint = 29
Forest = 30
Fern = 32
Teal = 34
Rain = 37
Sky = 38
Sea = 39
Silver = 40
Honey = 41
Sand = 42
Clay = 43
Umber = 44
BurntUmber = 45
Redwood = 46
Chrome = 47
Mauve = 48
Purple = 49

Default = Silver

Collection = {}

Collection["White"] = White
Collection["Black"] = Black
Collection["Red"] = Red
Collection["Lime"] = Lime
Collection["Azure"] = Azure
Collection["Yellow"] = Yellow
Collection["Pink"] = Pink
Collection["Turquoise"] = Turquoise
Collection["Green"] = Green
Collection["Blue"] = Blue
Collection["DarkGrey"] = DarkGrey
Collection["Grey"] = Grey
Collection["LightGrey"] = LightGrey
Collection["Stone"] = Stone
Collection["Brown"] = Brown
Collection["Mint"] = Mint
Collection["Forest"] = Forest
Collection["Fern"] = Fern
Collection["Teal"] = Teal
Collection["Rain"] = Rain
Collection["Sky"] = Sky
Collection["Sea"] = Sea
Collection["Silver"] = Silver
Collection["Honey"] = Honey
Collection["Sand"] = Sand
Collection["Clay"] = Clay
Collection["Umber"] = Umber
Collection["BurntUmber"] = BurntUmber
Collection["Redwood"] = Redwood
Collection["Chrome"] = Chrome
Collection["Mauve"] = Mauve
Collection["Purple"] = Purple

PastelCollection = {}

PastelCollection["DarkGrey"] = DarkGrey
PastelCollection["Grey"] = Grey
PastelCollection["LightGrey"] = LightGrey
PastelCollection["Stone"] = Stone
PastelCollection["Brown"] = Brown
PastelCollection["Mint"] = Mint
PastelCollection["Forest"] = Forest
PastelCollection["Fern"] = Fern
PastelCollection["Teal"] = Teal
PastelCollection["Rain"] = Rain
PastelCollection["Sky"] = Sky
PastelCollection["Sea"] = Sea
PastelCollection["Silver"] = Silver
PastelCollection["Honey"] = Honey
PastelCollection["Sand"] = Sand
PastelCollection["Clay"] = Clay
PastelCollection["Umber"] = Umber
PastelCollection["BurntUmber"] = BurntUmber
PastelCollection["Redwood"] = Redwood
PastelCollection["Chrome"] = Chrome
PastelCollection["Mauve"] = Mauve
PastelCollection["Purple"] = Purple

BlueGreenCollection = {}

BlueGreenCollection["Black"] = Black
BlueGreenCollection["Lime"] = Lime
BlueGreenCollection["Azure"] = Azure
BlueGreenCollection["Turquoise"] = Turquoise
BlueGreenCollection["Green"] = Green
BlueGreenCollection["Blue"] = Blue
BlueGreenCollection["DarkGrey"] = DarkGrey
BlueGreenCollection["Grey"] = Grey
BlueGreenCollection["LightGrey"] = LightGrey
BlueGreenCollection["Mint"] = Mint
BlueGreenCollection["Forest"] = Forest
BlueGreenCollection["Fern"] = Fern
BlueGreenCollection["Teal"] = Teal
BlueGreenCollection["Rain"] = Rain
BlueGreenCollection["Sky"] = Sky
BlueGreenCollection["Sea"] = Sea
BlueGreenCollection["Silver"] = Silver

def DistinguishableColourSet(NumberOfColours = 10, PastelColours = True, RandomColours = False):
	
	# Returns a list of colour numbers, of specified length, from the collection.
	
	ColourSet1 = []
	
	n1 = 0
			
	if (PastelColours == True):
		for Colour1 in PastelCollection:
			if (n1 < NumberOfColours):
				ColourSet1.append(Colour1)
				n1 += 1
	else:			
		for Colour1 in Collection:
			if (n1 < NumberOfColours):
				ColourSet1.append(Colour1)
				n1 += 1
	
	return ColourSet1

def ConsistentColourSet(References = [], PastelColours = True, RandomColours = False):

	# Returns a dictionary of colours associated to given references. The dictionary can then be used to consistently pair colours across graphs.
	
	ColourSet1 = []
	Collection1 = {}
	
	n1 = 0
	
	if (PastelColours == True):	
		for Colour1 in PastelCollection:
			ColourSet1.append(Colour1)	
	else:
		for Colour1 in Collection:
			ColourSet1.append(Colour1)
	
	for Reference1 in References:
		Collection1[Reference1] = ColourSet1[n1]
		n1 += 1
	
	return Collection1


PersistentColours = {}

def PersistentColour(Reference, PastelColours = True, RandomColours = False):
	
	# This function takes a reference and assigns a colour to it, which persists throughout the program.
	
	# Note that at the moment this function is limited to the total number of colours, and will otherwise return a default colour.
	
	Response = Blue
	
	if Reference in PersistentColours:
		Response = PersistentColours[Reference]
	else:
		if (PastelColours == True):
			for Colour1 in PastelCollection.values():
				if (not (Colour1 in PersistentColours.values())):
					PersistentColours[Reference] = Colour1
					Response = Colour1			
		else:
			for Colour1 in Collection.values():
				if (not (Colour1 in PersistentColours.values())):
					PersistentColours[Reference] = Colour1
					Response = Colour1
			
	return Response
