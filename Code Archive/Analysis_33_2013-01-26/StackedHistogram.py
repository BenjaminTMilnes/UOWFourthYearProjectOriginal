import ROOT 
ROOT.gROOT.SetBatch(True)

import ROOTFile

class StackedHistogram:
	
	def __init__(self, Reference, Title, LegendX1, LegendY1, LegendX2, LegendY2, XAxisTitle, YAxisTitle, Directory):
		
		self.StackedHistogram=ROOT.THStack(Reference, Title)
		
		self.HistogramDictionary = {}
		self.Legend = ROOT.TLegend(LegendX1, LegendY1, LegendX2, LegendY2)
		
		self.XAxisTitle = XAxisTitle
		self.YAxisTitle = YAxisTitle
		
		self.Directory = Directory
			
	def NewHistogram1D(self, Reference, Title, XAxisTitle, YAxisTitle, NumberOfBinsX, MinimumX, MaximumX, LegendLabel, Directory):
		
		HistogramObject = ROOTFile.HistogramStorage()
		
		HistogramObject.Histogram = ROOT.TH1D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX)
		HistogramObject.Histogram.SetXTitle(XAxisTitle)
		HistogramObject.Histogram.SetYTitle(YAxisTitle)
		HistogramObject.LegendLabel = LegendLabel
		HistogramObject.HistogramDirectory=Directory
		
		self.HistogramDictionary[Reference]=HistogramObject
	
	def AddToLegend(self, EntryStyle):
	
		for i, Histogram1 in enumerate(self.HistogramDictionary.itervalues()):

			self.Legend.AddEntry(Histogram1.Histogram, Histogram1.LegendLabel, EntryStyle)

	def AutoColour(self):
		
		for i, Histogram1 in enumerate(self.HistogramDictionary.itervalues()):
			
			Histogram1.Histogram.SetFillColor(i+1)

	def AddHistograms(self):
		
		for Histogram1 in self.HistogramDictionary.itervalues():
			
			self.StackedHistogram.Add(Histogram1.Histogram)

	def AutoPrepare(self, LegendEntryStyle):
		
		self.AutoColour()
		
		self.AddHistograms()
		
		self.AddToLegend(LegendEntryStyle)

	def StackedHistogramCanvas(self, Reference, Title, WidthX, WidthY):
		
		Canvas=ROOT.TCanvas(Reference, Title, WidthX, WidthY)
			
		self.StackedHistogram.Draw()
		
		self.StackedHistogram.GetXaxis().SetTitle(self.XAxisTitle)
		self.StackedHistogram.GetYaxis().SetTitle(self.YAxisTitle)
		
		self.Legend.Draw()
		
		return Canvas, self.Directory
		
	def DrawConstituentHistograms(self, ROOTFileObject):
		
		for Histogram1Key, Histogram1 in self.HistogramDictionary.iteritems():
			
			ROOTFileObject.HistogramDictionary[Histogram1Key] = Histogram1
			
	def ConstituentFill1D(self, ConstituentDictionary, EventDetail, FillVariable, BeginningTitle, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, StackedHistogramReference):
		
		EventAccountedFor = False
		
		for Key1, HistogramReference1 in ConstituentDictionary.iteritems():
			
			ConstituentHistogramReference = StackedHistogramReference + ":" + str(Key1)

			if (EventDetail == Key1):
				
				self.AttemptToFill1D(BeginningTitle, HistogramReference1, ConstituentHistogramReference, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, self.Directory + "/Constituent Histograms/", FillVariable, HistogramReference1)
					
				EventAccountedFor = True
				
		if (not EventAccountedFor):
		
			ConstituentHistogramReference = StackedHistogramReference + ":" + "Other"
			
			self.AttemptToFill1D(BeginningTitle, "Other Sources", ConstituentHistogramReference, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, self.Directory + "/Constituent Histograms/", FillVariable, "Other Sources")
							
	def AttemptToFill1D(self, BeginningTitle, Reference, ConstituentHistogramReference, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, Directory, FillVariable, LegendTitle):
		
		try:
			self.HistogramDictionary[ConstituentHistogramReference].Histogram.Fill(FillVariable)
		except:
			Title = BeginningTitle + " " + Reference
			self.NewHistogram1D(ConstituentHistogramReference, Title, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, LegendTitle, Directory)
			self.HistogramDictionary[ConstituentHistogramReference].Histogram.Fill(FillVariable)
	
	##################################
	
	def ConstituentFill2D(self, ConstituentDictionary, EventDetail, FillVariableX, FillVariableY, BeginningTitle, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, StackedHistogramReference):
		
		EventAccountedFor = False
		
		for Key1, HistogramReference1 in ConstituentDictionary.iteritems():
			
			ConstituentHistogramReference = StackedHistogramReference + ":" + str(Key1)

			if (EventDetail == Key1):
				
				self.AttemptToFill1D(BeginningTitle, HistogramReference1, ConstituentHistogramReference, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, self.Directory + "/Constituent Histograms/", FillVariableX, FillVariableY, HistogramReference1)
					
				EventAccountedFor = True
				
		if (not EventAccountedFor):
		
			ConstituentHistogramReference = StackedHistogramReference + ":" + "Other"
			
			self.AttemptToFill1D(BeginningTitle, "Other Sources", ConstituentHistogramReference, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, self.Directory + "/Constituent Histograms/", FillVariableX, FillVariableY, "Other Sources")
			
	def AttemptToFill2D(self, BeginningTitle, Reference, ConstituentHistogramReference, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, Directory, FillVariableX, FillVariableY, LegendTitle):
		
		try:
			self.HistogramDictionary[ConstituentHistogramReference].Histogram.Fill(FillVariableX, FillVariableY)
		except:
			Title = BeginningTitle + " " + Reference
			self.NewHistogram1D(ConstituentHistogramReference, Title, XAxisTitle, YAxisTitle, NumberOfBins, MinimumX, MaximumX, LegendTitle, Directory)
			self.HistogramDictionary[ConstituentHistogramReference].Histogram.Fill(FillVariableX, FillVariableY)
		
