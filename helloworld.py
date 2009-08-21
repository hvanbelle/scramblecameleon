import cgi
import os
import md5
import string
import base64
import crypt
import random

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

def scramble_reverse(chars):
  '''reverse the imported chars'''
  ochars = ''
  beyond = len(chars)
  for ix in range(beyond):
    ochars += chars[beyond - 1 - ix]
  return ochars

def scramble_md5(chars):
  '''excecute a md5 conversion'''
  hash = md5.new()
  hash.update(chars)
  return base64.encodestring(repr(hash.digest()))

def getsalt(chars = string.letters + string.digits):
  '''generate a random 2-character 'salt' '''
  return random.choice(chars) + random.choice(chars)

def scramble_crypt(chars):
  '''excecute a crypt conversion'''
  return crypt.crypt(chars, getsalt())

def scramble_crypt_ab(chars):
  '''excecute a crypt conversion with fixed salt'''
  return crypt.crypt(chars, "ab") # same salt so same crypt for same string

def scramble_rot13(chars):
  '''excecute a rot13 conversion'''
  rot13_result = ""
  for x in range(len(chars)):
    byte = ord(chars[x])
    cap = (byte & 32)
    byte = (byte & (~cap))
    if (byte >= ord('A')) and (byte <= ord('Z')):
      byte = ((byte - ord('A') + 13) % 26 + ord('A'))
    byte = (byte | cap)
    rot13_result = rot13_result + chr(byte)
  return rot13_result

class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


class MainPage(webapp.RequestHandler):
  def get(self):
    greetings_query = Greeting.all().order('-date') # Order decending
    greetings = greetings_query.fetch(5) # Fetch only the last 5 entries

    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'greetings': greetings,
      'url': url,
      'url_linktext': url_linktext,
      }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))


class Guestbook(webapp.RequestHandler):
  def post(self):
    greeting = Greeting()

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/')

class Guestbook2(webapp.RequestHandler):
  def post(self):
    greeting = Greeting()

    if users.get_current_user():
      greeting.author = users.get_current_user()

    scrambled_content = scramble_rot13(self.request.get('content2'))  

    greeting.content = scrambled_content
    greeting.put()
    self.redirect('/')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', Guestbook),
                                      ('/sign2', Guestbook2)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
