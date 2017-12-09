# Statistics
#
# This module contains classes to display simple, named statistical data in a standard format.
#
# Modified 2013.01.26 22:21
#


import TextConstants


class Collection:
	
	def __init__(This, Title = ""):
		
		This.Title = Title
		This.Statistics = {}
		
	def ToText(This):
		
		Text = ""
		
		Text += TextConstants.LineSeparator + TextConstants.NewLine
		Text += This.Title + TextConstants.NewLine
		Text += TextConstants.LineSeparator + TextConstants.NewLine
		
		# This is an inefficient approach to ordering the dictionary, but it will do for now.
		
		for i in range(len(This.Statistics)):
			for Statistic1 in This.Statistics.itervalues():
				if (Statistic1.Index == i + 1):
					Text += Statistic1.ToText() + TextConstants.NewLine
		
		return Text
	
	def NewStatistic(This, Reference, Title = "", Quantity = 0):
		
		NewIndex = len(This.Statistics) + 1
		
		Statistic1 = Statistic(NewIndex, Title, Quantity)
		
		This.Statistics[Reference] = Statistic1
	 

class Statistic: # This is a container class for simple statistical data.
	
	def __init__(This, Index = 0, Title = "", Quantity = 0):
		
		This.Index = Index
		This.Title = Title
		This.Quantity = Quantity
		
	def ToText(This):
		
		Text = This.Title + ": " + str(This.Quantity) + "."
		
		return Text
