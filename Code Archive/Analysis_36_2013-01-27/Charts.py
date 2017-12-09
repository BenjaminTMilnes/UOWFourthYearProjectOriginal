##########
########## Charts
##########
########## A set of container classes for containing histogram data, which can then be exported to ROOT objects.
##########
########## Modified: 2013.01.25 21:55
##########


####################################################################################################
########## DO NOT EDIT - PROTOTYPE CODE
####################################################################################################


import ROOT 


ROOT.gROOT.SetBatch(True)


class HistogramCollection: # This is a container class for the histogram objects.
	
	def __init__(This):
		
		This.Histograms = {} # The collection of histogram objects.
		
	def NewHistogram1D(This, Reference, Title = "", XAxisTitle = "", YAxisTitle = ""): # Create a new 1D histogram and add it to the dictionary.				
		This.Histograms[Reference] = Histogram1D(Reference, Title, XAxisTitle, YAxisTitle)
	
	def NewHistogram2D(This, Reference, Title = "", XAxisTitle = "", YAxisTitle = ""): # Create a new 2D histogram and add it to the dictionary.				
		This.Histograms[Reference] = Histogram2D(Reference, Title, XAxisTitle, YAxisTitle)
		
	def NewHistogram3D(This, Reference, Title = "", XAxisTitle = "", YAxisTitle = "", ZAxisTitle = ""):	# Create a new 3D histogram and add it to the dictionary.			
		This.Histograms[Reference] = Histogram3D(Reference, Title, XAxisTitle, YAxisTitle, ZAxisTitle)
		
	def NewStackedHistogram1D(This, Reference, Title = "", XAxisTitle = "", YAxisTitle = "", GroupReferences = []): # Create a new 1D stacked histogram and add it to the dictionary.
		This.Histograms[Reference] = StackedHistogram1D(Reference, Title, XAxisTitle, YAxisTitle, GroupReferences)
	
	def ToROOTHistogramCollection(This): # Convert the histograms to ROOT histogram objects and export the collection.
		
		ROOTHistograms = {}
		
		if (len(This.Histograms) > 0):
			for Histogram1 in This.Histograms:
				ROOTHistograms[Histogram1.Reference] = Histogram1.ToROOTHistogram()

		return ROOTHistograms


class Histogram:
	
	def __init__(This, Reference, Title = ""):
		
		This.Reference = Reference
		This.Title = Title
		This.ShowLegend = False
		
class Histogram1D(Histogram):
	
	def __init__(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100):
		
		Histogram.__init__(This, Reference, Title)
		
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle, YAxisNumberOfDivisions, YAxisMinimum, YAxisMaximum)
		
		This.Data = []	
	
	def Populate(This, X):
		
		This.Data.append([X])
	
	def ToROOTHistogram(This):
		
		TH1D1 = ROOT.TH1D(This.Reference, This.Title, This.XAxis.NumberOfDivisions, This.XAxis.Minimum, This.XAxis.Maximum)
		TH1D1.SetXTitle(This.XAxis.Title)
		TH1D1.SetYTitle(This.YAxis.Title)
		
		for DataItem in This.Data:
			TH1D1.Fill(DataItem[0])
		
		return TH1D1
		
class Histogram2D(Histogram):
	
	def __init__(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100):
		
		Histogram.__init__(This, Reference, Title)
				
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle, YAxisNumberOfDivisions, YAxisMinimum, YAxisMaximum)
		
		This.Data = []	
	
	def Populate(This, X, Y):
		
		This.Data.append([X, Y])
	
	def ToROOTHistogram(This):
		
		TH2D1 = ROOT.TH2D(This.Reference, This.Title, This.XAxis.NumberOfDivisions, This.XAxis.Minimum, This.XAxis.Maximum, This.YAxis.NumberOfDivisions, This.YAxis.Minimum, This.YAxis.Maximum)
		TH2D1.SetXTitle(This.XAxis.Title)
		TH2D1.SetYTitle(This.YAxis.Title)
				
		for DataItem in This.Data:
			TH1D1.Fill(DataItem[0], DataItem[1])
			
		return TH2D1

