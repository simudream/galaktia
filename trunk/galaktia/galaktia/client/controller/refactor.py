#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os
import pyglet
from pyglet.window import key


class GalaktiaViewport(pyglet.graphics.Batch):

    IMAGES_DIR = os.path.join(os.path.dirname( \
            os.path.abspath(__file__)), os.pardir, 'assets', 'images')

    def __init__(self):
        super(GalaktiaViewport, self).__init__()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        image = pyglet.image.load(os.path.join(self.IMAGES_DIR, 'walter.gif'))
        self.sprites = [
            pyglet.sprite.Sprite(image, batch=self, group=self.foreground)
        ]
        walter = self.sprites[0] # TODO: quick'n'dirty
        walter.x, walter.y = 380, 180

class PygletPanel(pyglet.window.Window,wx.Panel):

    def __init__(self):
        super(PygletPanel, self).__init__(caption='Galaktia')
        self.label = pyglet.text.Label(u'¡Bienvenido a Galaktia!',
                font_name='Arial', font_size=36, bold=True,
                x=self.width//2, y=self.height//2,
                anchor_x='center', anchor_y='center')
        self.keystate = key.KeyStateHandler()
        self.push_handlers(self.keystate)
        self.viewport = GalaktiaViewport()

    def on_draw(self):
        self.clear()
        self.draw_gl_rumble()
        self.label.draw()
        self.viewport.draw()

    def draw_gl_rumble(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2i', (300, 300, 500, 200, 300, 100, 100, 200)),
                ('c3B', (0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 0))
        )

    def on_key_press(self, symbol, modifiers):
        print 'A key was pressed: %s %s' % (symbol, modifiers)
        if symbol == pyglet.window.key.ESCAPE:
            self.dispatch_event('on_close')

    def on_text_motion(self, motion):
        STEP = 20
        motion_codes = [0, -1, 1, 0] # none, lower, upper, both
        decode = lambda lower, upper: motion_codes[self.keystate[lower] \
                | (self.keystate[upper] << 1)] * STEP
        dx, dy = (decode(key.LEFT, key.RIGHT), decode(key.DOWN, key.UP))
        if dx or dy:
            walter = self.viewport.sprites[0] # TODO: quick'n'dirty
            walter.x += dx
            walter.y += dy
            self.dispatch_event('on_draw')


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
        self.parent.username = self.usernameInput.GetValue()
        self.parent.password = self.passwordInput.GetValue()
        self.parent.SetStatusText('Logueado como: '+ self.parent.username + ". Su password es: " + self.parent.password)
        self.parent.logged()
        return    
	
class NudeFrame(wx.Frame):
    def __init__(self, parent, title, colour):
        wx.Frame.__init__(self, parent, -1, title, pos=(200, 200), size=(800, 800))
        self.username = None
        self.password = None
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
        self.panel = LoginPanel(self,colour)
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetBackgroundColour(colour)
        self.box.Add(self.panel, wx.EXPAND | wx.ALL, 3)
        self.Layout()
        self.SetSizer(self.box)
        
    def logged(self):
        self.SetBackgroundColour(wx.RED)
        self.panel.Destroy() 
        self.panel = PygletPanel()
        self.panel.SetBackgroundColour(wx.RED)
        self.panel.Fit()
        self.box.Add(self.panel, wx.EXPAND | wx.ALL, 3)
        self.Layout()
        
        
                
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