import libraries
import glob
import sys
import ROOT
import RooTrackerTools
import math
import datetime
import os

import EventCodeDeconstructor
import DataWriter
import TheoreticalParticle
import ParticleCodes

Now = datetime.datetime.now()
DataLocation = "/storage/epp2/phujce/Final Year Project/Main/Data Archive/"

Proton = TheoreticalParticle.TheoreticalParticle(938.272046, ParticleCodes.Proton)

ProtonRestEnergy=938.272046#From wikipedia

NewLine = "\n"
LineSeparator = "----------------------------------------"

class Analysis:
	
	def __init__(self, InputFileLocatorList, OutputROOTFileLocator, OutputTextFileLocator):
		
		self.InputFileLocatorList = InputFileLocatorList
		self.OutputROOTFileLocator = OutputROOTFileLocator
		self.OutputTextFileLocator= OutputTextFileLocator
		
		self.Histograms = {}
		self.Modules = []
		
		self.BasicInformation = self.LoadModule("HeaderDir/BasicHeader")
		
		self.Truth_GRTVertices = self.LoadModule("TruthDir/GRooTrackerVtx")
		self.Truth_Vertices = self.LoadModule("TruthDir/Vertices")
		self.Truth_Trajectories = self.LoadModule("TruthDir/Trajectories")
		
		self.Reconstructed_Global = self.LoadModule("ReconDir/Global")
		self.Reconstructed_TEC = self.LoadModule("ReconDir/TrackerECal")
		
		self.RTTools = RooTrackerTools.RooTrackerTools()
		
		self.DeltaPGammaTotal=0
		self.DeltaPGammaCC=0
		self.DeltaPGammaNC=0
		self.DeltaPGammaTotalinFGD=0
		self.DeltaPGammaCCinFGD=0
		self.DeltaPGammaNCinFGD=0
		self.VerticesCount=0
		self.ReconstructedPIDsNumber=0
		self.ReconstructedProtonTrack=0
		self.ProtonCorrectlyReconstructed=0
		self.ProtonTrackFirst=0
		self.ECalNumber=0
		self.ProtonAndECal=0
			
			
			
	def NewHistogram1D(self, Reference, Title, XAxisTitle, YAxisTitle, NumberOfBinsX, MinimumX, MaximumX):
		
		self.Histograms[Reference] = ROOT.TH1D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX)
		self.Histograms[Reference].SetXTitle(XAxisTitle)
		self.Histograms[Reference].SetYTitle(YAxisTitle)
	
	
	def NewHistogram2D(self, Reference, Title, XAxisTitle, YAxisTitle, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY):
		
		self.Histograms[Reference] = ROOT.TH2D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY)
		self.Histograms[Reference].SetXTitle(XAxisTitle)
		self.Histograms[Reference].SetYTitle(YAxisTitle)
	
	
	def NewHistogram3D(self, Reference, Title, XAxisTitle, YAxisTitle, ZAxisTitle, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY, NumberOfBinsZ, MinimumZ, MaximumZ):
		
		self.Histograms[Reference] = ROOT.TH3D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY, NumberOfBinsZ, MinimumZ, MaximumZ)
		self.Histograms[Reference].SetXTitle(XAxisTitle)
		self.Histograms[Reference].SetYTitle(YAxisTitle)
		self.Histograms[Reference].SetZTitle(ZAxisTitle)
			
					
	def NewHistogram1DStack(self, Reference, Title):
		
		self.Histograms[Reference] = ROOT.THStack(Reference, Title)
				
	
	
	
	def LoadInputFiles(self):		
		# Adds each file in the list of input file names to each module we want to use		
		
		for FileLocator in self.InputFileLocatorList:
			for Module in self.Modules:
				Module.Add(FileLocator)
		
		
	def LoadModule(self, Module_Reference):		
		# Load all the appropriate modules from the oaAnalysis file that we have defined	
			
		Module = ROOT.TChain(Module_Reference)
		self.Modules.append(Module)
		
		return Module
	
	
	def LoadOutputFile(self):		
	
		self.OutputROOTFile = ROOT.TFile(self.OutputROOTFileLocator, "RECREATE")
		sys.stdout = DataWriter.DataWriter(self.OutputTextFileLocator)
	
		
	
	def Analyse(self, n = 999999999):
		
		self.LoadInputFiles()
		self.LoadOutputFile()
		
		self.NewHistogram1D("Delta_Energy_Recon", "Energy of unknown parent particle of reconstructed proton and photon", "", "",100,0,5000)
		self.NewHistogram1D("Delta_Energy_True", "Energy of Delta Baryons", "", "",100,0,5000)
		self.NewHistogram1D("Delta_Momentum_Recon", "Energy of unknown parent particle of reconstructed proton and photon", "", "",100,0,3000)
		self.NewHistogram1D("Delta_Momentum_True", "Energy of Delta Baryons", "", "",100,0,3000)
		self.NewHistogram1D("Delta_Mass_Recon", "Mass of the Delta Baryon", "", "",100,0,3000)
		
		self.NewHistogram1DStack("Proton_Recon_Efficiency:TrueEnergy","Efficiency of reconstructed proton tracks for varying true energy")
		self.NewHistogram1D("Proton_Recon:ProtonEnergyTrue", "True energy of correctly reconstructed protons", "", "",100,0,5000)
		self.NewHistogram1D("Proton_Recon:MuonEnergyTrue", "True energy of muons incorrectly reconstructed as protons", "", "",100,0,5000)
		self.NewHistogram1D("Proton_Recon:ElectronEnergyTrue", "True energy of electrons incorrectly reconstructed as protons", "", "",100,0,5000)
		self.NewHistogram1D("Proton_Recon:AntiElectronEnergyTrue", "True energy of electrons incorrectly reconstructed as protons", "", "",100,0,5000)
		
		self.NewHistogram1DStack("Proton_Recon_Efficiency:ReconMomentum","Efficiency of reconstructed proton tracks for varying recon momentum")
		self.NewHistogram1D("Proton_Recon:ProtonMomentumRecon", "Recon momentum of correctly reconstructed protons", "", "",100,0,5000)
		self.NewHistogram1D("Proton_Recon:MuonMomentumRecon", "Recon momentum of muons incorrectly reconstructed as protons", "", "",100,0,5000)
		self.NewHistogram1D("Proton_Recon:ElectronMomentumRecon", "Recon momentum of electrons incorrectly reconstructed as protons", "", "",100,0,5000)
		self.NewHistogram1D("Proton_Recon:AntiElectronMomentumRecon", "Recon momentum of electrons incorrectly reconstructed as protons", "", "",100,0,5000)
	
		self.NewHistogram1D("Recon_Truth_Proton_Momentum", "Recon momentum minus truth momentum for PIDs reconstructed as protons", "", "",100,-500,500)
		self.NewHistogram1D("Truth_Proton_Momentum", "Truth momentum for PIDs reconstructed as protons", "", "",100,0,5000)
				
		n = min(n, self.BasicInformation.GetEntries())
		
		self.EventsCount = n
		
		print NewLine, LineSeparator
		print "Reading", n, "Events"
		print LineSeparator
		
		for i in range(n):
			for module in self.Modules:
				module.GetEntry(i)
			self.runEvent()

		self.Histograms["Proton_Recon:ProtonEnergyTrue"].SetFillColor(2)
		self.Histograms["Proton_Recon_Efficiency:TrueEnergy"].Add(self.Histograms["Proton_Recon:ProtonEnergyTrue"])
		self.Histograms["Proton_Recon:MuonEnergyTrue"].SetFillColor(3)
		self.Histograms["Proton_Recon_Efficiency:TrueEnergy"].Add(self.Histograms["Proton_Recon:MuonEnergyTrue"])
		self.Histograms["Proton_Recon:ElectronEnergyTrue"].SetFillColor(4)
		self.Histograms["Proton_Recon_Efficiency:TrueEnergy"].Add(self.Histograms["Proton_Recon:ElectronEnergyTrue"])
		self.Histograms["Proton_Recon:AntiElectronEnergyTrue"].SetFillColor(5)
		self.Histograms["Proton_Recon_Efficiency:TrueEnergy"].Add(self.Histograms["Proton_Recon:AntiElectronEnergyTrue"])
		
		self.Histograms["Proton_Recon:ProtonMomentumRecon"].SetFillColor(2)
		self.Histograms["Proton_Recon_Efficiency:ReconMomentum"].Add(self.Histograms["Proton_Recon:ProtonMomentumRecon"])
		self.Histograms["Proton_Recon:MuonMomentumRecon"].SetFillColor(3)
		self.Histograms["Proton_Recon_Efficiency:ReconMomentum"].Add(self.Histograms["Proton_Recon:MuonMomentumRecon"])
		self.Histograms["Proton_Recon:ElectronMomentumRecon"].SetFillColor(4)
		self.Histograms["Proton_Recon_Efficiency:ReconMomentum"].Add(self.Histograms["Proton_Recon:ElectronMomentumRecon"])
		self.Histograms["Proton_Recon:AntiElectronMomentumRecon"].SetFillColor(5)
		self.Histograms["Proton_Recon_Efficiency:ReconMomentum"].Add(self.Histograms["Proton_Recon:AntiElectronMomentumRecon"])
		
		"""Saves histograms to the output file and prints out any summary information"""
		self.OutputROOTFile.cd()
		for histogram in self.Histograms.itervalues():
			histogram.Write()
		
		print NewLine, LineSeparator
		print "TRUTH"
		print LineSeparator
		
		print "Number of events analysed:" , str(self.EventsCount)
		print "Number of vertices analysed: " , str(self.VerticesCount)
		print "Number of Delta -> p gamma events: " , str(self.DeltaPGammaTotal)
		print "Number of CC Delta -> p gamma events:" , str(self.DeltaPGammaCC)
		print "Number of NC Delta -> p gamma events:" , str(self.DeltaPGammaNC)
		print "Number of Delta -> p gamma events in the FGD:" , str(self.DeltaPGammaTotalinFGD)
		print "Number of NC Delta -> p gamma events in the FGD:" , str(self.DeltaPGammaNCinFGD)
		print "Number of CC Delta -> p gamma events in the FGD:" , str(self.DeltaPGammaCCinFGD)
		
		print NewLine, LineSeparator
		print "RECONSTRUCTION"
		print LineSeparator
		
		print "Number of events with a reconstructed PID:" , str(self.ReconstructedPIDsNumber)
		
		print "PROTON TRACK CUT:"
		print "Number of events with at least one reconstructed proton track:" , str(self.ReconstructedProtonTrack)
		print "Number of reconstructed proton tracks which was a true proton:" , str(self.ProtonCorrectlyReconstructed)
		print "Number of reconstructed proton tracks where the proton track begins in the detector before all other tracks:" , str(self.ProtonTrackFirst)
		print "ECAL CLUSTER CUT"
		print "Number of events with at least one Tracker ECal cluster:" , str(self.ECalNumber)
		print "Number of events with both a reconstructed proton track and at least one Tracker ECal cluster:" , str(self.ProtonAndECal)
		print ""
	
		del sys.stdout#Closes .txt file and returns to printing only to console
		self.OutputROOTFile.Close()#Closing .root file
	
		
	
	def runEvent(self):
	
		###### First loop over the true genie data to look for information about the delta interactions
	
		NVtx=self.Truth_GRTVertices.NVtx

		for VtxCounter in xrange(NVtx):#Loop over vertices in event
			Vtx=self.Truth_GRTVertices.Vtx[VtxCounter]
			
			self.VerticesCount+=1
			
			IncidentMuonNeutrino=False#For a later check of whether incident particle is a neutrino
			ProtonFromDelta=False#For logical check on Delta interaction of interest
			PhotonFromDelta=False
			
			for Particle in self.RTTools.getParticles(Vtx):
				
				###################################### Check for initial neutrino
				
				if(Particle.pdg==14):#Looks for a neutrino
				
					if(Particle.status==0):#Checks if neutrino is initial state
					
						IncidentMuonNeutrino=True						
				
				###################################### Check for Delta interactions
				
				if(Particle.pdg==2214):

					DeltaDaughterFirst=Particle.first_daughter#Finds first Delta daughter
					DeltaDaughterLast=Particle.last_daughter#Finds last Delta daughter
					DeltaDaughterNumber=DeltaDaughterLast-DeltaDaughterFirst+1#Finds number of daughters of the delta

					if(DeltaDaughterNumber==2):#Delta -> p gamma must have 2 daughters
						
						for DaughterParticle in self.RTTools.getParticles(Vtx):#Loop again over particles in vertex
						
							if(DaughterParticle.i>=DeltaDaughterFirst and DaughterParticle.i<=DeltaDaughterLast):#Only looks for when counter is in range of Delta daughter particles
							
								if(DaughterParticle.pdg==2212):
									ProtonFromDelta=True
									
								if(DaughterParticle.pdg==22):
									PhotonFromDelta=True
									
			######################################## Check if in FGD (target mass for neutrino interactions)
									
			inFGDX=(Vtx.EvtVtx[0]>=-832.2 and Vtx.EvtVtx[0]<=832.2)#Checks if interaction began in FGD: X axis
			inFGDY=(Vtx.EvtVtx[1]>=-777.2 and Vtx.EvtVtx[1]<=887.2)#Y axis
			inFGDZ=(Vtx.EvtVtx[2]>=123.45 and Vtx.EvtVtx[2]<=446.95) or (Vtx.EvtVtx[2]>=1481.45 and Vtx.EvtVtx[2]<=1807.95)#Z axis
			
			inFGD=(inFGDX and inFGDY and inFGDZ)
			
			######################################## Search for current and interaction type. This method can look at electron neutrinos and anti muon neutrinos for any possible extension
			
			EvtCode=str(Vtx.EvtCode)#Long event code for each vertex

			EvtCodeSplitList=EvtCode.split(";")#Splits code by semi colons
			
			for EvtCodeCounter in xrange(len(EvtCodeSplitList)):#loops over all elements in split list
			
				if(EvtCodeSplitList[EvtCodeCounter][:9]=="proc:Weak"):#looks for the weak process term
				
					Current=EvtCodeSplitList[EvtCodeCounter][10:12]#this will be a string of either CC or NC, I chose this rather than eg. 1,0 as it is easier to remember
							
					InteractionType=InteractionType=EvtCodeSplitList[EvtCodeCounter].split(",")[1]#Again, these are QES, RES, DIS etc
							
							
			###################################### Categorisation of various interesting interactions ############
							
			DeltaPGammaInteraction=(IncidentMuonNeutrino and ProtonFromDelta and PhotonFromDelta and InteractionType=="RES")
			
			if(DeltaPGammaInteraction):
				self.DeltaPGammaTotal+=1
				
			if(DeltaPGammaInteraction and Current=="CC"):
				self.DeltaPGammaCC+=1
				
			if(DeltaPGammaInteraction and Current=="NC"):
				self.DeltaPGammaNC+=1
				
			if(DeltaPGammaInteraction and inFGD):
				self.DeltaPGammaTotalinFGD+=1
				
			if(DeltaPGammaInteraction and inFGD and Current=="CC"):
				self.DeltaPGammaCCinFGD+=1
				
			if(DeltaPGammaInteraction and inFGD and Current=="NC"):
				self.DeltaPGammaNCinFGD+=1

		################################ Recon ###########################

		NPIDs=self.Reconstructed_Global.NPIDs#Number of reconstructed PIDs

		if(NPIDs>0):
			
			self.ReconstructedPIDsNumber+=1
			
		ReconstructedProtonTrack=False
		ProtonCorrectlyReconstructed=False
		
		PIDDetectorList=[]#List of detectors a PID has passed through
		
		ProtonEnergyList=[]#List of energies of reconstructed proton PIDs
		
		ProtonMomentumListX=[]#List of momenta of reconstructed proton PIDs
		ProtonMomentumListY=[]
		ProtonMomentumListZ=[]
		
		for PIDCounter in xrange(NPIDs):#Loop over the PIDs if they exist

			PID=self.Reconstructed_Global.PIDs[PIDCounter]
			
			PIDDetectorList.append(str(PID.Detectors))#This is a list of the detector paths for all the PIDs in the event
			
			############################# Looking at PDGs #######################
			
			if(len(PID.ParticleIds)>0):	#The reconstructed PID is put into a vector of possible PDGs: The best fitting PDG is given first and then the whole list (including the best
										#fitting  PDG) is given, ordered by PDG. See /home/theory/phujce/FinalYearProject/Recon/Data/FirstCut/Text/2012-12-31-11:46:57.txt
										#Sometimes the PDG vector is not given (because the reconstruction cannot decide?) so I ignore these PIDs
										
				if(PID.ParticleIds[0]!=0 and PID.PIDWeights[0]>=0):	#PDG is only nonzero if the event was in the inner, particle sensitive part of detector (eg not ECal)
																	#There is also the option of requiring the certainty of the particle identification to above be a set amount (not used yet)
					ParticleIds=PID.ParticleIds[0]
				else:
					ParticleIds=None
					
				if(ParticleIds==2212):
					
					TPCNumber=PID.NTPCs
					
					SuitablePIDNodeNumber=False#There must be enough nodes on at least one PID track 
					
					for TPCCounter in xrange(TPCNumber):#Loop over TPC PIDs
						TPCTrack=PID.TPC[TPCCounter]
						
						if(TPCTrack.NNodes>18):
							SuitablePIDNodeNumber=True
						
					if(SuitablePIDNodeNumber):
									
						ReconstructedProtonTrack=True
						PIDDetectorListProtonIndex=PIDCounter
						
						TrueParticle=None
						
						for TrueTrajectoryCounter in xrange(self.Truth_Trajectories.NTraj):#Loop over the truth trajectories for comparison
							if(self.Truth_Trajectories.Trajectories[TrueTrajectoryCounter].ID==PID.TrueParticle.ID):
								
								TrueTrajectory=self.Truth_Trajectories.Trajectories[TrueTrajectoryCounter]
								
								TrueParticle=TrueTrajectory.PDG
								
								TrueParticleEnergy=TrueTrajectory.InitMomentum.E()
								
								TrueParticleMomentum=math.sqrt(TrueTrajectory.InitMomentum.X()*TrueTrajectory.InitMomentum.X()+TrueTrajectory.InitMomentum.Y()*TrueTrajectory.InitMomentum.Y()+TrueTrajectory.InitMomentum.Z()*TrueTrajectory.InitMomentum.Z())
								
								TrueParticleReconMomentum=PID.FrontMomentum
								
						for TrueVertexCounter in xrange(self.Truth_Vertices.NVtx):#Loop over the truth vertices for comparison
							if(self.Truth_Vertices.Vertices[TrueVertexCounter].ID==PID.TrueParticle.Vertex.ID):#Can be used later for looking at purity

								TrueVertex=self.Truth_Vertices.Vertices[TrueVertexCounter]

						if(TrueParticle==2212):
							ProtonCorrectlyReconstructed=True
							
						########################################### Proton Cut Purity ################
							
							self.Histograms["Proton_Recon:ProtonEnergyTrue"].Fill(TrueParticleEnergy)
							self.Histograms["Proton_Recon:ProtonMomentumRecon"].Fill(TrueParticleReconMomentum)
						elif(TrueParticle==13):
							self.Histograms["Proton_Recon:MuonEnergyTrue"].Fill(TrueParticleEnergy)
							self.Histograms["Proton_Recon:MuonMomentumRecon"].Fill(TrueParticleReconMomentum)
						elif(TrueParticle==11):
							self.Histograms["Proton_Recon:ElectronEnergyTrue"].Fill(TrueParticleEnergy)
							self.Histograms["Proton_Recon:ElectronMomentumRecon"].Fill(TrueParticleReconMomentum)
						elif(TrueParticle==-11):
							self.Histograms["Proton_Recon:AntiElectronEnergyTrue"].Fill(TrueParticleEnergy)
							self.Histograms["Proton_Recon:AntiElectronMomentumRecon"].Fill(TrueParticleReconMomentum)
							
						Difference=TrueParticleReconMomentum-TrueParticleMomentum
						
						self.Histograms["Recon_Truth_Proton_Momentum"].Fill(Difference)	
						self.Histograms["Truth_Proton_Momentum"].Fill(TrueParticleMomentum)
						
						
						################################################# Proton Energy #############
						
						ProtonEnergy=math.sqrt(PID.FrontMomentum*PID.FrontMomentum+ Proton.Mass * Proton.Mass) # E^2 = p^2 + m^2 ... Using FrontMomentum of proton

						ProtonEnergyList.append(ProtonEnergy)#Append to list of energies of all reconstructed protons in an event
											
						ProtonMomentumListX.append(PID.FrontMomentum*PID.FrontDirection.X())#Momentum_x = Momentum Magnitude * Unit Vector_x
						ProtonMomentumListY.append(PID.FrontMomentum*PID.FrontDirection.Y())
						ProtonMomentumListZ.append(PID.FrontMomentum*PID.FrontDirection.Z())

		############################################### PID Origin #######################

		PIDOriginalDetectorList=[]#List of the detector origin of the PID for all PIDs in the event

		for PIDDetectorListCounter in xrange(len(PIDDetectorList)):#I know this could have been done quicker, but it might be useful to have the PIDDetectorList
			PIDOriginalDetectorList.append(PIDDetectorList[PIDDetectorListCounter][0])#Selecting the first character (therefore first detector) from PIDDetectorList[]
			
		ProtonFirst=True
				
		if(ReconstructedProtonTrack):	#This cut requires that the start of the proton track is earlier in the detector than the start of any other tracks.
										#This forces the proton track to come from the initial interaction
			ProtonDetectorOrigin=PIDOriginalDetectorList[PIDDetectorListProtonIndex]
			
			ProtonDetectorOriginReordered=SubDetectorReorder(ProtonDetectorOrigin)
						
			for PIDOriginalDetectorListCounter in xrange(len(PIDOriginalDetectorList)):
				
				DetectorListTemp=SubDetectorReorder(PIDOriginalDetectorList[PIDOriginalDetectorListCounter])
				
				if (DetectorListTemp<ProtonDetectorOriginReordered):
					ProtonFirst=False
					
			if(ProtonFirst):
				self.ProtonTrackFirst+=1
		
		############################## ECal cluster section ###################################
				
		TrackerECal=self.Reconstructed_TEC #I think we will only look at the Tracker ECal (TPC+FGD) as the POD ECal is mainly used for POD !! What about downstream ECal
		
		NTrackerECalRecon=TrackerECal.NReconObject#Number of reconstructed objects in the ECal
		
		PhotonEnergyList=[]#A list of the photon energies in each event
		PhotonMomentumListX=[]
		PhotonMomentumListY=[]
		PhotonMomentumListZ=[]
		
		for TrackerECalReconCounter in xrange(NTrackerECalRecon):#Loop over these reconstructed objects
			
			TrackerECalReconObject=TrackerECal.ReconObject[TrackerECalReconCounter]

			ECalEnergy=TrackerECalReconObject.EMEnergyFit_Result#The energy of photon

			PhotonEnergyList.append(ECalEnergy)#Add to the photon energy list
			
			if(TrackerECalReconObject.IsShowerLike):#Check if ECal reconstruction is tracklike or showerlike, it shouldnt matter which for the photon, but the directions are different
				ECalUnitXDirection=TrackerECalReconObject.Shower.Direction.X()#Finding the directions of showers or tracks (its a unit vector)
				ECalUnitYDirection=TrackerECalReconObject.Shower.Direction.Y()
				ECalUnitZDirection=TrackerECalReconObject.Shower.Direction.Z()
			elif(TrackerECalReconObject.IsTrackLike):
				ECalUnitXDirection=TrackerECalReconObject.Track.Direction.X()
				ECalUnitYDirection=TrackerECalReconObject.Track.Direction.Y()
				ECalUnitZDirection=TrackerECalReconObject.Track.Direction.Z()
			
			ECalDirectionMagnitude=math.sqrt(ECalUnitXDirection*ECalUnitXDirection+ECalUnitYDirection*ECalUnitYDirection+ECalUnitZDirection*ECalUnitZDirection)#Magnitude of unit vector (ie should be 1)
			
			if(ECalDirectionMagnitude<1.1):#For some reason there sometimes are occurences where the magnitude is far above 1. This if filters them out. We should probably look into this further
				PhotonMomentumListX.append(ECalUnitXDirection*ECalEnergy)#E = p ... p_x = E_x * unit vector_x
				PhotonMomentumListY.append(ECalUnitYDirection*ECalEnergy)
				PhotonMomentumListZ.append(ECalUnitZDirection*ECalEnergy)
		
		############################## Summary Section ########################################

		if(ReconstructedProtonTrack):#Counts number of events with at least one reconstructed proton track
			self.ReconstructedProtonTrack+=1
		if(ProtonCorrectlyReconstructed):
			self.ProtonCorrectlyReconstructed+=1
		if(NTrackerECalRecon>0):
			self.ECalNumber+=1
		if(ReconstructedProtonTrack and NTrackerECalRecon > 0):
			self.ProtonAndECal+=1
			
		###### Delta Mass Histogram ####
		
		DeltaMomentumList=[]
		
		if(len(PhotonEnergyList)>0 and len(ProtonEnergyList)>0):#Including only events where both photon and proton reconstruction happened
			for PhotonEnergyCounter in xrange(len(PhotonEnergyList)):#Loop over every item in both proton and photon lists and match them up
				for ProtonEnergyCounter in xrange(len(ProtonEnergyList)):
					
					UnknownObjectEnergy=PhotonEnergyList[PhotonEnergyCounter]+ProtonEnergyList[ProtonEnergyCounter]#Energy of Delta ... E_D = E_gamma + E_p
					
					self.Histograms["Delta_Energy_Recon"].Fill(UnknownObjectEnergy)
										
					if(PhotonEnergyCounter<len(PhotonMomentumListX) and ProtonEnergyCounter<len(ProtonMomentumListX)):#To account for earlier trick of not including unit vectors > 1.1
						DeltaMomentumX=PhotonMomentumListX[PhotonEnergyCounter]+ProtonMomentumListX[ProtonEnergyCounter]#In component form p_{x D} = p_{x gamma} + p_{x proton}
						DeltaMomentumY=PhotonMomentumListY[PhotonEnergyCounter]+ProtonMomentumListY[ProtonEnergyCounter]
						DeltaMomentumZ=PhotonMomentumListZ[PhotonEnergyCounter]+ProtonMomentumListZ[ProtonEnergyCounter]
					
						DeltaMomentumMagnitude=math.sqrt(DeltaMomentumX*DeltaMomentumX+DeltaMomentumY*DeltaMomentumY+DeltaMomentumZ*DeltaMomentumZ)#|p_{D}|^{2}
						
						if(UnknownObjectEnergy>DeltaMomentumMagnitude):#As this is statistical approach, sometimes can get sqrt(negative number)
							DeltaMass=math.sqrt(UnknownObjectEnergy*UnknownObjectEnergy-DeltaMomentumMagnitude*DeltaMomentumMagnitude)#m^2 = E^2 - p^2
							self.Histograms["Delta_Mass_Recon"].Fill(DeltaMass)
										
						self.Histograms["Delta_Momentum_Recon"].Fill(DeltaMomentumMagnitude)
				
			for VtxCounter in xrange(NVtx):#Can loop over truth for comparison
			
				Vtx=self.Truth_GRTVertices.Vtx[VtxCounter]
				
				for particle in self.RTTools.getParticles(Vtx):
					
					if(particle.pdg==2214):
						DeltaEnergy=particle.momentum[3]*1000#GeV->MeV
						
						DeltaMomentumXTrue=particle.momentum[0]
						DeltaMomentumYTrue=particle.momentum[1]
						DeltaMomentumZTrue=particle.momentum[2]
						
						DeltaMomentumMagnitudeTrue=math.sqrt(DeltaMomentumXTrue*DeltaMomentumXTrue+DeltaMomentumYTrue*DeltaMomentumYTrue+DeltaMomentumZTrue*DeltaMomentumZTrue)*1000
						
						self.Histograms["Delta_Energy_True"].Fill(DeltaEnergy)
						self.Histograms["Delta_Momentum_True"].Fill(DeltaMomentumMagnitudeTrue)

