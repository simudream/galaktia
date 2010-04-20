#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import cgi
import urllib


from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import mail as mailapi
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson



class Visitor(db.Model):
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    writer = db.StringProperty()


class MainPage(webapp.RequestHandler):

    def get(self):
        self.response.out.write(template.render('../view/main.django', {}))

class Trailer(webapp.RequestHandler):

    def get(self):
        self.response.out.write(template.render('../view/trailer.django', {}))

class Commit(webapp.RequestHandler):

    def get(self):
        self.post()
    def post(self):

        payload = simplejson.loads(self.request.body)
        for revision in payload["revisions"]:
            status = u"Commit de la revision %s de galaktia. Autor: %s en %s" % \
                    (revision["revision"],
                    revision["author"],
                    revision["url"])


        url = "http://twitter.com/status/update"

        form_fields = {
            "authenticity_token": "7b398163c060a32179ddd2e6630e96d961b633ef",
            "status": status,
            "twttr": "true",
            "return_rendered_status": "false"
        }
        headers = {
            "User-Agent":  "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009033100 Ubuntu/9.04 (jaunty) Firefox/3.0.8",
            "Keep-Alive": "300",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie" : "__utma=43838368.11236536384235740.1238534453.1250098114.1250175356.181; __utmz=43838368.1250092236.179.69.utmcsr=follow|utmccn=twitter20080331162631|utmcmd=email; __utmv=43838368.lang%3A%20en; auth_token=1250175383--cd6332f4e84ee499e68ca5295ec0ebc65b536612; _twitter_sess=BAh7CzoOcmV0dXJuX3RvMDoJdXNlcmkEIWfoAjoTcGFzc3dvcmRfdG9rZW4i%250ALWRlYjUzNjM0NWMyN2JiZTA1NDVmM2M0MTg0Yzc2YTZhNGIyZjc1YjY6DGNz%250AcmZfaWQiJTQ0YTY5OTYxNjFiZmY2ZGQ4NTY4ZmEwY2RhMjg5NmE2OgdpZCIl%250AYzYxZGFkM2U5YjI3NTFhMmE2ZjU4NjczMWQ2NDM0ZWEiCmZsYXNoSUM6J0Fj%250AdGlvbkNvbnRyb2xsZXI6OkZsYXNoOjpGbGFzaEhhc2h7AAY6CkB1c2VkewA%253D--e994c601eddd227bddd95d498c878f12ed38f26e; lang=en; __utmb=43838368.8.9.1250175431210; __utmc=43838368"
            }
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url=url,
                    payload=form_data,
                    method=urlfetch.POST,
                    headers=headers)
        self.response.out.write("Twitter update succesful<br>")
        self.response.out.write("Result:<br><br>")
        self.response.out.write(result)



class Error(webapp.RequestHandler):
    def get(self):
        self.response.out.write('404 Error: Not Found!')

def main():
    app = webapp.WSGIApplication(
                [
                ('/', MainPage),
                ('/trailer', Trailer),
                ('/commit/.*', Commit),
                ('/.*' , Error),
                ],
                debug = True)
    run_wsgi_app(app)

if __name__ == "__main__":
    main()

