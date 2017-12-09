########################################################################################################################
####
#### PDG PARTICLE CODES
####
#### This module contains integer constants which hold the PDG codes for particles. Not all particles 
#### are included. It also contains functions to evaluate whether a particle with a given PDG code
#### belongs to a group of particles like the leptons or quarks.
####
#### Modified 2012.11.21
#### Modified 2013.01.13 19:44
#### Modified 2013.02.12 13:40
#### Modified 2013.02.13 10:52
####
########################################################################################################################

DownQuark = 1
UpQuark = 2
StrangeQuark = 3
CharmQuark = 4
BottomQuark = 5
TopQuark = 6

Photon = 22

ZZero = 23
WPlus = 24
WMinus = -24

Electron = 11
AntiElectron = -11
ElectronNeutrino = 12
ElectronAntiNeutrino = -12

MuLepton = 13
AntiMuLepton = -13
MuNeutrino = 14
MuAntiNeutrino = -14

TauLepton = 15
AntiTauLepton = -15
TauNeutrino = 16
TauAntiNeutrino = -16

Pi00Meson = -211 # Where 00 corresponds to a charge of -1.
Pi0Meson = 111
Pi1Meson = 211

Neutron = 2112
Proton = 2212

Delta00Baryon = 1114 # Where 00 corresponds to a charge of -1.
Delta0Baryon = 2114
Delta1Baryon = 2214
Delta2Baryon = 2224

K1Meson = 321
K1AntiMeson = -321

Collection = {}

QuarkCollection = {}
LeptonCollection = {}

NeutrinoCollection = {}

Collection["DownQuark"] = DownQuark
Collection["UpQuark"] = UpQuark
Collection["StrangeQuark"] = StrangeQuark
Collection["CharmQuark"] = CharmQuark
Collection["BottomQuark"] = BottomQuark
Collection["TopQuark"] = TopQuark
Collection["Photon"] = Photon
Collection["ZZero"] = ZZero
Collection["WPlus"] = WPlus
Collection["WMinus"] = WMinus
Collection["Electron"] = Electron
Collection["AntiElectron"] = AntiElectron
Collection["ElectronNeutrino"] = ElectronNeutrino
Collection["ElectronAntiNeutrino"] = ElectronAntiNeutrino
Collection["MuLepton"] = MuLepton
Collection["AntiMuLepton"] = AntiMuLepton
Collection["MuNeutrino"] = MuNeutrino
Collection["MuAntiNeutrino"] = MuAntiNeutrino
Collection["TauLepton"] = TauLepton
Collection["AntiTauLepton"] = AntiTauLepton
Collection["TauNeutrino"] = TauNeutrino
Collection["TauAntiNeutrino"] = TauAntiNeutrino
Collection["Pi00Meson"] = Pi00Meson
Collection["Pi0Meson"] = Pi0Meson
Collection["Pi1Meson"] = Pi1Meson
Collection["Neutron"] = Neutron
Collection["Proton"] = Proton
Collection["Delta00Baryon"] = Delta00Baryon
Collection["Delta0Baryon"] = Delta0Baryon
Collection["Delta1Baryon"] = Delta1Baryon
Collection["Delta2Baryon"] = Delta2Baryon
Collection["K1Meson"] = K1Meson
Collection["K1AntiMeson"] = K1AntiMeson

QuarkCollection["DownQuark"] = DownQuark
QuarkCollection["UpQuark"] = UpQuark
QuarkCollection["StrangeQuark"] = StrangeQuark
QuarkCollection["CharmQuark"] = CharmQuark
QuarkCollection["BottomQuark"] = BottomQuark
QuarkCollection["TopQuark"] = TopQuark

LeptonCollection["Electron"] = Electron
LeptonCollection["AntiElectron"] = AntiElectron
LeptonCollection["ElectronNeutrino"] = ElectronNeutrino
LeptonCollection["ElectronAntiNeutrino"] = ElectronAntiNeutrino
LeptonCollection["MuLepton"] = MuLepton
LeptonCollection["AntiMuLepton"] = AntiMuLepton
LeptonCollection["MuNeutrino"] = MuNeutrino
LeptonCollection["MuAntiNeutrino"] = MuAntiNeutrino
LeptonCollection["TauLepton"] = TauLepton
LeptonCollection["AntiTauLepton"] = AntiTauLepton
LeptonCollection["TauNeutrino"] = TauNeutrino
LeptonCollection["TauAntiNeutrino"] = TauAntiNeutrino

NeutrinoCollection["ElectronNeutrino"] = ElectronNeutrino
NeutrinoCollection["ElectronAntiNeutrino"] = ElectronAntiNeutrino
NeutrinoCollection["MuNeutrino"] = MuNeutrino
NeutrinoCollection["MuAntiNeutrino"] = MuAntiNeutrino
NeutrinoCollection["TauNeutrino"] = TauNeutrino
NeutrinoCollection["TauAntiNeutrino"] = TauAntiNeutrino


def IsQuark(Code):
	
	Response = False
	
	for Code1 in QuarkCollection:
		if (Code1 == Code):
			Response = True
	
	return Response

	
def IsLepton(Code):
	
	Response = False
	
	for Code1 in LeptonCollection:
		if (Code1 == Code):
			Response = True
	
	return Response


def IsNeutrino(Code):
	
	Response = False
	
	for Code1 in NeutrinoCollection:
		if (Code1 == Code):
			Response = True
	
	return Response





ParticleDictionary = {}

for Variable in dir():

	if (isinstance(eval(Variable), int)):
		ParticleDictionary[eval(Variable)] = Variable
	

