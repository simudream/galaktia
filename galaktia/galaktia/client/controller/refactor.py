# -*- coding: utf-8 -*-
import wx
import os
import pyglet
from pyglet.window import key

class LoginPanel(wx.Panel):
    def __init__(self,parent,colour):
        wx.Panel.__init__(self,parent)
        self.parent = parent
        
        panel = wx.Panel(self)
        panel1 = wx.Panel(self)
        
        panel.SetBackgroundColour(colour)
        panel1.SetBackgroundColour(colour)
        
        self.welcomeText = wx.StaticText(panel, -1, 'Bienvenido a Galaktia!')
        self.welcomeText.SetFont(wx.Font(24, wx.SCRIPT, wx.NORMAL, wx.BOLD))
        self.welcomeText.SetForegroundColour(wx.GREEN)
        self.welcomeText.SetSize(self.welcomeText.GetBestSize())
        
        self.usernameInput = wx.TextCtrl(panel1, -1, size=(200,30))
        self.passwordInput = wx.TextCtrl(panel1, -1, size=(200,30), style=wx.TE_PASSWORD)
        
        self.usernameLabel = wx.StaticText(panel1, -1, 'Username')
        self.usernameLabel.SetForegroundColour(wx.WHITE)
        
        self.passwordLabel = wx.StaticText(panel1, -1, 'Password')
        self.passwordLabel.SetForegroundColour(wx.WHITE)
        
        self.ingresarBtn = wx.Button(panel1, -1, "Ingresar")
        self.quitBtn = wx.Button(panel1, -1,  "Salir")
        
        self.Bind(wx.EVT_BUTTON, self.OnIngresar, self.ingresarBtn)
        self.Bind(wx.EVT_BUTTON, self.OnQuit, self.quitBtn)
        
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        dataBox = wx.GridSizer(3,2,0,0)
         
        dataBox.AddMany([ (self.usernameLabel,0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_HORIZONTAL),(self.usernameInput, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_HORIZONTAL),(self.passwordLabel,0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_HORIZONTAL),(self.passwordInput,0,wx.ALIGN_RIGHT | wx.ALIGN_CENTER_HORIZONTAL),(self.ingresarBtn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_HORIZONTAL),(self.quitBtn, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_HORIZONTAL)])
        
        panel1.SetSizer(dataBox)
        
        textBox = wx.BoxSizer(wx.VERTICAL)
        textBox.Add(self.welcomeText, 0, wx.EXPAND | wx.ALL, 50)
        
        panel.SetSizer(textBox)
        
        vbox1.Add(panel, 1, wx.EXPAND | wx.ALL, 3)
        vbox1.Add(panel1, 1, wx.EXPAND | wx.ALL, 3)
        
        self.SetSizer(vbox1)

    def OnQuit(self, evt):
        self.parent.Close()
        
    def OnIngresar(self, evt):
        if not self.usernameInput.GetValue() or not self.passwordInput.GetValue():
            self.parent.SetStatusText('Ingrese un nombre y password válidos')
            return	
        self.parent.SetStatusText('Logueando')
        username = self.usernameInput.GetValue()
        password = self.passwordInput.GetValue()
        self.parent.SetStatusText('Logueado como: '+ username + ". Su password es: " + password)
        return    
	
class NudeFrame(wx.Frame):
    def __init__(self, parent, title, colour):
        wx.Frame.__init__(self, parent, -1, title, pos=(200, 200), size=(500, 500))
        self.SetBackgroundColour(colour)
        IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'assets', 'images')
        icon = wx.Icon(os.path.join(IMAGES_DIR, 'logo2.jpg'), wx.BITMAP_TYPE_ANY)
        self.SetIcon(icon)
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit the program")
        self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)    
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)
        self.CreateStatusBar()
        panel = LoginPanel(self,colour)
        box = wx.BoxSizer(wx.VERTICAL)
        panel.SetBackgroundColour(colour)
        box.Add(panel, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(box)
        
    def OnQuit(self, evt):
        self.Close()
	    

class wxPyApp(wx.App):
    def OnInit(self):
        frame = NudeFrame(None, "Galaktia Client v0.1", wx.BLACK)
        self.SetTopWindow(frame)
        frame.Show(True)
        return True

app = wxPyApp(redirect=True)
app.MainLoop()