#!/usr/bin/python

import os
import cgi

from google.appengine.ext import webapp
from google.appengine.ext import db

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api import mail as mailapi

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

	
class Visitor(db.Model):

        content = db.StringProperty(multiline=True)
        date = db.DateTimeProperty(auto_now_add=True)
        writer = db.StringProperty()


class MainPage(webapp.RequestHandler):
	
	def get(self):
		visitors = db.GqlQuery("SELECT * FROM Visitor ORDER BY date DESC")
		users_per_page = 10
	
		counter=visitors.count()
		if(not (counter % users_per_page )):
			pages = range(counter/users_per_page)
		else:
			pages = range(counter/users_per_page+1)

		page = self.request.get('page')
		try:
			page = int(page)
		except ValueError:
			page = 0
		offset = (page) * users_per_page
		if offset < 0: offset = 0

		nombre = ''
			
		visitors = visitors.fetch(users_per_page, offset)

		guestbook_values = {
			'nombre' : nombre,
			'visitors': visitors,
			'counter': counter,
			'pages': pages,
			}

        	self.response.out.write(template.render('../view/main.django', guestbook_values))



  
class Messaging(webapp.RequestHandler):
        
	
	def post(self):
                visitor = Visitor()
		
                if self.request.get('writer'):
                        writer = cgi.escape(self.request.get('writer'))
			if (len(writer)>15):
				error_writer_too_long = True
			else:
				error_writer_too_long = False
				visitor.writer = writer
     
                content = cgi.escape(self.request.get('content'))
		if (len(content)>450):
			error_content_too_long = True
		else:
			error_content_too_long = False
			visitor.content = content

		
		if (not (error_writer_too_long or error_content_too_long )):
			#Mail sending to admins: beginning
			content = "Hola! Te aviso que dejaron una idea en Galaktia. Fue "+writer +'\n'
			subject = "[galaktia] new idea"
			mailapi.send_mail("manuelaraoz@gmail.com","manuelaraoz@gmail.com",subject,content)
			#Mail sending to admins: ending
			
               		visitor.put()
                self.redirect('/')

class Error(webapp.RequestHandler):
			
	def get(self):
		self.response.out.write('404 Error: Not Found!')

def main():
	
	app = webapp.WSGIApplication(
				[
				('/', MainPage),
				('/sign' , Messaging),
		
				('/.*' , Error),
				
				],
				debug = True)
					
	run_wsgi_app(app)
					
if __name__ == "__main__":
	main()

