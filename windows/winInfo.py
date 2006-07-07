"""\
This module contains the Information window. The Information window
displays all objects information.
"""

import os
import os.path
from types import *

import pprint

# wxPython imports
import wx

try:
	from extra.GIFAnimationCtrl import GIFAnimationCtrl
except ImportError:
	from wx.animate import GIFAnimationCtrl

# Network imports
from tp.netlib.objects.ObjectExtra.Universe import Universe
from tp.netlib.objects.ObjectExtra.Galaxy import Galaxy
from tp.netlib.objects.ObjectExtra.StarSystem import StarSystem
from tp.netlib.objects.ObjectExtra.Planet import Planet
from tp.netlib.objects.ObjectExtra.Fleet import Fleet

# Local imports
from winBase import *
from utils import *

def splitall(start):
	bits = []

	while True:
		start, end = os.path.split(start)
		if end is '':
			break
		bits.append(end)
	bits.reverse()
	return bits


WAITING = os.path.join(".", "graphics", "loading.gif")
class winInfo(winBase):
	title = _("Information")

	from defaults import winInfoDefaultPosition as DefaultPosition
	from defaults import winInfoDefaultSize as DefaultSize
	from defaults import winInfoDefaultShow as DefaultShow

	def __init__(self, application, parent):
		winBase.__init__(self, application, parent)

		self.titletext = wx.StaticText(self, -1, _("No Object Selected."))

		self.picture_panel = wx.Panel(self)
		self.picture_panel.SetBackgroundColour(wx.Colour(0, 0, 0))

		self.picture_still = wx.StaticBitmap(self.picture_panel, -1, wx.BitmapFromImage(wx.EmptyImage(128, 128)))

		self.picture_animated = GIFAnimationCtrl(self.picture_panel, -1)
		self.picture_animated.SetBackgroundColour(wx.Colour(0, 0, 0))
		self.picture_animated.Stop(); self.picture_animated.Hide()

		self.text = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)

		top = wx.BoxSizer(wx.VERTICAL)
		top.Add(self.titletext, 0, wx.BOTTOM|wx.TOP|wx.ALIGN_CENTER, 3)

		information = wx.BoxSizer(wx.VERTICAL)
		information.Add(self.text, 1, wx.EXPAND, 0)
		
		middle = wx.BoxSizer(wx.HORIZONTAL)
		middle.Add(self.picture_panel,    0, 0, 0)
		middle.Add(information, 1, wx.EXPAND, 0)

		top.Add(middle, 1, wx.EXPAND, 0)

		self.SetSizer(top)

		# Find the images
		self.images = {'nebula':{'still':[]}, 'star':{'still':[]}, 'planet':{'still':[]}}

	def OnMediaUpdate(self, evt):
		print
		print "winInfo.OnMediaUpdate", evt
		files = {}
		for file, timestamp in evt.files:
			bits = splitall(file)
	
			if bits[-2] in ['animation', 'still']:
				type = bits[-2]
				del bits[-2]
			else:
				type = 'still'
	
			if not bits[-2].endswith("-small"):
				continue
			else:
				key = bits[-2][:-6]
				if not files.has_key(key):
					files[key] = {}
				if not files[key].has_key(type):
					files[key][type] = []
				files[key][type].append((file, timestamp))
		self.images = files
	
	def OnMediaDownloadDone(self, evt):
		if evt.file == self.image_waiting:
			# FIXME: Should load the image now...
			pass	

	def OnSelectObject(self, evt):
		print "winInfo SelectObject", evt
		try:
			object = self.application.cache.objects[evt.id]
		except:
			do_traceback()
			debug(DEBUG_WINDOWS, "SelectObject: No such object.")
			return

		self.titletext.SetLabel(object.name)

		# Figure out the right graphic
		if isinstance(object, (Universe, Galaxy)):
			images = self.images['nebula']
		elif isinstance(object, StarSystem):
			images = self.images['star']
		elif isinstance(object, Planet):
			images = self.images['planet']
		else:
			images = {'still': []}

		print
		pprint.pprint(images)
		print

		if images.has_key("animation"):
			images = images["animation"]
		else:
			images = images["still"]

		print
		pprint.pprint(images)
		print

		try:
			image = images[object.id % len(images)]
			file = self.application.media.GetFile(*image)
			if file is None:
				self.image_waiting = image
				file = WAITING
		
			if file.endswith(".gif"):
				print "Animated image!"
				self.picture_still.Hide()
				print "Showing the Image"	
				self.picture_animated.Show()
				print "Loading Image"
				self.picture_animated.LoadFile(file)
				print "Playing the Image"
				self.picture_animated.Play()
			else:
				print "Still image!"
				self.picture_still.Show()
				self.picture_animated.Stop()
				self.picture_animated.Hide()

			bitmap = wx.BitmapFromImage(wx.Image(file))
		except:
			bitmap = wx.BitmapFromImage(wx.EmptyImage(128, 128))
			self.picture_still.SetBitmap(bitmap)

		self.Layout()

		# Add the object type specific information
		s = ""
		for key, value in object.__dict__.items():
			if key.startswith("_") or key in \
				('protocol', 'sequence', 'otype', 'length', 'order_types', 'order_number', 'contains'):
				continue

			if key == "ships":
				s += "ships: "
				for t, number in value:
					design = self.application.cache.designs[t]
					s += "%s %s, " % (number, design.name)
				s = s[:-2] + "\n"
				continue

			if type(value) == StringType:
				s += "%s: '%s'\n" % (key, value)
			elif type(value) in (ListType, TupleType):
				s += "%s: " % (key,)
				for i in value:
					s += "%s, " % (i,)
				s = s[:-2] + "\n"
			else:
				s += "%s: %s\n" % (key, value)

		self.text.SetValue(s)

