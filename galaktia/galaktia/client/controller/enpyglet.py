# -*- coding: utf-8 -*-
import os
import pyglet
from pyglet.window import key
from pyglet.gl import *

class Rectangle(object):
    '''Draws a rectangle into a batch.'''
    def __init__(self, x1, y1, x2, y2, batch):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
            ('c4B', [200, 200, 220, 255] * 4)
        )

class TextWidget(object):
    def __init__(self, text, x, y, width, batch):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), 
            dict(color=(0, 0, 0, 255))
        )
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.rectangle = Rectangle(x - pad, y - pad, 
                                   x + width + pad, y + height + pad, batch)

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)


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

class GalaktiaClientWindow(pyglet.window.Window):

    def __init__(self):
        super(GalaktiaClientWindow, self).__init__(caption='Galaktia')
        self.welcomeLabel = pyglet.text.Label(u'¡Bienvenido a Galaktia!',
                font_name='Arial', font_size=36, bold=True,
                x=self.width//2, y=self.height//2,
                anchor_x='center', anchor_y='center')
        self.usernameLabel = pyglet.text.Label(u'Username',
                font_name='Arial', font_size=12, bold=True,
                x=self.width//4, y=self.height//4,
                anchor_x='center', anchor_y='center')
        self.passwordLabel = pyglet.text.Label(u'Password',
                font_name='Arial', font_size=12, bold=True,
                x=self.width//4, y=self.height//5,
                anchor_x='center', anchor_y='center')
        self.viewport = GalaktiaViewport()
        self.keystate = key.KeyStateHandler()
        self.push_handlers(self.keystate)
        self.widgets = [
            TextWidget('', self.width//4 + 50, self.height//4 - 10, self.width//2, self.viewport),
            TextWidget('', self.width//4 + 50, self.height//5 - 10, self.width//2, self.viewport),
        ]
        self.text_cursor = self.get_system_mouse_cursor('text') 
        self.focus = None
        self.set_focus(self.widgets[0])
    
    def on_mouse_motion(self, x, y, dx, dy):
        for widget in self.widgets:
            if widget.hit_test(x, y):
                self.set_mouse_cursor(self.text_cursor)
                break
        else:
            self.set_mouse_cursor(None)

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.widgets:
            if widget.hit_test(x, y):
                self.set_focus(widget)
                break
        else:
            self.set_focus(None)

        if self.focus:
            self.focus.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)
      
    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)
        
    def set_focus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)
        

    def on_ingresar(self):
        self.clear()
        self.keystate = key.KeyStateHandler()
        self.push_handlers(self.keystate)
        self.viewport = GalaktiaViewport()
        self.draw_gl_rumble()
        self.viewport.draw()

    def on_draw(self):
        self.clear()
        self.draw_gl_rumble()
        self.viewport.draw()
        self.welcomeLabel.draw()
        self.usernameLabel.draw()
        self.passwordLabel.draw()


    def draw_gl_rumble(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2i', (300, 300, 500, 200, 300, 100, 100, 200)),
                ('c3B', (0, 0, 255, 255, 0, 0, 255, 255, 0, 0, 255, 0))
        )

    def on_key_press(self, symbol, modifiers):
        print 'A key was pressed: %s %s' % (symbol, modifiers)
        if symbol == pyglet.window.key.ESCAPE:
            self.dispatch_event('on_close')
        elif symbol == pyglet.window.key.ENTER:
            self.dispatch_event('on_ingresar')
        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                dir = -1
            else:
                dir = 1
            if self.focus in self.widgets:
                i = self.widgets.index(self.focus)
            else:
                i = 0
                dir = 0
            self.set_focus(self.widgets[(i + dir) % len(self.widgets)])
        

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
        
    def on_resize(self,width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)


if __name__ == '__main__':
    window = GalaktiaClientWindow()
    window.push_handlers(pyglet.window.event.WindowEventLogger())
    pyglet.app.run()
