# PDG Particle Code Constants
#
# This file contains integer constants which hold the PDG codes for particles. Not all particles are included.
#
# Modified 2012.11.21
# Last Modified 2013.01.13 19:44
#

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

ParticleDictionary = {}

for Variable in dir():

	if (isinstance(eval(Variable), int)):
		ParticleDictionary[eval(Variable)] = Variable
	

