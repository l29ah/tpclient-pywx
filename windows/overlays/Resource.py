"""\
This overlay shows circles which are proportional to the amount of a certain
resource found in that object.
"""
# Python imports
import os
from math import *

import numpy as N

# wxPython imports
import wx
from extra.wxFloatCanvas import FloatCanvas
from extra.wxFloatCanvas.RelativePoint import RelativePoint
from extra.wxFloatCanvas.Icon import Icon

from extra.wxFloatCanvas.NavCanvas import NavCanvas

class Resource(Proportional):
	"""\
	Draws proportional circles for the relative number of resources.
	"""
	TOTAL		= -1
	SURFACE	  = 1
	MINABLE	  = 2
	INACCESSABLE = 3	

	def __init__(self, canvas, cache, resource, type=-1):
		Overlay.__init__(self, canvas, cache)

		self.resource = resource
		self.type     = type
	
	def amount(self, oid):
		"""\
		The amount of this resource on this object.
		"""
		c = self.cache 
		o = c.objects[oid]

		amount = 0
		if hasattr(self, "contains"):
			for child in o.contains:
				amount += self.amount(child)

		if hasattr(self, "resources"):
			for resource in o.resources:
				rid = resource[0]

				if rid == self.resource:
					if self.type == Resource.TOTAL:
						amount += reduce(int.__add__, resource[1:])
					else:
						amount += resouce[self.type]
					break

		return amount
