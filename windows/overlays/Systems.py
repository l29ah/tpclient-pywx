"""\
This overlay draws Star Systems on the Starmap.
"""
# Python imports
from math import *

import numpy as N

# wxPython imports
import wx
from extra.wxFloatCanvas.FloatCanvas import Point, Group
from extra.wxFloatCanvas.RelativePoint import RelativePoint, RelativePointSet

from extra.wxFloatCanvas.FloatCanvas import EVT_FC_ENTER_OBJECT, EVT_FC_LEAVE_OBJECT
from extra.wxFloatCanvas.FloatCanvas import EVT_FC_LEFT_UP, EVT_FC_RIGHT_UP

# tp imports
from tp.netlib.objects.ObjectExtra.Galaxy import Galaxy
from tp.netlib.objects.ObjectExtra.Universe import Universe
from tp.netlib.objects.ObjectExtra.StarSystem import StarSystem
from tp.netlib.objects.ObjectExtra.Planet import Planet
from tp.netlib.objects.ObjectExtra.Fleet import Fleet

class GenericIcon(Group):
	PrimarySize = 3
	ChildSize   = 3

	def __init__(self, pos, type, children=[]):
		ObjectList = []

		# The center Point
		ObjectList.append(Point(pos, type, self.PrimarySize, False))

		if len(children) > 0:
			# The orbit bits
			ObjectList.insert(0, Point(pos, "Black", 8))
			ObjectList.insert(0, Point(pos, "Grey",  9, False))
	
			# The orbiting children
			for i, childtype in enumerate(children):
				ObjectList.append(RelativePoint(pos, childtype, self.ChildSize, False, 
									self.ChildOffset(i, len(children))))

		Group.__init__(self, ObjectList, False)

	def XY(self):
		return self.ObjectList[0].XY
	XY = property(XY)

	def ChildOffset(self, i, num):
		angle = ((2.0*pi)/num)*(i-0.125)
		return (int(cos(angle)*6), int(sin(angle)*6))

from Colorizer import *
class Holder(list):
	def __init__(self, cache, parent, children=[]):
		"""

		"""
		self.cache = cache

		if not isinstance(parent, (int, long)):
			raise TypeError("Parent must be an ID's not %r" % parent) 
		for i, child in enumerate(children):
			if not isinstance(child, (int, long)):
				raise TypeError("Child %i must be an ID's not %r" % (i, child)) 

		self.extend([parent] + children)
		self.ResetLoop()

	def ResetLoop(self):
		self.current = -1

	def NextLoop(self):
		self.current = (self.current + 1) % len(self)
		return self.current, self[self.current]

	def SetColorizer(self, colorizer):
		if not isinstance(colorizer, Colorizer):
			raise TypeError('Colorizer must be of Colorizer type!')
		self.Colorizer = colorizer

	def GetColors(self):
		parentcolor = self.Colorizer(FindOwners(self.cache, self[0]))
		
		childrencolors = []
		for child in self[1:]:
			childrencolors.append(self.Colorizer(FindOwners(self.cache, child)))
	
		return parentcolor, childrencolors

	def __eq__(self, value):
		return [self[0], self.current] == value

def FindChildren(cache, oid):
	"""
	Figure out all the children of this object.
	"""
	if not isinstance(oid, (int, long)):
		raise TypeError("oid must be a oid not %r" % oid)

	kids = set()
	for child in cache.objects[oid].contains:
		kids.update(FindChildren(cache, child))
		kids.add(child)

	return list(kids)

def FindOwners(cache, oid):
	"""
	Figure out the owners of this oidect (and it's children).
	"""
	if not isinstance(oid, (int, long)):
		raise TypeError("oid must be a oid not %r" % oid)

	owners = set()
	for child in [oid]+FindChildren(cache, oid):
		if not hasattr(cache.objects[child], 'owner'):
			continue

		owner = cache.objects[child].owner
		if owner in (0, -1):
			continue
		owners.add(owner)
	return list(owners)

from Overlay import Overlay

