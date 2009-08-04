#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyglet



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
    def text(self):
        return self.document.text
    def empty(self):
        self.document.text = ""

class myCaret(pyglet.text.caret.Caret):
    def __init__(self, layout):
        super(myCaret,self).__init__(layout)
        
    def on_text(self,text):
        super(myCaret,self).on_text('*'*len(text))
        self._layout.document.insert_password_text(self._position,text)

        

class PasswordDocument(pyglet.text.document.UnformattedDocument):
    def __init__(self, text, field):
        self.field = field
        super(PasswordDocument,self).__init__(text)

    def insert_password_text(self,start,text):
        self.field.passwd = self.field.passwd[:start] + text + self.field.passwd[start:]
        print 'add:'+self.field.passwd
        
    def delete_text(self,start,end):
        self.field.passwd = self.field.passwd[:start] + self.field.passwd[end:]
        super(PasswordDocument,self).delete_text(start,end)
        print 'delete:'+self.field.passwd
        
        
        
    
class PasswordField(TextWidget):
    def __init__(self, text, x, y, width, batch):
        super(PasswordField,self).__init__(text,x,y,width,batch)
        self.document = PasswordDocument(text,self)
        self.document.set_style(0, len(self.document.text), 
            dict(color=(0, 0, 0, 255))
        )
        font = self.document.get_font()
        height = font.ascent - font.descent
        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.layout.x = x
        self.layout.y = y
        self.passwd = text
        self.caret = myCaret(self.layout)

    def text(self):
        return self.passwd