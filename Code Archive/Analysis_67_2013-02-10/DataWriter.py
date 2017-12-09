import sys

class DataWriterStdOut:

	def __init__(self, FileLocator, Flag):
	
		self.FileLocator = FileLocator
		self.File = open(FileLocator, Flag)
		self.Terminal = sys.stdout

	def write(self, Content):
		
		self.ToFileAndTerminal(Content)

	def ToFileAndTerminal(self, Content):
		
		self.File.write(Content)
		self.Terminal.write(Content)
		
	def ToFile(self, Content):
		
		self.File.write(Content)
		
	def ToTerminal(self, Content):
		
		self.Terminal.write(Content)

	def __del__(self):
		
		sys.stdout = self.Terminal
		self.File.close()

class DataWriterStdErr:

	def __init__(self, FileLocator, Flag):
	
		self.FileLocator = FileLocator
		self.File = open(FileLocator, Flag)
		self.Terminal = sys.stderr

	def write(self, Content):
		
		self.ToFileAndTerminal(Content)

	def ToFileAndTerminal(self, Content):
		
		self.File.write(Content)
		self.Terminal.write(Content)
		
	def ToFile(self, Content):
		
		self.File.write(Content)
		
	def ToTerminal(self, Content):
		
		self.Terminal.write(Content)

	def __del__(self):
		
		sys.stderr = self.Terminal
		self.File.close()
