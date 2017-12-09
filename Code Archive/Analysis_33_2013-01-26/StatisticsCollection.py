# Statistics Collection
#
# This is a container class for simple statistical data.
#
# Last Modified 2013.01.13 21:07
#

import Statistic
import TextConstants

class StatisticsCollection:
	
	def __init__(self, Title = ""):
		
		self.Title = Title
		self.Statistics = {}
		
	def ToText(self):
		
		Text = ""
		
		Text += TextConstants.LineSeparator + TextConstants.NewLine
		Text += self.Title + TextConstants.NewLine
		Text += TextConstants.LineSeparator + TextConstants.NewLine
		
		for Statistic1 in self.Statistics.itervalues():
			Text += Statistic1.ToText() + TextConstants.NewLine
		
		return Text
	
	def NewStatistic(self, Reference, Title, Quantity):
		
		Statistic1 = Statistic.Statistic(Title, Quantity)
		
		self.Statistics[Reference] = Statistic1
	 
