########################################################################################################################
####
#### CHARTS
####
#### This module contains classes for containing histogram data, which can then be exported to ROOT objects.
#### 
#### Modified: 2013.01.25 21:55
#### Modified: 2013.02.12, Completed
#### 
#### DO NOT EDIT - PROTOTYPE CODE
####
########################################################################################################################


import gc

import ROOT 
import ROOTFile # Transitional Code

ROOT.gROOT.SetBatch(True)

import Colours


########################################################################################################################


# Configuration Constants

CreateStackedHistogramGroupsOnAssignment = True
DisplayStackedHistogramGroupsWithNoData = False


class HistogramCollection: 

	# This is a container class for the histogram objects.
	
	def __init__(This):
		
		This.Histograms = {} # The collection of histogram objects.
		
	def NewHistogram1D(This, Reference, Collection = "", Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = ""): # Create a new 1D histogram and add it to the dictionary.				
		This.Histograms[Reference] = Histogram1D(Reference, Collection, Title, XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum, YAxisTitle)
	
	def NewHistogram2D(This, Reference, Collection = "", Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100): # Create a new 2D histogram and add it to the dictionary.				
		This.Histograms[Reference] = Histogram2D(Reference, Collection, Title, XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum, YAxisTitle, YAxisNumberOfDivisions, YAxisMinimum, YAxisMaximum)
		
	def NewHistogram3D(This, Reference, Collection = "", Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100, ZAxisTitle = "", ZAxisNumberOfDivisions = 100, ZAxisMinimum = 0, ZAxisMaximum = 100):	# Create a new 3D histogram and add it to the dictionary.			
		This.Histograms[Reference] = Histogram3D(Reference, Collection, Title, XAxisTitle, YAxisTitle, ZAxisTitle)
		
	def NewStackedHistogram1D(This, Reference, Collection = "", Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 10, XAxisMinimum = 0, XAxisMaximum = 10, YAxisTitle = "", GroupReferences = []): # Create a new 1D stacked histogram and add it to the dictionary.
		This.Histograms[Reference] = StackedHistogram1D(Reference, Collection, Title, XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum, YAxisTitle, GroupReferences)
	
	def ToROOTHistogramCollection(This): # Convert the histograms to ROOT histogram objects and export the collection.
		
		ROOTHistograms = {}
		
		if (len(This.Histograms) > 0):
			for Histogram1 in This.Histograms:
				ROOTHistograms[Histogram1.Reference] = Histogram1.ToROOTHistogram()

		return ROOTHistograms	
	
	def ToHistogramStorage(This): # This is transitional code and will be deleted later.
		
		m1 = {}
		
		for Histogram1 in This.Histograms.values():
						
			HistogramStorage1 = ROOTFile.HistogramStorage()
			
			HistogramStorage1.Histogram = Histogram1.ToROOTHistogram()
			HistogramStorage1.HistogramDirectory = Histogram1.Collection
			
			m1[Histogram1.Reference] = HistogramStorage1
		
		return m1


class Histogram:
	
	# This is the base histogram class. All histograms inherit from this, however on its own it does not produce a histogram, nor store any histogram data.
	
	def __init__(This, Reference, Collection = "", Title = ""):
		
		This.Reference = Reference
		This.Collection = Collection
		This.Title = Title
		This.ShowLegend = False
		
class Histogram1D(Histogram):
	
	def __init__(This, Reference, Collection = "", Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = ""):
		
		Histogram.__init__(This, Reference, Collection, Title)
		
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle)
		
		# These additional attributes would eventually work in a different way; but for the moment there is no need.
		
		This.BinErrors = []
		
		This.Colour = Colours.Default
		This.MarkerStyle = 1
		This.Options = ""
		This.Statistics = 0
		
		This.Data = []	
	
	def Populate(This, X, W = None):
		
		if (W == None):
			This.Data.append([X])
		else:
			This.Data.append([X, W])
	
	def ToROOTHistogram(This):
		
		TH1D1 = ROOT.TH1D(This.Reference, This.Title, int(This.XAxis.NumberOfDivisions), float(This.XAxis.Minimum), float(This.XAxis.Maximum))
		
		TH1D1.SetXTitle(This.XAxis.Title)
		TH1D1.SetYTitle(This.YAxis.Title)	
		TH1D1.GetXaxis().CenterTitle()
		TH1D1.GetYaxis().CenterTitle()	
		
		TH1D1.SetFillColor(This.Colour)
		
		TH1D1.SetMarkerStyle(This.MarkerStyle)
		
		TH1D1.SetOption(This.Options)
		
		TH1D1.SetStats(This.Statistics)
		
		for DataItem in This.Data:
			if (len(DataItem) == 1):
				TH1D1.Fill(DataItem[0])
			if (len(DataItem) == 2):
				TH1D1.Fill(DataItem[0], DataItem[1])
		
		for BinError1 in This.BinErrors:
			if (len(BinError1) == 2):
				TH1D1.SetBinError(BinError1[0], BinError1[1])
		
		return TH1D1
	
	# This is transitional code and will be deleted later.
	def ToHistogramStorage(This): 
	
		HistogramStorage1 = ROOTFile.HistogramStorage()
		
		HistogramStorage1.Histogram = This.ToROOTHistogram()
		HistogramStorage1.HistogramDirectory = This.Collection
		
		return HistogramStorage1
		
