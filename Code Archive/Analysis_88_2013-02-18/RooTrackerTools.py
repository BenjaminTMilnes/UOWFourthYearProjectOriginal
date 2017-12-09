import os
import ROOT



class RooTrackerParticle:
	
	def __init__(self):
		self.i = -1
		self.momentum = ROOT.TLorentzVector(0.0,0.0,0.0,0.0)
		self.pdg = 0
		self.position = ROOT.TLorentzVector(0.0,0.0,0.0,0.0)
		self.status = -1
		self.first_daughter = -1
		self.last_daughter = -1
		self.first_mother = -1
		self.last_mother = -1
	
	def isIncoming(self):
		return( self.status == 0 )
	
	def isOutgoing(self):
		return( self.status == 1 )
	
	def __str__(self):
		return "[" + str(self.status) + "] " + str(self.pdg)



class RooTrackerTools:
	
	def __init__(self):
		ROOT.gROOT.ProcessLine(".L ./RooTrackerTools.C+")
	
	
	def getParticleMomentum(self, vertex, i):
		return ROOT.getRooTrackerMomentum(vertex, i)
	
	
	def getParticle(self, vertex, i):
		particle = RooTrackerParticle()
		particle.i = i
		particle.pdg = vertex.StdHepPdg[i]
		particle.momentum = self.getParticleMomentum(vertex, i)
		particle.position = self.getParticlePosition(vertex, i)
		particle.status = vertex.StdHepStatus[i]
		particle.first_daughter = vertex.StdHepFd[i]
		particle.last_daughter = vertex.StdHepLd[i]
		particle.first_mother = vertex.StdHepFm[i]
		particle.last_mother = vertex.StdHepLm[i]
		return particle
	
	
	def getParticles(self, vertex):
		particles = []
		for i in range(vertex.StdHepN):
			particles.append( self.getParticle(vertex, i) )
		return particles
	
	
	def getParticlePosition(self, vertex, i):
		return ROOT.getRooTrackerPosition(vertex, i)
	
	
	def getNeutCode(self, vertex):
		return ROOT.getRooTrackerNeutCode(vertex)
	
	
	def getVertexPosition(self, vertex):
		return ROOT.getRooTrackerLocation(vertex)
