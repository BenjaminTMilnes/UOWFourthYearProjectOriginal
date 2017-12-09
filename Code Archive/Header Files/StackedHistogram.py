import ROOT 
ROOT.gROOT.SetBatch(True)

class StackedHistogram:
	
	def __init__(self, Reference, Title, LegendX1, LegendY1, LegendX2, LegendY2, XAxisTitle, YAxisTitle):
		
		self.StackedHistogram=ROOT.THStack(Reference, Title)
		
		self.HistogramDictionary = {}
		self.Legend=ROOT.TLegend(LegendX1, LegendY1, LegendX2, LegendY2)
		
		self.XAxisTitle=XAxisTitle
		self.YAxisTitle=YAxisTitle
			
	def NewHistogram1D(self, Reference, Title, XAxisTitle, YAxisTitle, NumberOfBinsX, MinimumX, MaximumX, LegendLabel):
		
		HistogramObject=HistogramStorage()
		
		HistogramObject.Histogram=ROOT.TH1D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX)
		HistogramObject.Histogram.SetXTitle(XAxisTitle)
		HistogramObject.Histogram.SetYTitle(YAxisTitle)
		HistogramObject.LegendLabel=LegendLabel
		
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
		
		return Canvas
		
class HistogramStorage:
	
	def __init__(self):
		
		self.Histogram=""
		self.LegendLabel=""
