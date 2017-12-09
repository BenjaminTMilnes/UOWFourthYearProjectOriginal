# ROOT File
#
# Last Modified: 2013.01.13 20:21
#
# This is a container class for ROOT histograms, graphs, charts, and other objects.
#

import ROOT 
ROOT.gROOT.SetBatch(True)

class ROOTFile:
		
	def __init__(self, FileLocator):
				
		self.FileLocator = FileLocator
		
		self.Histograms = {}
	
	
	def Open(self):		
	
		self.File = ROOT.TFile(self.FileLocator, "RECREATE")
		
			
	def Close(self):		
	
		self.File.cd()
		
		for Histogram1 in self.Histograms.itervalues():
			Histogram1.Write()
			
		self.File.Close()
		
			
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
		
				
	def NewGraph(self, Reference, Title, NumberOfPoints, XAxisTitle, XArray, YAxisTitle, YArray):
	
		self.Histograms[Reference] = ROOT.TGraph(NumberOfPoints, XArray, YArray)
		self.Histograms[Reference].SetTitle(Title)
		
		XAxis1 = self.Histograms[Reference].GetXaxis()
		XAxis1.SetTitle(XAxisTitle)
		
		YAxis1 = self.Histograms[Reference].GetYaxis()
		YAxis1.SetTitle(YAxisTitle)
		
		self.Histograms[Reference].SetName(Reference)

	def NewCanvas(self, Reference, Title, WidthX, WidthY):
		
		self.Histograms[Reference] = ROOT.TCanvas(Reference, Title, WidthX, WidthY)
		
	def NewStackedHistogramCanvas(self, Reference, Canvas):
		
		self.Histograms[Reference] = Canvas
