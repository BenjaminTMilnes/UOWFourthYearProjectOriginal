import ROOT

class DataCollection:
	
	def __init__(self, FileLocator):
		
		self.FileLocator = FileLocator
		self.TChain = ROOT.TChain(FileLocator)
	
