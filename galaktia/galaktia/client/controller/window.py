# -*- coding: utf-8 -*-
import wx
class Frame1(wx.Frame):
    #
    # create a simple windows frame (sometimes called form)
    #
    # pos=(ulcX,ulcY) size=(width,height) in pixels
    #
    #
    def __init__(self, parent, title):
    #
	wx.Frame.__init__(self, parent, -1, title, pos=(200, 200), size=(500, 500))
    #
    #
    # create a menubar at the top of the user frame
    #
	menuBar = wx.MenuBar()
    #
    #
    # create a menu ...
    #
	menu = wx.Menu()
    #
    #
    # ... add an item to the menu
    #
    # \tAlt-X creates an accelerator for Exit (Alt + x keys)
    #
    # the third parameter is an optional hint that shows up in
    #
    # the statusbar when the cursor moves across this menu item
    #
	menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit the program")
    #
    #
    # bind the menu event to an event handler, share QuitBtn event
    #
	self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
    #
    #
    # put the menu on the menubar
    #
	menuBar.Append(menu, "&File")
    #
	self.SetMenuBar(menuBar)
    #
    #
    # create a status bar at the bottom of the frame
    #
	self.CreateStatusBar()
    #
    #
    #
    # now create a panel (between menubar and statusbar) ...
    #
	panel = wx.Panel(self)
	panel1 = wx.Panel(self)

    #
	panel2 = wx.Panel(self)

    #
    # ... put some controls on the panel
    #
	self.welcomeText = wx.StaticText(panel, -1, 'Bienvenido a Galaktia!')
	self.welcomeText.SetFont(wx.Font(24, wx.SCRIPT, wx.NORMAL, wx.BOLD))
	self.welcomeText.SetBackgroundColour("blue")
	self.welcomeText.SetForegroundColour("red")
	self.welcomeText.SetSize(self.welcomeText.GetBestSize())
	self.usernameInput = wx.TextCtrl(panel1, -1, size=(200,30))
	self.passwordInput = wx.TextCtrl(panel1, -1, size=(200,30), style=wx.TE_PASSWORD)
	#
	ingresarBtn = wx.Button(panel2, -1, "Ingresar")
	quitBtn = wx.Button(panel2, -1,  "Salir")
	#
	# bind the button events to event handlers
	#
	self.Bind(wx.EVT_BUTTON, self.OnIngresar, ingresarBtn)
	self.Bind(wx.EVT_BUTTON, self.OnQuit, quitBtn)
	#
	#
	# use a sizer to layout the controls, stacked vertically
	#
	# with a 10 pixel border around each
	#
	vbox1 = wx.BoxSizer(wx.VERTICAL)
	dataBox = wx.GridSizer(2,2,0,0)
	dataBox.AddMany([ (wx.StaticText(panel1, -1, 'Username'),0, wx.ALIGN_CENTER),(self.usernameInput, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL),(wx.StaticText(panel1, -1, 'Password'),0, wx.ALIGN_CENTER_HORIZONTAL),(self.passwordInput,0)])
	#
	panel1.SetSizer(dataBox)
	buttonBox = wx.BoxSizer(wx.VERTICAL)
	buttonBox.Add(ingresarBtn, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 20)
	buttonBox.Add(quitBtn,0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 20)
	panel2.SetSizer(buttonBox)
	textBox = wx.BoxSizer(wx.VERTICAL)
	textBox.Add(self.welcomeText, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 20)
	panel.SetSizer(textBox)
	#
	#
	#
	vbox1.Add(panel, 1, wx.EXPAND | wx.ALL, 3)
	vbox1.Add(panel1, 1, wx.EXPAND | wx.ALL, 3)
        vbox1.Add(panel2, 1, wx.EXPAND | wx.ALL, 3)
	self.SetSizer(vbox1)
    #
    def OnQuit(self, evt):
	self.Close()
    def OnIngresar(self, evt):
	if not self.usernameInput.GetValue() or not self.passwordInput.GetValue():
	    self.SetStatusText('Ingrese un nombre y password válidos')
	    return	
	self.SetStatusText('Logueando')
	username = self.usernameInput.GetValue()
	password = self.passwordInput.GetValue()
	self.SetStatusText('Logueado como: '+ username + ". Su password es: " + password)
	return
#
class wxPyApp(wx.App):
#
    def OnInit(self):
#
# set the title too
#
	frame = Frame1(None, "Galaktia Client v0.1")
#
	self.SetTopWindow(frame)
#
	frame.Show(True)
#
	return True
#
#
# get it going ...
#
app = wxPyApp(redirect=True)
#
app.MainLoop()