class Histogram2D(Histogram):
	
	def __init__(This, Reference, Collection = "", Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100):
		
		Histogram.__init__(This, Reference, Collection, Title)
				
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle, YAxisNumberOfDivisions, YAxisMinimum, YAxisMaximum)
		
		This.Data = []	
	
	def Populate(This, X, Y):
		
		This.Data.append([X, Y])
	
	def ToROOTHistogram(This):
		
		TH2D1 = ROOT.TH2D(This.Reference, This.Title, int(This.XAxis.NumberOfDivisions), float(This.XAxis.Minimum), float(This.XAxis.Maximum), int(This.YAxis.NumberOfDivisions), float(This.YAxis.Minimum), float(This.YAxis.Maximum))
		
		TH2D1.SetXTitle(This.XAxis.Title)
		TH2D1.SetYTitle(This.YAxis.Title)
		TH2D1.GetXaxis().CenterTitle()
		TH2D1.GetYaxis().CenterTitle()
				
		for DataItem in This.Data:
			TH2D1.Fill(DataItem[0], DataItem[1])
			
		return TH2D1

class Histogram3D(Histogram):
	
	def __init__(This, Reference, Collection = "", Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", YAxisNumberOfDivisions = 100, YAxisMinimum = 0, YAxisMaximum = 100, ZAxisTitle = "", ZAxisNumberOfDivisions = 100, ZAxisMinimum = 0, ZAxisMaximum = 100):
		
		Histogram.__init__(This, Reference, Collection, Title)
				
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle, YAxisNumberOfDivisions, YAxisMinimum, YAxisMaximum)
		This.ZAxis = HistogramAxis(ZAxisTitle, ZAxisNumberOfDivisions, ZAxisMinimum, ZAxisMaximum)
		
		This.Data = []	
	
	def Populate(This, X, Y, Z):
		
		This.Data.append([X, Y, Z])
	
	def ToROOTHistogram(This):
		
		TH3D1 = ROOT.TH3D(This.Reference, This.Title, int(This.XAxis.NumberOfDivisions), float(This.XAxis.Minimum), float(This.XAxis.Maximum), int(This.YAxis.NumberOfDivisions), float(This.YAxis.Minimum), float(This.YAxis.Maximum), int(This.ZAxis.NumberOfDivisions), float(This.ZAxis.Minimum), float(This.ZAxis.Maximum))
		
		TH3D1.SetXTitle(This.XAxis.Title)
		TH3D1.SetYTitle(This.YAxis.Title)
		TH3D1.SetZTitle(This.ZAxis.Title)
		TH3D1.GetXaxis().CenterTitle()
		TH3D1.GetYaxis().CenterTitle()
		TH3D1.GetZaxis().CenterTitle()
				
		for DataItem in This.Data:
			TH1D1.Fill(DataItem[0], DataItem[1], DataItem[2])
			
		return TH3D1