class Histogram3D(Histogram):
	
	def __init__(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100, ZAxisTitle = "", ZAxisNumberOfDivisions = 100, ZAxisMinimum = 0, ZAxisMaximum = 100):
		
		Histogram.__init__(This, Reference, Title)
				
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle, YAxisNumberOfDivisions, YAxisMinimum, YAxisMaximum)
		This.ZAxis = HistogramAxis(ZAxisTitle, ZAxisNumberOfDivisions, ZAxisMinimum, ZAxisMaximum)
		
		This.Data = []	
	
	def Populate(This, X, Y, Z):
		
		This.Data.append([X, Y, Z])
	
	def ToROOTHistogram(This):
		
		TH3D1 = ROOT.TH3D(This.Reference, This.Title, This.XAxis.NumberOfDivisions, This.XAxis.Minimum, This.XAxis.Maximum, This.YAxis.NumberOfDivisions, This.YAxis.Minimum, This.YAxis.Maximum, This.ZAxis.NumberOfDivisions, This.ZAxis.Minimum, This.ZAxis.Maximum)
		TH3D1.SetXTitle(This.XAxis.Title)
		TH3D1.SetYTitle(This.YAxis.Title)
		TH3D1.SetZTitle(This.ZAxis.Title)
				
		for DataItem in This.Data:
			TH1D1.Fill(DataItem[0], DataItem[1], DataItem[2])
			
		return TH3D1

class StackedHistogram1D(Histogram):
	
	def __init__(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100, DataGroupReferences = []):
		
		Histogram.__init__(This, Reference, Title)
		
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle, YAxisNumberOfDivisions, YAxisMinimum, YAxisMaximum)
		
		This.DataGroups = {}
		
		if (len(DataGroupReferences) > 0):
			for DataGroupReference1 in DataGroupReferences:
				This.DataGroups[DataGroupReference1] = StackedHistogramDataGroup()
				
	def Populate(This, GroupReference, X):
		
		This.DataGroups[GroupReference].Data.append([X])
			
	def ToROOTHistogram(This, Width = 1000, Height = 1000, AutoColour = True):
		
		TCanvas1 = ROOT.TCanvas(This.Reference, This.Title, WidthX, WidthY)
		THStack1 = ROOT.THStack(This.Reference, This.Title)
		
		TLegend1 = ROOT.TLegend(This.LegendX1, This.LegendX2, This.LegendY1, This.LegendY2)
		
		n1 = 0
		
		for DataGroupReference1 in This.DataGroups.keys():
			
			TH1D1 = ROOT.TH1D(DataGroupReference1, This.Title, This.XAxis.NumberOfDivisions, This.XAxis.Minimum, This.XAxis.Maximum)
			TH1D1.SetXTitle(This.XAxis.Title)
			TH1D1.SetYTitle(This.YAxis.Title)
			
			if (AutoColour == True):
				TH1D1.SetFillColor(n1)
				n1 += 1
			
			for DataItem1 in This.DataGroups[DataGroupReference1].Data:
				TH1D1.Fill(DataItem[0])
			
			TLegend1.AddEntry(TH1D1, This.DataGroups[DataGroupReference1].LegendTitle, This.DataGroups[DataGroupReference1].LegendEntryStyle)
			
			THStack1.Add(TH1D1)
					
		return 0

class HistogramAxis:
	
	def __init__(This, Title = "", NumberOfDivisions = 100, Minimum = 0, Maximum = 100):
		
		This.Title = Title
		This.NumberOfDivisions = NumberOfDivisions
		This.Minimum = Minimum
		This.Maximum = Maximum
		This.Labels = []

class StackedHistogramDataGroup:
	
	def __init__(This, LegendTitle = "", LegendEntryStyle = ""):
		
		This.Data = []
		This.LegendTitle = LegendTitle
		This.LegendEntryStyle = LegendEntryStyle

class HistogramLegend:
	
	def __init__(This, Title = ""):
		
		This.Title = Title
