"""\
All the windows are controlled by this class

"""

# wxPython imports
from wxPython.wx import *

# Python Imports
from utils import *
from config import *

class MainControl:

	def ConfigLoad(self):
		config = load_data("windows")

		if not config:

			# Create some default positioning, good for 1024x768 on linux
			config = Blank()
			config.main = Blank()
			config.message = Blank()
			config.starmap = Blank()
			config.system = Blank()

			sc_width = 1024
			sc_height = 768

			map_width = 600
			map_height = 500

			padding = 5

			middle = sc_width-map_width-padding

			config.main.pos = (0,0)
			config.main.size = (middle, 50)
			config.main.show = TRUE
			
			config.message.pos = (0, map_height-padding*4)
			config.message.size = (middle, 200)
			config.message.show = TRUE

			config.starmap.pos = (middle+padding, 0)
			config.starmap.size = (map_width-padding, map_height-padding*2)
			config.starmap.show = TRUE

			config.system.pos = (middle+padding, map_height)
			config.system.size = (map_width-padding, 200)
			config.system.show = TRUE
		
			config.raise_ = "All on All" 
	
		return config

	def ConfigSave(self):
		config = self.config
		config.main.pos = self.main.GetPositionTuple()
		config.main.size = self.main.GetSizeTuple()
		config.main.show = self.main.IsShown()
		config.message.pos = self.message.GetPositionTuple()
		config.message.size = self.message.GetSizeTuple()
		config.message.show = self.main.IsShown()
		config.starmap.pos = self.starmap.GetPositionTuple()
		config.starmap.size = self.starmap.GetSizeTuple()
		config.starmap.show = self.main.IsShown()
		config.system.pos = self.system.GetPositionTuple()
		config.system.size = self.system.GetSizeTuple()
		config.system.show = self.main.IsShown()

		save_data("windows", config)

	def ConfigActivate(self, show=TRUE):
		config = self.config

		self.main.SetPosition(config.main.pos)
		self.main.SetSize(config.main.size)
		self.message.SetPosition(config.message.pos)
		self.message.SetSize(config.message.size)
		self.starmap.SetPosition(config.starmap.pos)
		self.starmap.SetSize(config.starmap.size)
		self.system.SetPosition(config.system.pos)
		self.system.SetSize(config.system.size)
		
		if show:
			self.main.Show(config.main.show)
			self.message.Show(config.message.show)
			self.starmap.Show(config.starmap.show)
			self.system.Show(config.system.show)

	def __init__(self, app):

		self.app = app

		##########
		# Load the windows
		##########
		from windows.winConfig  import winConfig
		from windows.winConnect import winConnect
		from windows.winMain    import winMain
		from windows.winMessage import winMessage
		from windows.winStarMap import winStarMap
		from windows.winSystem  import winSystem

		config = self.ConfigLoad()
		self.config = config

		self.main = winMain(app, config.main.pos, config.main.size)

		self.winconfig = winConfig(app, self.main)
		self.connect = winConnect(app, -1, None)
		
		self.message = winMessage(app, self.main, config.message.pos, config.message.size)
		
		self.starmap = winStarMap(app, self.main, config.starmap.pos, config.starmap.size)
		self.system = winSystem(app, self.main, config.system.pos, config.system.size)

		self.ConfigActivate(FALSE)

	def Raise(self):
		"""\
			Raise all the windows.
		"""
		self.system.Raise()
		self.message.Raise()
		self.starmap.Raise()
		self.main.Raise()

		self.winconfig.Raise()
		self.connect.Raise()

	def Show(self):
		"""\
			Show the main window
		"""
		config = self.config
		self.main.Show(config.main.show)
		self.message.Show(config.message.show)
		self.starmap.Show(config.starmap.show)
		self.system.Show(config.system.show)

		# Move everything to there home positions
		self.ConfigActivate()

	def Hide(self):
		"""\
			Show the main window
		"""
		self.main.Show(FALSE)
		self.message.Show(FALSE)
		self.starmap.Show(FALSE)
		self.system.Show(FALSE)

