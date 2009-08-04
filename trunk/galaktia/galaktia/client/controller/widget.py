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

class PasswordDocument(pyglet.text.document.UnformattedDocument):
    def __init__(self, text, field):
        self.field = field
        super(PasswordDocument,self).__init__(text)

    def insert_text(self,start,text):
        print 'a'
        self.field.passwd = self.field.passwd[:start] + text + self.field.passwd[start:]
        self.text = '*'*len(self.text)
        super(PasswordDocument,self).insert_text(start,'*'*len(text))

    def delete_text(self,start,end):
        self.field.passwd = self.field.passwd[:start] + self.field.password[end:]
        self.text = '*'*len(self.text)
        super(PasswordDocument,self).delete_text(start,end)
    
class PasswordField(TextWidget):
    def __init__(self, text, x, y, width, batch):
        super(PasswordField,self).__init__(text,x,y,width,batch)
        self.passwd = text
        self.document = PasswordDocument(text,self)

    def text(self):
        return self.passwd