def FileNameGenerator():#Generates a unique file name based on current time (without file extension)

	FolderName=Now.strftime("%Y-%m/%d/")

	FileName=Now.strftime("%Y-%m-%d-%H:%M:%S")
	
	return FolderName , FileName
	
def SubDetectorReorder(InputDetectorNumber):#Reorders the detector number labels into the order in which an incoming neutrino sees them
											# TPC1 -> FGD1 -> TPC2 -> FGD2 -> TPC3
	if(InputDetectorNumber==4):# TPC1: 1 -> 1 , FGD1: 4 -> 2
		OutputDetectorNumber=2
	elif(InputDetectorNumber==2):#TPC2: 2 -> 3
		OutputDetectorNumber=3
	elif(InputDetectorNumber==5):#FGD2: 5 -> 4
		OutputDetectorNumber=4
	elif(InputDetectorNumber==3):#TPC3: 3 -> 5
		OutputDetectorNumber=5
	else:#Ignoring the PIDs reconstructed in the ECal and SMRD and Tracker ECal
		OutputDetectorNumber=None
					
	return OutputDetectorNumber
	
def FilePathGenerator(Subfolder,Extension):
	
	(FolderName,FileName)=FileNameGenerator()
		
	FileLocation=DataLocation+FolderName+Subfolder
	
	if (not os.path.exists(FileLocation)):#Found from http://stackoverflow.com/questions/1274405/how-to-create-new-folder
		os.makedirs(FileLocation)#Makes the file directory if it doesn't already exist
		
	FilePath=FileLocation+FileName+Extension
	
	return FilePath
		