class StackedHistogram1D(Histogram):
	
	def __init__(This, Reference, Collection = "", Title = "", XAxisTitle = "", XAxisNumberOfDivisions = 100, XAxisMinimum = 0, XAxisMaximum = 100, YAxisTitle = "", DataGroupReferences = []):
		
		Histogram.__init__(This, Reference, Collection, Title)
		
		This.XAxis = HistogramAxis(XAxisTitle, XAxisNumberOfDivisions, XAxisMinimum, XAxisMaximum)
		This.YAxis = HistogramAxis(YAxisTitle)
		
		This.DataGroups = {}
		
		if (len(DataGroupReferences) > 0):
			for DataGroupReference1 in DataGroupReferences:
				This.DataGroups[DataGroupReference1] = StackedHistogramDataGroup()
				
		This.THStack1 = ROOT.THStack(This.Reference, This.Title)
		This.TH1Ds = {}
		This.TLegend1 = ROOT.TLegend(0.7, 0.65, 0.86, 0.88, "")
		This.TPaveText1 = ROOT.TPaveText(0.1, 0.9, 0.9, 0.7, "r")
		
	def NewDataGroup(This, Reference, LegendTitle = "", LegendEntryStyle = ""):
		
		This.DataGroups[Reference] = StackedHistogramDataGroup(LegendTitle, LegendEntryStyle)		

	def Populate(This, GroupReference, X, GroupLegendTitle = "", GroupLegendEntryStyle = "f"):
		
		if GroupReference in This.DataGroups:
			This.DataGroups[GroupReference].Data.append([X])
		else:
			if (CreateStackedHistogramGroupsOnAssignment == True):
				This.DataGroups[GroupReference] = StackedHistogramDataGroup(GroupLegendTitle, GroupLegendEntryStyle)
		
	def ToROOTCanvas(This, Width = 700, Height = 490, AutoColour = True):
		
		TCanvas1 = ROOT.TCanvas(This.Reference + str("Canvas"), This.Title, Width, Height)
		
		IsData = False
		
		for DataGroup1 in This.DataGroups.values():
			if (len(DataGroup1.Data) > 0):
				IsData = True
		
		if (IsData == True):
			
			n1 = 1		
					
			for DataGroupReference1 in This.DataGroups.keys():
				if ((len(This.DataGroups[DataGroupReference1].Data) > 0) or (DisplayStackedHistogramGroupsWithNoData == True)):
				
					This.TH1Ds[DataGroupReference1] = ROOT.TH1D(This.Reference + "_" + str(DataGroupReference1), This.Title, int(This.XAxis.NumberOfDivisions), float(This.XAxis.Minimum), float(This.XAxis.Maximum))
					This.TH1Ds[DataGroupReference1].SetXTitle(This.XAxis.Title)
					This.TH1Ds[DataGroupReference1].SetYTitle(This.YAxis.Title)
					
					if (AutoColour == True):
						
						This.TH1Ds[DataGroupReference1].SetFillColor(Colours.PersistentColour(str(DataGroupReference1)))
						
						#This.TH1Ds[DataGroupReference1].SetFillColor(n1)
						#n1 += 1
					
					for DataItem1 in This.DataGroups[DataGroupReference1].Data:
						This.TH1Ds[DataGroupReference1].Fill(DataItem1[0])
					
					This.TLegend1.AddEntry(This.TH1Ds[DataGroupReference1], This.DataGroups[DataGroupReference1].LegendTitle, This.DataGroups[DataGroupReference1].LegendEntryStyle)	
																		
					This.THStack1.Add(This.TH1Ds[DataGroupReference1])
									
			This.THStack1.Draw()	
			
			This.THStack1.GetXaxis().SetTitle(This.XAxis.Title)
			This.THStack1.GetYaxis().SetTitle(This.YAxis.Title)			
			
			This.THStack1.GetXaxis().CenterTitle()
			This.THStack1.GetYaxis().CenterTitle()
			
			This.TLegend1.Draw()
		
		else:
			
			This.TPaveText1.AddText("In finalisation, this histogram was found not to contain any data, and so was not drawn to the canvas.")
			
			This.TPaveText1.Draw()
		
		return TCanvas1
		
	
	def ToROOTHistogram(This):
		
		return This.ToROOTCanvas()
	
	def ToNormalisedStackedHistogram(This):
		
		# This is incomplete.
		
		StackedHistogram1D1 = StackedHistogram1D(This.Reference, This.Title, This.XAxis.Title, This.XAxis.NumberOfDivisions, This.XAxis.Minimum, This.XAxis.Maximum, This.YAxis.Title, This.DataGroups.keys())
		
		for DataGroupReference1 in This.DaraGroups.keys():
			for DataItem1 in This.DaraGroups[DataGroupReference1].Data:
				StackedHistogram1D1.Populate(DataGroupReference1, DataItem[0])
	
	def ToHistogramStorage(This): # Transitional code.
				
		HistogramStorage1 = ROOTFile.HistogramStorage()
		
		HistogramStorage1.Histogram = This.ToROOTCanvas()
		HistogramStorage1.HistogramDirectory = This.Collection
		
		return HistogramStorage1		
		

class HistogramAxis:
	
	def __init__(This, Title = "", NumberOfDivisions = 100, Minimum = 0, Maximum = 100):
		
		This.Title = Title
		This.NumberOfDivisions = NumberOfDivisions
		This.Minimum = Minimum
		This.Maximum = Maximum
		This.Labels = []

class StackedHistogramDataGroup:
	
	def __init__(This, LegendTitle = "", LegendEntryStyle = "f"):
		
		This.Data = []
		This.LegendTitle = LegendTitle
		This.LegendEntryStyle = LegendEntryStyle

class HistogramLegend:
	
	def __init__(This, Title = ""):
		
		This.Title = Title
