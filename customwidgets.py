#Some basic custom tkinter widgets


#Imports are in this manner for convenience's sake
import platform, os
import tkinter as tk
from tkinter.constants import *
from .style import *
#Basic Widgets

#Frame to use instead of default tk.frame, by default themed with light_color
class ThemedFrame(tk.Frame):
	def __init__(self, parent,
		background = w,
		frame_borderwidth = 0,
		frame_highlightthickness = 0,
		frame_highlightcolor=w
		):

		tk.Frame.__init__(self,parent, background = background, highlightcolor = frame_highlightcolor, highlightthickness=frame_highlightthickness, highlightbackground=light_color, borderwidth = frame_borderwidth)


#themed author/ etc label
class ThemedLabel(tk.Label):
	def __init__(self,frame,label_text="",label_font=smalltext,text_variable=None,background = light_color,foreground=lg,anchor="w",wraplength = None):
		tk.Label.__init__(self,frame,
			background = background,
			highlightthickness=0,
			anchor=anchor,
			text = label_text,
			font=label_font,
			foreground= foreground,
			textvariable = text_variable,
			)
		if not wraplength == None:
			self.configure(wraplength=wraplength)
	def set(self,text):
		self.configure(text=text)

#themed author/ etc label
class ThemedListbox(tk.Listbox):
	def __init__(self,frame, foreground = lg, highlightthickness = 0, background = light_color):
		tk.Listbox.__init__(self,frame,
			background = background,
			selectbackground = dark_color,
			borderwidth = 0,
			highlightthickness=highlightthickness,
			foreground= foreground,
			font = largeboldtext,
			activestyle=None
		)

#Custom button
#A tkinter label with a bound on-click event to fix some issues 
#that were happening with normal tkinter buttons on MacOS.
#Unfortunately MacOS was causing a weird white translucent
#effect to be applied to all classes that used the tk.Button Widget.
#This fixes it but making our own "button" by binding a callback to 
#an on_click event. Feel free to use this in other projects where mac
#compatibility is an issue, also special thanks to Kabiigon for testing
#this widget until I got it right since I don't have a mac
class button(tk.Label):
	def __init__(self,frame,callback=None,image_object= None,text_string=None,background=dark_color, font=smallboldtext):
		self.callback = callback

		tk.Label.__init__(self,frame,
			background=background,
			foreground= w,
			borderwidth= 0,
			activebackground=light_color,
			image=image_object,
			text = text_string,
			font = font,
			anchor="center"
			)
		self.bind('<Button-1>', self.on_click)

	#Use callback when our makeshift "button" clicked
	def on_click(self, event=None):
		if self.callback:
			self.callback()

	#Function to set the button's image
	def setimage(self,image):
		self.configure(image=image)

	#Function to set the button's text
	def settext(self,text):
		self.configure(text=text)

#Tooltip
class ToolTipBase:
	def __init__(self, button):
		self.button = button
		self.tipwindow = None
		self.id = None
		self.x = self.y = 0
		self._id1 = self.button.bind("<Enter>", self.enter)
		self._id2 = self.button.bind("<Leave>", self.leave)
		self._id3 = self.button.bind("<ButtonPress>", self.leave)
		self._id4 = self.button.bind("<Key>", self.leave)

	def enter(self, event=None):
		self.schedule()

	def leave(self, event=None):
		self.unschedule()
		self.hidetip()

	def schedule(self):
		self.unschedule()
		self.id = self.button.after(10, self.showtip)

	def unschedule(self):
		id = self.id
		self.id = None
		if id:
			self.button.after_cancel(id)

	def showtip(self):
		if self.tipwindow:
			return
		# The tip window must be completely outside the button;
		# otherwise when the mouse enters the tip window we get
		# a leave event and it disappears, and then we get an enter
		# event and it reappears, ad naseum.
		x = self.button.winfo_rootx() + 100
		y = self.button.winfo_rooty() + 100
		self.tipwindow = tw = tk.Toplevel(self.button)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))
		self.showcontents()
		self.button.after(20000, self.leave)

	def showcontents(self, text=""):
		label = tk.Label(self.tipwindow, text=text, justify=LEFT,
					  background=dark_color, 
					  relief=SOLID, 
					  borderwidth=2,
					  foreground=lg,
					  font=mediumboldtext
					  )
		label.pack()

	def hidetip(self):
		tw = self.tipwindow
		self.tipwindow = None
		if tw:
			tw.destroy()

