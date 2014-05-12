"""A webapp2 server for ChunaaviTukka."""

import os
import urllib
import json
import logging
import re

from google.appengine.api import users
from google.appengine.ext import ndb

from models import CTUser 
from models import CTCandidate 
from models import CTConstituency
from models import CTTukka 

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def user_setup(self):
    '''Function to do basic user URL setup'''
    google_user = users.get_current_user()
    if google_user:
        ct_user = CTUser.get_or_insert(google_user)
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout ' + ct_user.display_name
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        ct_user = None
    return (ct_user, url, url_linktext)

def get_predictions(user_id):
    return [{'cons':{'name':'Varanasi','slug':'varanasi-up'},'candidate':{'id':'1234','name':'M.M.Malaviya','party':'BHU','coalition': 'ABC'}},{'cons':{'name':'Amritsar','slug':'amritsar-pu'},'candidate':{'id':'5678','name':'Guru Gobind Singh','party':'Gurdwara','coalition': 'XYZ'}}]

def get_constituency_info(contest_slug):
    if contest_slug != 'varanasi' and contest_slug != 'lucknow':
        return {'name':'Some city', 'state': 'some state', 'predictions':[{'candidate':{'id':'1234','name':'M.M.Malaviya','party':'BHU','coalition': 'ABC'},'support':100},{'candidate':{'id':'5678','name':'Guru Gobind Singh','party':'Gurdwara','coalition': 'XYZ'},'support':75}]}
    else:
        conskey = ndb.Key(CTConstituency, contest_slug)
#        logging.error(conskey)
        #TODO exception handling
        cons = conskey.get()
#        logging.error(cons)
        predictions = []
        for candidate_key in cons.candidates:
            c = candidate_key.get()
            predictions.append({'candidate':{'id':c.key.id(),'name':c.name,'party':c.party,'coalition': c.coalition},'support':get_support(conskey,candidate_key)})
        return {'name':cons.name, 'state': cons.state, 'predictions':predictions};

def get_support(conskey,candidate_key):
    '''overall support for a candidate in a constituency'''
    #TODO implement this
    return 100
	
class HomeHandler(webapp2.RequestHandler):
    '''Shows the home page'''
    def get(self):
        (ct_user, url, url_linktext) = user_setup(self)
        template_values = {
            'url': url,
            'ct_user': ct_user,
            'url_linktext': url_linktext,
        }
        
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render(template_values))
		
class AllConsHandler(webapp2.RequestHandler):
    '''Shows the all constituencies page'''
    def get(self):
        (ct_user, url, url_linktext) = user_setup(self)
        template_values = {
            'url': url,
            'ct_user': ct_user,
            'url_linktext': url_linktext,
        }
        
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/constituencies.html')
        self.response.write(template.render(template_values))

class ContestPageHandler(webapp2.RequestHandler):
    '''Handler for showing a contest's page'''
    def get(self, contest_slug):
        cons_info = get_constituency_info(contest_slug)
        (ct_user, url, url_linktext) = user_setup(self)
        format = self.request.get("f")
        template_values = {
            'slug': contest_slug,
            'contest_info': cons_info,
            'ct_user': ct_user,
            'url': url,
            'url_linktext': url_linktext,
        }

        if (format == 'json'):
          self.response.headers['Content-Type'] = 'application/json'   
          json.dump(cons_info,self.response.out)
        else:
          self.response.headers['Content-Type'] = 'text/html'
          template = JINJA_ENVIRONMENT.get_template('templates/contest.html')
          self.response.write(template.render(template_values))

