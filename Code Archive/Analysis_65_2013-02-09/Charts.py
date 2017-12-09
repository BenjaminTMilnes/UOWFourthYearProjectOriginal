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
import ROOTFile # Transitional Code

ROOT.gROOT.SetBatch(True)


class HistogramCollection: # This is a container class for the histogram objects.
	
	def __init__(This):
		
		This.Histograms = {} # The collection of histogram objects.
		
	def NewHistogram1D(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = ""): # Create a new 1D histogram and add it to the dictionary.				
		This.Histograms[Reference] = Histogram1D(Reference, Title, XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum, YAxisTitle)
	
	def NewHistogram2D(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100): # Create a new 2D histogram and add it to the dictionary.				
		This.Histograms[Reference] = Histogram2D(Reference, Title, XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum, YAxisTitle, YAxisNumberOfDivisions, YAxisMinimum, YAxisMaximum)
		
	def NewHistogram3D(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100, ZAxisTitle = "", ZAxisNumberOfDivisions = 100, ZAxisMinimum = 0, ZAxisMaximum = 100):	# Create a new 3D histogram and add it to the dictionary.			
		This.Histograms[Reference] = Histogram3D(Reference, Title, XAxisTitle, YAxisTitle, ZAxisTitle)
		
	def NewStackedHistogram1D(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 10, XAxisMinimum = 0, XAxisMaximum = 10, YAxisTitle = "", GroupReferences = []): # Create a new 1D stacked histogram and add it to the dictionary.
		This.Histograms[Reference] = StackedHistogram1D(Reference, Title, XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum, YAxisTitle, GroupReferences)
	
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
	
	def __init__(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = ""):
		
		Histogram.__init__(This, Reference, Title)
		
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle)
		
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
	
	# This is transitional code and will be deleted later.
	def ToHistogramStorage(This): 
	
		HistogramStorage1 = ROOTFile.HistogramStorage()
		
		HistogramStorage1.Histogram = This.ToROOTHistogram()
		
		return HistogramStorage1
		
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
	
	def __init__(This, Reference, Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", DataGroupReferences = []):
		
		Histogram.__init__(This, Reference, Title)
		
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle)
		
		This.DataGroups = {}
		
		if (len(DataGroupReferences) > 0):
			for DataGroupReference1 in DataGroupReferences:
				This.DataGroups[DataGroupReference1] = StackedHistogramDataGroup()
				
		This.THStack1 = ROOT.THStack(This.Reference, This.Title)
		This.TLegend1 = ROOT.TLegend(0, 10, 0, 10)
		
	def Populate(This, GroupReference, X):
		
		#This.DataGroups[GroupReference].Data.append([0])
		This.DataGroups[GroupReference].Data.append([X])
			
	def ToROOTCanvas(This, Width = 700, Height = 490, AutoColour = True):
				
		TCanvas1 = ROOT.TCanvas(This.Reference + str("Canvas"), This.Title, Width, Height)
		
		n1 = 1		
		
		for DataGroupReference1 in This.DataGroups.keys():
						
			TH1D1 = ROOT.TH1D(This.Reference + "_" + DataGroupReference1, This.Title, This.XAxis.NumberOfDivisions, This.XAxis.Minimum, This.XAxis.Maximum)
			TH1D1.SetXTitle(This.XAxis.Title)
			TH1D1.SetYTitle(This.YAxis.Title)
			
			if (AutoColour == True):
				TH1D1.SetFillColor(n1)
				n1 += 1
			
			for DataItem1 in This.DataGroups[DataGroupReference1].Data:
				TH1D1.Fill(DataItem1[0])
			
			This.TLegend1.AddEntry(TH1D1, This.DataGroups[DataGroupReference1].LegendTitle, This.DataGroups[DataGroupReference1].LegendEntryStyle)
						
			This.THStack1.Add(TH1D1)
					
		TCanvas1.cd()	
				
		This.THStack1.Draw()				
		This.TLegend1.Draw()
						
		TCanvas1.Update()
		
		return TCanvas1
		
	
	def ToNormalisedStackedHistogram(This):
		
		StackedHistogram1D1 = StackedHistogram1D(This.Reference, This.Title, This.XAxis.Title, This.XAxis.NumberOfDivisions, This.XAxis.Minimum, This.XAxis.Maximum, This.YAxis.Title, This.DataGroups.keys())
		
		for DataGroupReference1 in This.DaraGroups.keys():
			for DataItem1 in This.DaraGroups[DataGroupReference1].Data:
				StackedHistogram1D1.Populate(DataGroupReference1, DataItem[0])
	
	def ToHistogramStorage(This): # Transitional code.
		
		THStack1 = This.ToROOTHistogram()
		
		HistogramStorage1 = ROOTFile.HistogramStorage()
		
		HistogramStorage1.Histogram = THStack1
		
		return HistogramStorage1		
		

class HistogramAxis:
	
	def __init__(This, Title = "", NumberOfDivisions = 100, Minimum = 0, Maximum = 100):
		
		This.Title = Title
		This.NumberOfDivisions = NumberOfDivisions
		This.Minimum = Minimum
		This.Maximum = Maximum
		This.Labels = []

class StackedHistogramDataGroup:
	
	def __init__(This, LegendTitle = "asdasd", LegendEntryStyle = "f"):
		
		This.Data = []
		This.LegendTitle = LegendTitle
		This.LegendEntryStyle = LegendEntryStyle

class HistogramLegend:
	
	def __init__(This, Title = ""):
		
		This.Title = Title
