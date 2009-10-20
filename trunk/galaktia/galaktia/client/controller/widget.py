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

    def delete_text(self,start,end):
        self.field.passwd = self.field.passwd[:start] + self.field.passwd[end:]
        super(PasswordDocument,self).delete_text(start,end)


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

class ChatWidget(object):

    chat_width = 40

    def __init__(self):
        self.messages = []

    def show_message(self, message):
        self.shift_messages()
        is_first = True
        while len(message) > self.chat_width:
            next_line = message[:self.chat_width]
            if is_first:
                self.formatted_line(next_line)
                is_first = False
            else:
                self.append_line(next_line)
            self.shift_messages()
            message = message[self.chat_width:]
        if is_first:
            self.formatted_line(message)
        else:
            self.append_line(message)


    def shift_messages(self):
        for label in self.messages:
            label.y += 16
    def append_line(self, line):
        self.messages.append(pyglet.text.Label(u''+line,
                font_name='Courier New', font_size=8, bold=False,
                x=20, y=60,
                anchor_x='left', anchor_y='center'))
        if len(self.messages) > 20:
            self.messages = self.messages[1:21]

    def formatted_line(self, line):
        splitted = line.split(":")
        if len(splitted) == 1:
            splitted.append("")
        uname = splitted[0]
        message = splitted[1:]

        self.messages.append(pyglet.text.Label(u''+line,
                font_name='Courier New', font_size=8, bold=False,
                x=20, y=60,
                anchor_x='left', anchor_y='center'))
        if len(self.messages) > 20:
            self.messages = self.messages[1:21]
    def draw(self):
        for message in self.messages:
            message.draw()