class tooltip(ToolTipBase):
	def __init__(self, button, text):
		ToolTipBase.__init__(self, button)
		self.text = text

	def showcontents(self):
		try:
		  ToolTipBase.showcontents(self, self.text)
		except:
			print("Failed to set tooltip {}".format(self.text))





#Widgets with scroll bars that appear when needed and supporting code
#Automatic scrollbars on certain text boxes
class AutoScroll(object):
	def __init__(self, master):
		try:
			vsb = tk.Scrollbar(master, orient='vertical', command=self.yview)
		except:
			pass
		hsb = tk.Scrollbar(master, orient='horizontal', command=self.xview)

		try:
			self.configure(yscrollcommand=self._autoscroll(vsb))
		except:
			pass
		self.configure(xscrollcommand=self._autoscroll(hsb))

		self.grid(column=0, row=0, sticky='nsew')
		try:
			vsb.grid(column=1, row=0, sticky='ns')
		except:
			pass
		hsb.grid(column=0, row=1, sticky='ew')

		master.grid_columnconfigure(0, weight=1)
		master.grid_rowconfigure(0, weight=1)

		methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
			| tk.Place.__dict__.keys()

		for meth in methods:
			if meth[0] != '_' and meth not in ('config', 'configure'):
				setattr(self, meth, getattr(master, meth))

	@staticmethod
	def _autoscroll(sbar):
		'''Hide and show scrollbar as needed.'''
		def wrapped(first, last):
			first, last = float(first), float(last)
			if first <= 0 and last >= 1:
				sbar.grid_remove()
			else:
				sbar.grid()
			sbar.set(first, last)
		return wrapped

	def __str__(self):
		return str(self.master)

def _create_container(func):
	'''Creates a tk Frame with a given master, and use this new frame to
	place the scrollbars and the widget.'''
	def wrapped(cls, master, **kw):
		container = tk.Frame(master)
		container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
		container.bind('<Leave>', lambda e: _unbound_to_mousewheel(e, container))
		return func(cls, container, **kw)
	return wrapped

class scrolledText(AutoScroll, tk.Text):
	'''A standard Tkinter Text widget with scrollbars that will
	automatically show/hide as needed.'''
	@_create_container
	def __init__(self, master, **kw):
		tk.Text.__init__(self, master, **kw)
		AutoScroll.__init__(self, master)

class ScrolledThemedListBox(AutoScroll, ThemedListbox):
	@_create_container
	def __init__(self, master, **kw):
		ThemedListbox.__init__(self, master, **kw,)
		AutoScroll.__init__(self, master)

def _bound_to_mousewheel(event, widget):
	child = widget.winfo_children()[0]
	if platform.system() == 'Windows' or platform.system() == 'Darwin':
		child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
		child.bind_all('<Shift-MouseWheel>', lambda e: _on_shiftmouse(e, child))
	else:
		child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
		child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
		child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
		child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))

def _unbound_to_mousewheel(event, widget):
	if platform.system() == 'Windows' or platform.system() == 'Darwin':
		widget.unbind_all('<MouseWheel>')
		widget.unbind_all('<Shift-MouseWheel>')
	else:
		widget.unbind_all('<Button-4>')
		widget.unbind_all('<Button-5>')
		widget.unbind_all('<Shift-Button-4>')
		widget.unbind_all('<Shift-Button-5>')

def _on_mousewheel(event, widget):
	if platform.system() == 'Windows':
		widget.yview_scroll(-1*int(event.delta/120),'units')
	elif platform.system() == 'Darwin':
		widget.yview_scroll(-1*int(event.delta),'units')
	else:
		if event.num == 4:
			widget.yview_scroll(-1, 'units')
		elif event.num == 5:
			widget.yview_scroll(1, 'units')

def _on_shiftmouse(event, widget):
	if platform.system() == 'Windows':
		widget.xview_scroll(-1*int(event.delta/120), 'units')
	elif platform.system() == 'Darwin':
		widget.xview_scroll(-1*int(event.delta), 'units')
	else:
		if event.num == 4:
			widget.xview_scroll(-1, 'units')
		elif event.num == 5:
			widget.xview_scroll(1, 'units')