from wx.lib.fancytext import StaticFancyText
class NamePopup(wx.PopupWindow):
	Padding = 2

	def __init__(self, parent, style):
		wx.PopupWindow.__init__(self, parent, style)

		self.parent = parent

		self.SetBackgroundColour("#202020")
		self.Bind(wx.EVT_MOTION, parent.MotionEvent)

	def SetText(self, text):
		try:
			self.st.Unbind(wx.EVT_MOTION)
			self.st.Destroy()
		except AttributeError:
			pass

		self.st = StaticFancyText(self.Window, -1, text, pos=(self.Padding, self.Padding))
		sz = self.st.GetSize()
		self.SetSize( (sz.width+2*self.Padding, sz.height+2*self.Padding) )

		self.st.Bind(wx.EVT_MOTION, self.parent.MotionEvent)

class Systems(Overlay):
	toplevel = Galaxy, Universe

	def __init__(self, *args, **kw):
		Overlay.__init__(self, *args, **kw)

		self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_RIGHT_ARROW))
		self.Selected = None

		self.PopupText = NamePopup(self.canvas, wx.SIMPLE_BORDER)

	def updateall(self):
		#self.Colorizer = ColorVerses(self.cache.players[0].id)
		self.Colorizer = ColorEach()

		Overlay.updateall(self)

		from extra.wxFloatCanvas.Arrow import Arrow
		self['arrow'] = Arrow((0,0), "Red", True)

	def updateone(self, oid):
		"""\

		"""
		obj = self.cache.objects[oid]

		# Only draw top level objects
		if isinstance(obj, Systems.toplevel):
			return

		# Don't draw objects which parent's are not top level objects
		parent = self.cache.objects[obj.parent]
		if not isinstance(parent, Systems.toplevel):
			return

		holder = Holder(self.cache, oid, FindChildren(self.cache, oid))
		holder.SetColorizer(self.Colorizer)

		self[oid] = GenericIcon(obj.pos[0:2], *holder.GetColors())
		self[oid].holder = holder

		# These pop-up the name of the object
		self[oid].Bind(EVT_FC_ENTER_OBJECT, self.SystemEnter)
		self[oid].Bind(EVT_FC_LEAVE_OBJECT, self.SystemLeave)
		self[oid].Bind(EVT_FC_LEFT_UP, self.SystemLeftClick)

	def SystemLeftClick(self, obj):
		print "SystemClick", obj

		# Are we clicking on the same object?
		if self.Selected != obj.holder:
			self.Selected = obj.holder
			self.Selected.ResetLoop()

		# Cycle throught the children on each click
		i, rid = self.Selected.NextLoop()
		
		self['arrow'].SetPoint(self.cache.objects[obj.holder[0]].pos[0:2])
		self['arrow'].SetOffset((0,0))
		if i > 0:
			self['arrow'].SetOffset(obj.ChildOffset(i-1, len(obj.holder)-1))

		self.canvas.Draw(True)

		self.SystemLeave(obj)
		self.SystemEnter(obj)

	def SystemEnter(self, obj):
		print "SystemEnter", obj
		screen = self.canvas.WorldToPixel(obj.XY)
		pos	= self.canvas.ClientToScreen( screen )

		# Build the string
		s = "<font size='%s'>" % wx.local.normalFont.GetPointSize()
		for i, cid in enumerate(obj.holder):
			cobj = self.cache.objects[cid]

			style = 'normal'
			if [obj.holder[0], i] == self.Selected:
				style = 'italic'

			color = obj.holder.Colorizer(FindOwners(self.cache, cid))

			s += "<font style='%s' color='%s'>%s" % (style, color, cobj.name)
			if isinstance(cobj, Fleet):
				for shipid, amount in cobj.ships:
					s+= "\n  %s %ss" % (amount, self.cache.designs[shipid].name)
			s += "</font>\n"

		s = s[:-1]+"</font>"

		self.PopupText.SetText(s)
		self.PopupText.Position(pos, (GenericIcon.PrimarySize, GenericIcon.PrimarySize))
		self.PopupText.Show(True)

		# Also do a "preview" event after X seconds

	def SystemLeave(self, evt):
		print "SystemLeave", evt
		self.PopupText.Hide()
