#!/usr/bin/python


from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import images

from datamodels import *

class Image (webapp.RequestHandler):
	def get(self):
		try:
			user = db.get(self.request.get("img_id"))
		except:
			self.redirect('/error')
			return
			
		if user.avatar:
			self.response.headers['Content-Type'] = "image/png"
			self.response.out.write(user.avatar)
		else:
			self.response.out.write("No image")
		





def main():
	application = webapp.WSGIApplication([
		('/img', Image),
		], debug=False)
		
	run_wsgi_app(application)


if __name__ == '__main__':
	main()