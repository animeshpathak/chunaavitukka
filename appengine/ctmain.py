"""A webapp2 server for ChunaaviTukka."""

import os
import urllib
import json

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def user_setup(self):
    '''Function to do basic user URL setup'''
    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        nickname = users.get_current_user().nickname()
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        nickname = None
    return (url, url_linktext)

def get_predictions(user_id):
    return [{'cons':{'name':'Varanasi','slug':'varanasi-up'},'candidate':{'name':'M.M.Malaviya','party':'BHU','coalition': 'ABC'}},{'cons':{'name':'Amritsar','slug':'amritsar-pu'},'candidate':{'name':'Guru Gobind Singh','party':'Gurdwara','coalition': 'XYZ'}}]

def get_constituency_info(contest_slug):
    return [{'candidate':{'name':'M.M.Malaviya','party':'BHU','coalition': 'ABC'},'support':100},{'candidate':{'name':'Guru Gobind Singh','party':'Gurdwara','coalition': 'XYZ'},'support':75}]

	
class HomeHandler(webapp2.RequestHandler):

    def get(self):
        (url, url_linktext) = user_setup(self)
        template_values = {
            'greetings': [],
            'url': url,
            'url_linktext': url_linktext,
        }
        
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(template_values))
		
class ContestPageHandler(webapp2.RequestHandler):
    '''Handler for showing a contest's page'''
    def get(self, contest_slug):
        contest_name = contest_slug.capitalize()

        predictions = get_constituency_info(contest_slug)
        (url, url_linktext) = user_setup(self)
        format = self.request.get("f")
        template_values = {
            'contest_slug': contest_slug,
            'contest_name': contest_name,
            'url': url,
            'url_linktext': url_linktext,
            'predictions': predictions,
        }

        if (format == 'json'):
          self.response.headers['Content-Type'] = 'application/json'   
          json.dump(predictions,self.response.out)
        else:
          self.response.headers['Content-Type'] = 'text/html'
          template = JINJA_ENVIRONMENT.get_template('templates/contest.html')
          self.response.write(template.render(template_values))

class UserPageHandler(webapp2.RequestHandler):
    '''Handler for showing a user's page'''
    def get(self, user_id):
        predictions = get_predictions(user_id)
        (url, url_linktext) = user_setup(self)

        format = self.request.get("f")
        template_values = {
            'user_name': user_id,
            'url': url,
            'url_linktext': url_linktext,
            'predictions': predictions,
        }

        if (format == 'json'):
          self.response.headers['Content-Type'] = 'application/json'   
          json.dump(predictions,self.response.out)
        else:
          self.response.headers['Content-Type'] = 'text/html'
          template = JINJA_ENVIRONMENT.get_template('templates/user.html')
          self.response.write(template.render(template_values))

class UserPredictionHandler(webapp2.RequestHandler):
    '''Handler for recording user predictions'''
    def get(self, user_id, contest_slug):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Show contest detail!')

application = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=HomeHandler, name='home'),
    webapp2.Route(r'/c/<contest_slug>/', handler=ContestPageHandler, name='contest_page'),
    webapp2.Route(r'/u/<user_id>/', handler=UserPageHandler, name='user_page'),
    webapp2.Route(r'/u/<user_id>/<contest_slug>/', handler=UserPredictionHandler, name='user_prediction'),
], debug=True)

# URL mapping, for reference
# /c/contest_slug - a contest's public page
# returns: list of public predictions about the contest, including summaries
# /u/user-id - a user's public page
# returns: list of public predictions by that user
# /u/user-id/contest-slug - user u's prediction about contest c
# returns: JSON object with candidate id, name, and party
