"""\
The order window.
"""

# Python Imports
import time
import copy

# wxPython Imports
import wx
import wx.lib.anchors
import wx.lib.mixins.listctrl

# Local Imports
from winBase import *
from utils import *

# Protocol Imports
from netlib import failed
from netlib import objects
from netlib.objects import OrderDescs, constants

TURNS_COL = 0
ORDERS_COL = 1

wx.ListCtrlOrig = wx.ListCtrl
class wxListCtrl(wx.ListCtrlOrig, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
		wx.ListCtrlOrig.__init__(self, parent, ID, pos, size, style)
		wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

		self.tooltips = {}
		self.objects = {}

		self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

	def SetItemPyData(self, slot, data):
		self.objects[slot] = data

	def GetItemPyData(self, slot):
		try:
			return self.objects[slot]
		except:
			return None

	def FindItemByPyData(self, data):
		slot = -1
		while True:
			slot = self.GetNextItem(slot, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE);
			if slot == wx.NOT_FOUND:
				return wx.NOT_FOUND
				
			if self.GetItemPyData(slot) == data:
				return slot

	def GetStringItem(self, slot, col):
		item = self.GetItem(slot, col)
		if item == wx.NOT_FOUND:
			return wx.NOT_FOUND
		else:
			return item.GetText()

	def SetToolTip(self, tooltip):
		if isinstance(tooltip, wx.ToolTip):
			tooltip = tooltip.GetTip()
		self.tooltips[-1] = tooltip
		wx.ListCtrlOrig.SetToolTip(self, wx.ToolTip(tooltip))

	def SetToolTipItem(self, slot, text):
		self.tooltips[slot] = text
	
	def GetToolTipItem(self, slot):
		if self.tooltips.has_key(slot):
			return self.tooltips[slot]
		else:
			return None
	
	def OnMouseMotion(self, evt):
		slot = self.HitTest(evt.GetPosition())[0]
		
		if self.tooltips.has_key(slot):
			if self.GetToolTip() == None:
				wx.ListCtrlOrig.SetToolTip(self, wx.ToolTip(self.tooltips[slot]))
			elif self.GetToolTip().GetTip() != self.tooltips[slot]:
				self.GetToolTip().SetTip(self.tooltips[slot])

wx.ListCtrl = wxListCtrl

wx.ChoiceOrig = wx.Choice
class wxChoice(wx.Choice):
	def __init__(self, *arg, **kw):
		wx.ChoiceOrig.__init__(self, *arg, **kw)

		self.tooltips = {}
		self.Bind(wx.EVT_CHOICE, self.OnSelection)

	def SetToolTip(self, tooltip):
		if isinstance(tooltip, wx.ToolTip):
			tooltip = tooltip.GetTip()
		self.tooltips[-1] = tooltip
		wx.ChoiceOrig.SetToolTip(self, wx.ToolTip(tooltip))

	def SetToolTipItem(self, slot, text):
		self.tooltips[slot] = text
	
	def GetToolTipItem(self, slot):
		if self.tooltips.has_key(slot):
			return self.tooltips[slot]
		else:
			return None
	
	def OnSelection(self, evt):
		slot = self.GetSelection()
		
		if self.tooltips.has_key(slot):
			if self.GetToolTip() == None:
				wx.ChoiceOrig.SetToolTip(self, wx.ToolTip(self.tooltips[slot]))
			elif self.GetToolTip().GetTip() != self.tooltips[slot]:
				self.GetToolTip().SetTip(self.tooltips[slot])

wx.Choice = wxChoice
buttonSize = (wx.local.buttonSize[0], wx.local.buttonSize[1]+2)

class winOrder(winBase):
	title = "Orders"
	
	def __init__(self, application, parent, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
		winBase.__init__(self, application, parent, pos, size, style)

		self.application = application

		# Create a base panel
		base_panel = wx.Panel(self, -1)
		base_panel.SetAutoLayout( True )

		# Create a base sizer
		base_sizer = wx.BoxSizer( wx.VERTICAL )
		base_sizer.Fit( base_panel )
		base_sizer.SetSizeHints( base_panel )

		# Link the panel to the sizer
		base_panel.SetSizer( base_sizer )
		
		# List of current orders
		order_list = wx.ListCtrl( base_panel, -1, wx.DefaultPosition, wx.Size(160,80), wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER )
		order_list.InsertColumn(TURNS_COL, "Turns")
		order_list.SetColumnWidth(TURNS_COL, 40)
		order_list.InsertColumn(ORDERS_COL, "Order Information")
		order_list.SetColumnWidth(ORDERS_COL, 140)
		order_list.SetFont(wx.local.normalFont)

		# A horizontal line
		line_horiz1 = wx.StaticLine( base_panel, -1, wx.DefaultPosition, wx.Size(20,-1), wx.LI_HORIZONTAL)
		line_horiz2 = wx.StaticLine( base_panel, -1, wx.DefaultPosition, wx.Size(20,-1), wx.LI_HORIZONTAL)

		# Buttons to add/delete orders
		button_sizer = wx.FlexGridSizer( 1, 0, 0, 0 )
		
		new_button = wx.Button( base_panel, -1, "New", size=wx.local.buttonSize)
		new_button.SetFont(wx.local.normalFont)
		
		type_list = wx.Choice( base_panel, -1, choices=[], size=wx.local.buttonSize)
		type_list.SetFont(wx.local.tinyFont)
		
		line_vert = wx.StaticLine( base_panel, -1, wx.DefaultPosition, wx.Size(-1,10), wx.LI_VERTICAL )

		delete_button = wx.Button( base_panel, -1, "Delete", size=wx.local.buttonSize)
		delete_button.SetFont(wx.local.normalFont)
		
		button_sizer.AddWindow( new_button,    0, wx.ALIGN_CENTRE, 1 )
		button_sizer.AddWindow( type_list,     0, wx.ALIGN_CENTRE, 1 )
		button_sizer.AddWindow( line_vert,     0, wx.ALIGN_CENTRE, 1 )
		button_sizer.AddWindow( delete_button, 0, wx.ALIGN_CENTRE, 1 )
		
		# Order arguments
		argument_sizer = wx.FlexGridSizer( 0, 1, 0, 0)
		argument_panel = wx.Panel(base_panel, -1)

		# Link the argument sizer with the new panel
		argument_panel.SetSizer(argument_sizer)
		argument_panel.SetAutoLayout( True )

		# Put them all on the sizer
		base_sizer.AddWindow( order_list, 1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1 )
		base_sizer.AddWindow( line_horiz1, 0, wx.ALIGN_CENTRE|wx.ALL, 1 )
		base_sizer.AddSizer ( button_sizer, 0, wx.ALIGN_CENTRE|wx.ALL, 1 )
		base_sizer.AddWindow( line_horiz2, 0, wx.ALIGN_CENTRE|wx.ALL, 1 )
		base_sizer.AddWindow( argument_panel, 0, wx.GROW|wx.ALIGN_CENTER|wx.ALL, 1 )

		self.oid = -1
		self.app = application
		self.base_panel = base_panel
		self.base_sizer = base_sizer
		self.order_list = order_list
		self.type_list = type_list
		self.argument_sizer = argument_sizer
		self.argument_panel = argument_panel

		self.Bind(wx.EVT_BUTTON, self.OnOrderNew, new_button)
		self.Bind(wx.EVT_BUTTON, self.OnOrderDelete, delete_button)
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnOrderSelect, order_list)

		self.SetSize(size)
		self.SetPosition(pos)

	def OnSelectType(self, evt):
		print "Selecting!"

	def OnSelectObject(self, evt):
		oslot = self.order_list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

		self.oid = evt.id

		try:
			object = self.application.cache.objects[self.oid]
		except:
			debug(DEBUG_WINDOWS, "SelectObject: No such object.")
			return
			
		self.order_list.SetToolTip("Current orders on %s." % object.name)
		
		self.order_list.DeleteAllItems()
		for slot in range(0, object.order_number):
			order = self.application.cache.orders[self.oid][slot]

			self.order_list.InsertStringItem(slot, "")
			self.order_list.SetStringItem(slot, TURNS_COL, str(order.turns))
			self.order_list.SetStringItem(slot, ORDERS_COL, order.name)
			self.order_list.SetToolTipItem(slot, "Tip %s" % slot)

			if slot == oslot:
				self.order_list.Select(slot)
				self.BuildPanel(order)
			
		# Set which orders can be added to this object
		self.type_list.Clear()
		self.type_list.SetToolTip("Order type to create")
		for type in object.order_types:
			if not OrderDescs().has_key(type):
				continue

			od = OrderDescs()[type]
			
			self.type_list.Append(od.name, type)
			if hasattr(od, "doc"):
				desc = od.doc
			else:
				desc = od.__doc__
			desc = desc.strip()
			self.type_list.SetToolTipItem(self.type_list.GetCount()-1, desc)

		self.OnOrderSelect(None)

	def OnOrderSelect(self, evt):
		slot = self.order_list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if slot == wx.NOT_FOUND:
			order = None
		else:
			order = self.application.cache.orders[self.oid][slot]

		self.BuildPanel(order)

	def OnOrderNew(self, evt):
		type = self.type_list.GetSelection()
		if type == wx.NOT_FOUND:
			debug(DEBUG_WINDOWS, "OrderNew: No order type selected for new.")
			return
			
		type = self.type_list.GetClientData(type)
			
		# Append a new order to the list below the currently selected one
		slot = self.order_list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if slot == wx.NOT_FOUND:
			debug(DEBUG_WINDOWS, "OrderNew: No orders in the order list.")
			slot = 0
		else:
			slot += 1
			
		try:
			orderdesc = OrderDescs()[type]
		except:
			debug(DEBUG_WINDOWS, "OrderNew: Have not got OrderDesc yet (%i)" % type)
			return
			
		args = []
		for name, type in orderdesc.names:
			if type == constants.ARG_ABS_COORD:
				args += [0,0,0]
			elif type == constants.ARG_TIME:
				args += [0]
			elif type == constants.ARG_OBJECT:
				args += [0]
			elif type == constants.ARG_PLAYER:
				args += [0,0]
			elif type == constants.ARG_REL_COORD:
				args += [0,0,0,0]
			elif type == constants.ARG_RANGE:
				args += [0,0,0,0]
			elif type == constants.ARG_LIST:
				args += [[],[]]
			elif type == constants.ARG_STRING:
				args += [0,""]

		r = self.application.connection.insert_order(self.oid, slot, orderdesc.subtype, *args)
		if failed(r):
			debug(DEBUG_WINDOWS, "OrderNew: Insert failed")
			return
					
		order = self.application.connection.get_orders(self.oid, slot)[0]
		if failed(order):
			debug(DEBUG_WINDOWS, "OrderNew: Get failed")
			return

		self.application.cache.orders[self.oid].insert(slot, order)
		self.application.cache.objects[self.oid].order_number += 1

		self.OnSelectObject(wx.local.SelectObjectEvent(self.oid))

	def OnOrderDelete(self, evt):
		slot = self.order_list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if slot == wx.NOT_FOUND:
			debug(DEBUG_WINDOWS, "OrderDelete: No order selected for delete.")
			return
			
		# Remove the order
		r = self.application.connection.remove_orders(self.oid, slot)
		if failed(r):
			debug(DEBUG_WINDOWS, "OrderDelete: Remove failed!")
			return

		del self.application.cache.orders[self.oid][slot]
		self.application.cache.objects[self.oid].order_number -= 1

		self.OnSelectObject(wx.local.SelectObjectEvent(self.oid))

	def OnOrderSave(self, evt):
		slot = self.order_list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if slot == wx.NOT_FOUND:
			debug(DEBUG_WINDOWS, "OrderSave: No order selected for save.")
			return

		try:
			order = self.application.cache.orders[self.oid][slot]
		except:
			debug(DEBUG_WINDOWS, "OrderSave: Could not get order")
			return
		
		try:
			orderdesc = OrderDescs()[order.type]
		except:
			debug(DEBUG_WINDOWS, "OrderSave: No order description.")
			return

		args = [order.sequence, order.id, order.slot, order.type, 0, []]

		subpanels = copy.copy(self.argument_subpanels)
		for name, type in orderdesc.names:
			panel = subpanels.pop(0)
				
			if type == constants.ARG_ABS_COORD:
				args += argCoordGet( panel )
			elif type == constants.ARG_TIME:
				args += argTimeGet( panel )
			elif type == constants.ARG_OBJECT:
				args += argObjectGet( panel )
			elif type == constants.ARG_PLAYER:
				debug(DEBUG_WINDOWS, "Argument type (ARG_PLAYER) not implimented yet.")
			elif type == constants.ARG_RANGE:
				debug(DEBUG_WINDOWS, "Argument type (ARG_RANGE) not implimented yet.")
			elif type == constants.ARG_LIST:
				args += argListGet( panel )
			elif type == constants.ARG_STRING:
				args += argStringGet( panel )

		print args
		order = apply(objects.Order, args)
		print order

		debug(DEBUG_WINDOWS, "OrderSave: Inserting.")
		order = self.application.connection.insert_order(self.oid, slot, order)
		if failed(order):
			debug(DEBUG_WINDOWS, "OrderSave: Insert failed.")
			return
		
		debug(DEBUG_WINDOWS, "OrderSave: Getting.")
		order = self.application.connection.get_orders(self.oid, slot)[0]
		if failed(order):
			debug(DEBUG_WINDOWS, "OrderSave: Get failed.")
			return
		self.application.cache.orders[self.oid].insert(slot, order)

		debug(DEBUG_WINDOWS, "OrderSave: Removing.")
		r = self.application.connection.remove_orders(self.oid, slot+1)
		if failed(r):
			debug(DEBUG_WINDOWS, "OrderSave: Remove failed.")
			return
		del self.application.cache.orders[self.oid][slot+1]

		self.OnSelectObject(wx.local.SelectObjectEvent(self.oid))
		self.application.windows.Post(wx.local.SelectOrderEvent(self.oid, slot, True))

	def BuildPanel(self, order):
		"""\
		Builds a panel for the entering of orders arguments.
		"""
		# Remove the previous panel and stuff
		self.argument_panel.Hide()
		self.base_sizer.Remove(self.argument_panel)
		self.argument_panel.Destroy()

		# Create a new panel
		self.argument_panel = wx.Panel(self.base_panel, -1)
		self.argument_panel.SetAutoLayout( True )
		self.argument_sizer = wx.FlexGridSizer( 0, 2, 0, 0)
		
		self.argument_panel.SetSizer(self.argument_sizer)
		self.argument_sizer.AddGrowableCol( 1 )

		# Do we actually have an order
		if order:
			orderdesc = OrderDescs()[order.type]
			
			# List for the argument subpanels
			self.argument_subpanels = []
				
			for name, type in orderdesc.names:
				# Add there name..
				name_text = wx.StaticText( self.argument_panel, -1, name.title().replace("_","") )
				name_text.SetFont(wx.local.normalFont)

				self.argument_sizer.AddWindow( name_text, 0, wx.ALIGN_CENTER|wx.RIGHT, 4 )

				# Add the arguments bit
				if type == constants.ARG_ABS_COORD:
					subpanel = argCoordPanel( self, self.argument_panel, getattr(order, name) )
				elif type == constants.ARG_TIME:
					subpanel = argTimePanel( self, self.argument_panel, getattr(order, name) )
				elif type == constants.ARG_OBJECT:
					subpanel = argObjectPanel( self, self.argument_panel, getattr(order, name), self.application.cache )
				elif type == constants.ARG_LIST:
					subpanel = argListPanel( self, self.argument_panel, getattr(order, name) )
				elif type == constants.ARG_STRING:
					subpanel = argStringPanel( self, self.argument_panel, getattr(order, name) )
				else:
					subpanel = argNotImplimentedPanel( self, self.argument_panel, None )

				subpanel.SetToolTip(wx.ToolTip(getattr(orderdesc, name+'__doc__')))

				subpanel.SetFont(wx.local.normalFont)
				self.argument_subpanels.append( subpanel )
				
				self.argument_sizer.AddWindow( subpanel, 0, wx.GROW|wx.ALIGN_CENTER)
				self.argument_sizer.AddGrowableRow( len(self.argument_subpanels) - 1 )

			button_sizer = wx.FlexGridSizer( 1, 0, 0, 0 )

			save_button = wx.Button( self.argument_panel, -1, "Save", size=wx.local.buttonSize )
			save_button.SetFont(wx.local.normalFont)
			self.Bind(wx.EVT_BUTTON, self.OnOrderSave, save_button)
			revert_button = wx.Button( self.argument_panel, -1, "Revert", size=wx.local.buttonSize )
			revert_button.SetFont(wx.local.normalFont)
			self.Bind(wx.EVT_BUTTON, self.OnOrderSelect, revert_button)
			
			button_sizer.AddWindow( save_button, 0, wx.ALIGN_CENTRE|wx.ALL, 1 )
			button_sizer.AddWindow( revert_button, 0, wx.ALIGN_CENTRE|wx.ALL, 1 )
	
			self.argument_sizer.AddSizer( wx.BoxSizer( wx.HORIZONTAL ) )
			self.argument_sizer.AddSizer( button_sizer, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
			
		else:
			# Display message
			text = "No order selected."
			msg = wx.StaticText( self.argument_panel, -1, text, wx.DefaultPosition, wx.DefaultSize, 0)
			msg.SetFont(wx.local.normalFont)
			
			self.argument_sizer.AddWindow( msg, 0, wx.ALIGN_CENTER|wx.ALL, 5)
		
		self.argument_sizer.Fit(self.argument_panel)
		self.base_sizer.AddWindow( self.argument_panel, 0, wx.GROW|wx.ALIGN_CENTER|wx.ALL, 5 )
		self.base_sizer.Layout()

# The display for an ARG_COORD
X = 0
Y = 1
Z = 2

max = 2**31-1
min = -1*max

def argNotImplimentedPanel(parent, parent_panel, args):
	panel = wx.Panel(parent_panel, -1)
	item0 = wx.BoxSizer( wx.HORIZONTAL )

	panel.SetSizer(item0)
	panel.SetAutoLayout( True )
	
	item1 = wx.StaticText( panel, -1, "Not implimented.")
	item1.SetFont(wx.local.normalFont)
	item0.AddWindow( item1, 0, wx.ALIGN_CENTRE|wx.LEFT, 0 )

	return panel

def argStringPanel(parent, parent_panel, args):
	panel = wx.Panel(parent_panel, -1)
	item0 = wx.BoxSizer( wx.HORIZONTAL )

	panel.SetSizer(item0)
	panel.SetAutoLayout( True )
	
	item1 = wx.TextCtrl( panel, -1, args[1], size=(wx.local.spinSize[0]*2, wx.local.spinSize[1]))
	item1.SetFont(wx.local.tinyFont)
	item0.AddWindow( item1, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )
	
	return panel
	
def argStringGet(panel):
	windows = panel.GetChildren()
	return [0, windows[0].GetValue()]
	
def argObjectPanel(parent, parent_panel, args, cache):
	panel = wx.Panel(parent_panel, -1)
	item0 = wx.BoxSizer( wx.HORIZONTAL )

	panel.SetSizer(item0)
	panel.SetAutoLayout( True )

	if args == -1:
		args = "None selected..."
	else:
		args = str(args)

	item1 = wx.TextCtrl( panel, -1, args, size=(wx.local.spinSize[0]*2, wx.local.spinSize[1]))
	item1.SetFont(wx.local.tinyFont)
	item0.AddWindow( item1, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )
	
	return panel

def argObjectGet(panel):
	windows = panel.GetChildren()
	try:
		return [int(windows[0].GetValue())]
	except:
		return [-1]
	
def argListPanel(parent, parent_panel, args):
	panel = wx.Panel(parent_panel, -1)
	base = wx.BoxSizer(wx.VERTICAL)

	# Convert the first arg to a dictionary
	types = {}
	for type, name, max in args[0]:
		types[type] = (name, max)

	panel.SetSizer(base)
	panel.SetAutoLayout( True )
	
	selected = wx.ListCtrl( panel, -1, wx.DefaultPosition, wx.Size(130,80), wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER )
	selected.InsertColumn(0, "#")
	selected.SetColumnWidth(0, 25)
	selected.InsertColumn(1, "Type")
	selected.SetColumnWidth(1, 100)
	selected.SetFont(wx.local.tinyFont)

	# Fill in the selected box
	for slot in range(0, len(args[1])):
		type, number = args[1][slot]

		selected.InsertStringItem(slot, "")
		selected.SetStringItem(slot, 0, str(number))
		selected.SetStringItem(slot, 1, types[type][0])
		selected.SetItemPyData(slot, type)
		
	add = wx.Button( panel, -1, "Add", size=wx.local.buttonSize )
	add.SetFont(wx.local.normalFont)
	
	number = wx.SpinCtrl( panel, -1, "", min=0, max=100, size=wx.local.spinSize )
	number.SetFont(wx.local.tinyFont)

	type_list = wx.Choice( panel, -1, choices=[], size=wx.local.buttonSize)
	type_list.SetFont(wx.local.tinyFont)

	for type, item in types.items():
		type_list.Append(item[0], type)

	delete = wx.Button( panel, -1, "D", size=(wx.local.smallSize[0],wx.local.buttonSize[1]) )
	delete.SetFont(wx.local.normalFont)

	box_add = wx.BoxSizer(wx.HORIZONTAL)
	box_add.AddWindow( add, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )
	box_add.AddWindow( number, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )
	box_add.AddWindow( type_list, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )
	box_add.AddWindow( delete, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )

	base.AddSizer( selected, 1, wx.EXPAND|wx.ALIGN_CENTRE|wx.ALL, 1 )
	base.AddSizer( box_add, 0, wx.ALIGN_CENTRE|wx.ALL, 1 )

	base.Fit(panel)

	def addf(evt, selected=selected, number=number, type_list=type_list):
		"""\
		Add a new selection to the list.
		"""
		amount = number.GetValue()
	
		type = type_list.GetSelection()
		if type == wx.NOT_FOUND:
			debug(DEBUG_WINDOWS, "ListAdd: No type selected.")
			return
		type = type_list.GetClientData(type)

		slot = selected.FindItemByPyData(type)
		if slot == wx.NOT_FOUND:
			# Insert new object
			slot = 0

			selected.InsertStringItem(slot, "")
			selected.SetStringItem(slot, 0, str(amount))
			selected.SetStringItem(slot, 1, types[type][0])
			selected.SetItemPyData(slot, type)

		else:
			# Need to update the amount slot
			oldamount = int(selected.GetStringItem(slot, 0))
		
			max = types[type][1]
			if max != -1 and (amount + oldamount) > max:
				amount = max - oldamount

			if amount + oldamount < 0:
				amount = -1 * oldamount
			
			selected.SetStringItem(slot, 0, str(amount + oldamount))

	def deletef(evt, selected=selected):
		"""\
		Delete a selection from the list.
		"""
		slot = selected.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if slot == wx.NOT_FOUND:
			debug(DEBUG_WINDOWS, "ListDel: No selection selected.")
			return

		selected.DeleteItem(slot)

	def typef(evt, selected=selected, number=number, types=types, type_list=type_list, nocallback=False):
		"""\
		Update the max for the spinner.
		"""
		type = type_list.GetSelection()
		if type == wx.NOT_FOUND:
			debug(DEBUG_WINDOWS, "ListAdd: No type selected.")
			number.SetRange(0, 0)
		else:
			current = 0
		
			slot = selected.FindItemByPyData(type)
			if slot != wx.NOT_FOUND:
				if not nocallback:
					selected.SetItemState(slot, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
				current = int(selected.GetStringItem(slot, 0))*-1
		
			type = type_list.GetClientData(type)
			if types[type][1] == 4294967295:
				number.SetRange(current, 1000)
			else:
				number.SetRange(current, types[type][1])

	def selectf(evt, selected=selected, type_list=type_list, typef=typef):
		slot = selected.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if slot == wx.NOT_FOUND:
			debug(DEBUG_WINDOWS, "ListSelect: No selection selected.")
			return

		type = selected.GetItemPyData(slot)

		for slot in range(0, type_list.GetCount()):
			if type_list.GetClientData(slot) == type:
				type_list.SetSelection(slot)
				typef(None, nocallback=True)
				return
		
	parent.Bind(wx.EVT_LIST_ITEM_SELECTED, selectf, selected)
	parent.Bind(wx.EVT_BUTTON, addf, add)
	parent.Bind(wx.EVT_BUTTON, deletef, delete)
	parent.Bind(wx.EVT_CHOICE, typef, type_list)
	
	return panel

def argListGet(panel):
	selected = panel.GetChildren()[0]
	
	returns = [[], []]
	
	slot = -1
	while True:
		slot = selected.GetNextItem(slot, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE);
		if slot == wx.NOT_FOUND:
			break
		
		type = selected.GetItemPyData(slot)
		amount = int(selected.GetStringItem(slot, 0))
		
		returns[-1].append((type, amount))
	
	return returns

def argTimePanel(parent, parent_panel, args):
	panel = wx.Panel(parent_panel, -1)
	item0 = wx.BoxSizer( wx.HORIZONTAL )

	panel.SetSizer(item0)
	panel.SetAutoLayout( True )
	
	item1 = wx.SpinCtrl( panel, -1, str(args), min=min, max=max, size=(wx.local.spinSize[0]*2, wx.local.spinSize[1]) )
	item1.SetFont(wx.local.tinyFont)
	item0.AddWindow( item1, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )
	
	return panel
	
def argTimeGet(panel):
	windows = panel.GetChildren()
	return [windows[0].GetValue()]

def argCoordPanel(parent, parent_panel, args):

	panel = wx.Panel(parent_panel, -1)
	item0 = wx.BoxSizer( wx.HORIZONTAL )

	panel.SetSizer(item0)
	panel.SetAutoLayout( True )
	
	item1 = wx.StaticText( panel, -1, "X")
	item1.SetFont(wx.local.normalFont)
	item0.AddWindow( item1, 0, wx.ALIGN_CENTRE|wx.LEFT, 0 )

	item2 = wx.SpinCtrl( panel, -1, str(args[X]), min=min, max=max, size=wx.local.spinSize )
	item2.SetFont(wx.local.tinyFont)
	item0.AddWindow( item2, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )

	item3 = wx.StaticText( panel, -1, "Y")
	item3.SetFont(wx.local.normalFont)
	item0.AddWindow( item3, 0, wx.ALIGN_CENTRE|wx.LEFT, 3 )

	item4 = wx.SpinCtrl( panel, -1, str(args[Y]), min=min, max=max, size=wx.local.spinSize )
	item4.SetFont(wx.local.tinyFont)
	item0.AddWindow( item4, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )

	item5 = wx.StaticText( panel, -1, "Z")
	item5.SetFont(wx.local.normalFont)
	item0.AddWindow( item5, 0, wx.ALIGN_CENTRE|wx.LEFT, 3 )

	item6 = wx.SpinCtrl( panel, -1, str(args[Z]), min=min, max=max, size=wx.local.spinSize )
	item6.SetFont(wx.local.tinyFont)
	item0.AddWindow( item6, 0, wx.ALIGN_CENTRE|wx.LEFT, 1 )

	item7 = wx.Button( panel, -1, "P", size=wx.local.smallSize )
	item7.SetFont(wx.local.normalFont)
	item0.AddWindow( item7, 0, wx.ALIGN_CENTRE|wx.LEFT, 3 )

	return panel

def argCoordGet(panel):
	windows = panel.GetChildren()
	return [windows[1].GetValue(), windows[3].GetValue(), windows[5].GetValue()]
	
