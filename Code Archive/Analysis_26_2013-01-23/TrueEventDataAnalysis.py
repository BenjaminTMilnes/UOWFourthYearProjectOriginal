# True Event Data Analysis
#
# This module is simply a division of the code from the main analysis program.
#
# Modified: 2013.01.21 13:05 BTM
# Modified: 2013.01.21 13:27 BTM
#

import sys

import ROOT
import RooTrackerTools

import ParticleCodes
import EventCodeDeconstructor

def Analyse(TrueEvents_GRTVertices):
	
	TruthStatistics = StatisticsCollection.StatisticsCollection("Truth Statistics")
			
	TruthStatistics.NewStatistic("NVertices", "Number of Vertices", 0)
	TruthStatistics.NewStatistic("NDeltaToProtonPhoton", "Number of Delta to Proton-Photon Events", 0)
	TruthStatistics.NewStatistic("NDeltaToProtonPhotonCC", "Number of Delta to Proton-Photon Charged-Current Events", 0)
	TruthStatistics.NewStatistic("NDeltaToProtonPhotonNC", "Number of Delta to Proton-Photon Neutral-Current Events", 0)		
	TruthStatistics.NewStatistic("NDeltaToPi0Meson", "Number of Delta to Proton-Pi Meson Events", 0)
	TruthStatistics.NewStatistic("NDeltaToPi0MesonCC", "Number of Delta to Proton-Pi Meson Charged-Current Events", 0)
	TruthStatistics.NewStatistic("NDeltaToPi0MesonNC", "Number of Delta to Proton-Pi Meson Neutral-Current Events", 0)		
	
	EventCodeDeconstructor1 = EventCodeDeconstructor.EventCodeDeconstructor()
	
	IsDeltaHadronToProtonPhotonEvent = False
	IsDeltaHadronToProtonPi0MesonEvent = False
	
	for GRTVertex1 in TrueEvents_GRTVertices:
		# Each event has multiple vertices, which define the individual interactions.
							
		TruthStatistics.Statistics["NVertices"].Quantity += 1
					
		IncidentMuNeutrino = False
		ProtonFromDeltaHadron = False
		PhotonFromDeltaHadron = False
		Pi0MesonFromDeltaHadron = False
		
		Current = ""
		Interaction = ""
		
		for GRTParticle1 in self.RTTools.getParticles(GRTVertex1):
			# Look through each particle in the vertex.
			
			if ((GRTParticle1.pdg == ParticleCodes.MuNeutrino) and (GRTParticle1.status == 0):
				# See whether there is an incident mu neutrino.
				IncidentMuNeutrino = True						
						
			if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon):
				# See whether there is a Delta 1 Hadron

				FirstProduct = GRTParticle1.first_daughter
				LastProduct = GRTParticle1.last_daughter
				NumberOfProducts = DeltaDaughterLast - DeltaDaughterFirst + 1

				if (NumberOfProducts == 2):
				# The Delta 1 Hadron must deteriorate to two particles.
					
					for GRTParticle2 in self.RTTools.getParticles(GRTVertex1):
						
						if (GRTParticle2.i >= FirstProduct and GRTParticle2.i <= LastProduct):
						
							if (GRTParticle2.pdg == ParticleCodes.Proton):
								ProtonFromDeltaHadron = True
								
							if (GRTParticle2.pdg == ParticleCodes.Photon):
								PhotonFromDeltaHadron = True
								
							if (GRTParticle2.pdg == ParticleCodes.Pi0Meson):
								Pi0MesonFromDeltaHadron = True

													
		EventCodeDeconstructor1.ReadCode(GRTVertex1.EvtCode)
		
		for Element1 in EventCodeDeconstructor1.Elements:
			if (Element1.Reference == "Current Code"):
				Current = Element1.Content
			if (Element1.Reference == "Process Code"):
				InteractionType = Element1.Content
												
												
		IsDeltaHadronToProtonPhotonVertex = (IncidentMuNeutrino and ProtonFromDeltaHadron and PhotonFromDeltaHadron and InteractionType == "RP")
		IsDeltaHadronToProtonPi0MesonVertex = (IncidentMuNeutrino and ProtonFromDeltaHadron and Pi0MesonFromDeltaHadron and InteractionType == "RP")
				
		
		if (IsDeltaHadronToProtonPhotonVertex):
			
			TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity += 1
			IsDeltaHadronToProtonPhotonEvent = True
				
			if (Current == "CC"):
				TruthStatistics.Statistics["NDeltaToProtonPhotonCC"].Quantity += 1
				
			if (Current == "NC"):
				TruthStatistics.Statistics["NDeltaToProtonPhotonNC"].Quantity += 1


		if (IsDeltaHadronToProtonPi0MesonVertex):
			
			TruthStatistics.Statistics["NDeltaToProtonPi0Meson"].Quantity += 1
			IsDeltaHadronToProtonPi0MesonEvent = True
				
			if (Current == "CC"):
				TruthStatistics.Statistics["NDeltaToProtonPi0MesonCC"].Quantity += 1
				
			if (Current == "NC"):
				TruthStatistics.Statistics["NDeltaToProtonPi0MesonNC"].Quantity += 1


	return (TruthStatistics, IsDeltaHadronToProtonPhotonEvent, IsDeltaHadronToProtonPi0MesonEvent)