class UserPageHandler(webapp2.RequestHandler):
    '''Handler for showing a user's page'''
    def get(self, user_id):
        predictions = get_predictions(user_id)
        (ct_user, url, url_linktext) = user_setup(self)

        format = self.request.get("f")
        template_values = {
            'user_name': user_id,
            'ct_user': ct_user,
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

class SettingsPageHandler(webapp2.RequestHandler):
    '''Show and manage settings page'''
    def get(self):
        (ct_user, url, url_linktext) = user_setup(self)
        if not ct_user:
            return webapp2.redirect(url)
        template_values = {
            'ct_user': ct_user,
            'url': url,
            'url_linktext': url_linktext,
            'error_message':'Remember, only letters, numbers, #, @, _, and spaces.',
        }
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/settings.html')
        self.response.write(template.render(template_values))
    def post(self):
        (ct_user, url, url_linktext) = user_setup(self)
        if not ct_user:
            return webapp2.redirect(url)
        user_dn = self.request.get("display_name")
        error_message = ''
        
        if (ct_user.display_name == user_dn):
            update_success = False
            error_message = 'New name same as old.' 
        elif self.is_display_name_disallowed(user_dn):
            update_success = False
            error_message = 'New name not allowed.' 
        elif CTUser.is_display_name_taken(user_dn):
            update_success = False
            error_message = 'Someone already has this name.' 
        else:
            ct_user.display_name = user_dn
            ct_user.put()
            update_success = True
        
        template_values = {
            'success': update_success,
            'error_message': error_message,
            'ct_user': ct_user,
            'url': url,
            'url_linktext': url_linktext,
        }
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/settings.html')
        self.response.write(template.render(template_values))
    
class TukkaPageHandler(webapp2.RequestHandler):
    '''Show and process predictions form'''
    def get(self):
        (ct_user, url, url_linktext) = user_setup(self)
        if not ct_user:
            return webapp2.redirect(url)
        template_values = {
            'ct_user': ct_user,
            'url': url,
            'url_linktext': url_linktext,
            'error_message':'So, what is your prediction?',
        }
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/tukka.html')
        self.response.write(template.render(template_values))
    def post(self):
        (ct_user, url, url_linktext) = user_setup(self)
        if not ct_user:
            return webapp2.redirect(url)

        status = 500 #defaults to error
        cons_slug = self.request.get("contest_slug")
        candidate_id = self.request.get("candidate_id")
        
        tukka_response = {'message':'','total':-1} # empty response object

        #TODO exception handling
        # if constituency not found, send 404
        conskey = ndb.Key(CTConstituency, cons_slug)
        cons = conskey.get()
        if not cons :
            status = 404
            tukka_response['message'] = "Constituency not found"
        else:
            #TODO check candidate key in the list of candidates for this cons!
            # if candiate not found, send 404
            candidate_key = ndb.Key(CTCandidate, int(candidate_id))
            if not (candidate_key in set(cons.candidates)):
                status = 404
                logging.error(candidate_key)
                logging.error(set(cons.candidates))
                logging.error(cons.candidates)
                tukka_response['message'] = "Candidate not participating in this constituency."
            elif CTTukka.get_tukka(ct_user,cons):
                # if user+const has already voted for this, say he has already voted. Send 409
                status = 409
                tukka_response['message'] = "You already voted for this candidate in this constituency."
            else:
                # insert, send 200 and the sum (for now, send a 42) TODO
                status = 200 
                tukka = CTTukka(user=ct_user.key,constituency = cons.key, candidate = candidate_key)
                tukka.put()
                tukka_response['total'] = 42
                
        self.response.headers['Content-Type'] = 'application/json'   
        self.response.status = status
        json.dump(tukka_response,self.response.out)

    def is_display_name_disallowed(self,user_dn):
        invalid_users = set(['about','account','admin','administrator','administration','app','api','backup','bin','bot','bots','cache','chi','config','db','dev','download','edit','forum','feed','faq','ftp','help','home','index','login','logout','php','public','settings','system','task','username','xxx','you'])
        if user_dn.lower() in invalid_users :
            return True
        else:
            p = re.compile('^[a-zA-Z0-9#@_][a-zA-Z0-9#@_ ]*$') #chars,nums,and some others allowed, no spaces in beginning
            return not p.match(user_dn)

class TempAddHandler(webapp2.RequestHandler):
    '''Show and manage settings page'''
    def get(self):
        candidate1 = CTCandidate(name='Arvind Kejriwal',party='AAP')
        candidate1.put()
        candidate2 = CTCandidate(name='Narendra Modi',party='BJP', coalition='NDA')
        candidate2.put()
        candidate3 = CTCandidate(name='Ajay Rai',party='Congress', coalition='UPA')
        candidate3.put()
        candidate4 = CTCandidate(name='Vijay Jaiswal',party='BSP')
        candidate4.put()
        candidate5 = CTCandidate(name='Kailash Chaurasia',party='SP')
        candidate5.put()
        
        conskey = ndb.Key(CTConstituency, 'varanasi')
        cons = CTConstituency(key=conskey,name='Varanasi',state='Uttar Pradesh', candidates=[candidate1.key,candidate2.key,candidate3.key,candidate4.key,candidate5.key])
        cons.put()

        candidate11 = CTCandidate(name='Jaaved Jaaferi',party='AAP')
        candidate11.put()
        candidate12 = CTCandidate(name='Rajnath Singh',party='BJP', coalition='NDA')
        candidate12.put()
        candidate13 = CTCandidate(name='Rita Bahuguna Joshi',party='Congress', coalition='UPA')
        candidate13.put()
        candidate14 = CTCandidate(name='Nakul Dubey',party='BSP')
        candidate14.put()
        candidate15 = CTCandidate(name='Ashok Bajpai',party='SP')
        candidate15.put()
        
        conskey2 = ndb.Key(CTConstituency, 'lucknow')
        cons = CTConstituency(key=conskey2,name='Lucknow',state='Uttar Pradesh', candidates=[candidate11.key,candidate12.key,candidate13.key,candidate14.key,candidate15.key])
        cons.put()


        
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=HomeHandler, name='home'),
    webapp2.Route(r'/constituencies/', handler=AllConsHandler, name='constituencies'),
    webapp2.Route(r'/c/<contest_slug>/', handler=ContestPageHandler, name='contest_page'),
    webapp2.Route(r'/s/', handler=SettingsPageHandler, name='settings_page'),
    webapp2.Route(r'/t/', handler=TukkaPageHandler, name='tukka_page'),
    webapp2.Route(r'/u/<user_id>/', handler=UserPageHandler, name='user_page'),
    webapp2.Route(r'/u/<user_id>/<contest_slug>/', handler=UserPredictionHandler, name='user_prediction'),
    #webapp2.Route(r'/adddata/', handler=TempAddHandler, name='temp_addition'),
], debug=True)

# URL mapping, for reference
# /c/contest_slug - a contest's public page
# returns: list of public predictions about the contest, including summaries
# /u/user-id - a user's public page
# returns: list of public predictions by that user
# /u/user-id/contest-slug - user u's prediction about contest c
# returns: JSON object with candidate id, name, and party
