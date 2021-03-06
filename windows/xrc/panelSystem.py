# This file has been automatically generated.
# Please do not edit it manually.

# Python Imports
import os.path

# wxPython imports
import wx
from wx.xrc import XRCCTRL, XmlResourceWithHandlers

# Local imports
from requirements import location

class panelSystemBase(wx.Panel):
	xrc = os.path.join(location(), "windows", "xrc", 'panelSystem.xrc')

	def PreCreate(self, pre):
		""" This function is called during the class's initialization.
		
		Override it for custom setup before the window is created usually to
		set additional window styles using SetWindowStyle() and SetExtraStyle()."""
		pass

	def __init__(self, parent, *args, **kw):
		""" Pass an initialized wx.xrc.XmlResource into res """
		f = os.path.join(os.path.dirname(__file__), self.xrc)
		res = XmlResourceWithHandlers(f)		

		# Two stage creation (see http://wiki.wxpython.org/index.cgi/TwoStageCreation)
		pre = wx.PrePanel()
		res.LoadOnPanel(pre, parent, "panelSystem")
		self.PreCreate(pre)
		self.PostCreate(pre)

		# Define variables for the controls
		self.Tree = XRCCTRL(self, "Tree")
		self.PrevObject = XRCCTRL(self, "PrevObject")
		if hasattr(self, "OnPrevObject"):
			self.Bind(wx.EVT_BUTTON, self.OnPrevObject, self.PrevObject)

		self.NextObject = XRCCTRL(self, "NextObject")
		if hasattr(self, "OnNextObject"):
			self.Bind(wx.EVT_BUTTON, self.OnNextObject, self.NextObject)

		self.StepInto = XRCCTRL(self, "StepInto")
		if hasattr(self, "OnStepInto"):
			self.Bind(wx.EVT_BUTTON, self.OnStepInto, self.StepInto)

		self.Search = XRCCTRL(self, "Search")


def strings():
	pass