def ListFileCreator(input_filename_list):
		
	(FolderName,FileName)=FileNameGenerator()
	
	FileLocation=DataLocation+FolderName+"Input List/"

	try:
		ExistingFileList=os.listdir(FileLocation)
		ExistingFileNumber=len(ExistingFileList)
	except:
		ExistingFileNumber=0

	if(ExistingFileNumber>0):
		LastFile=open(FileLocation+ExistingFileList[ExistingFileNumber-1])
		
		LastFileList = LastFile.read().splitlines()
			
		LastFile.close()
	
		if(LastFileList!=input_filename_list):
			
			output_ListFilename=FilePathGenerator("Input List/",".list")#For archiving the .list file used
	
			OutputListFile=open(output_ListFilename,"w")
	
			for ListCounter in xrange(len(input_filename_list)):
				OutputListFile.write(str(input_filename_list[ListCounter])+"\n")
	
	else:
	
		output_ListFilename=FilePathGenerator("Input List/",".list")#For archiving the .list file used
	
		OutputListFile=open(output_ListFilename,"w")
	
		for ListCounter in xrange(len(input_filename_list)):
			OutputListFile.write(str(input_filename_list[ListCounter])+"\n")
		
def main():
		
	libraries.load("nd280/nd280.so")
		
	#input_filename_list = ( glob.glob( sys.argv[1]+"*" ) )
	
	FileList = open("prod5_analysis.list")
	
	InputFileLocatorList = FileList.read().splitlines()
		
	OutputROOTFileLocator = FilePathGenerator("ROOT/", ".root")
	OutputTextFileLocator = FilePathGenerator("Text/", ".txt")
	
	ListFileCreator(InputFileLocatorList)

	Analysis1 = Analysis(InputFileLocatorList, OutputROOTFileLocator, OutputTextFileLocator)
	
	Analysis1.Analyse(200)

if __name__ == "__main__":
	main()
