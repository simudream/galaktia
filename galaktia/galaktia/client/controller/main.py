import pyglet
from pyglet.gl import *

class HelloWorldWindow(pyglet.window.Window):

    def __init__(self):
        super(HelloWorldWindow, self).__init__(caption='Galaktia')
        self.label = pyglet.text.Label('Bienvenido a Galaktia!',
                font_name='Arial',
                font_size=36,
                x=self.width//2, y=self.height//2,
                anchor_x='center', anchor_y='center')

    def on_draw(self):
        self.clear()
        #self.draw_test_gl_triangle()
        self.label.draw()

    def draw_test_gl_triangle(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glBegin(GL_TRIANGLES)
        glVertex2f(0, 0)
        glVertex2f(window.width, 0)
        glVertex2f(window.width, window.height)
        glEnd()

    def on_key_press(symbol, modifiers):
        print 'A key was pressed: %s %s' % (symbol, modifiers)

if __name__ == '__main__':
    window = HelloWorldWindow()
    window.push_handlers(pyglet.window.event.WindowEventLogger())
    pyglet.app.run()

