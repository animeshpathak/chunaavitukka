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

def get_predictions(ct_user):
    '''Get predictions of a user object'''
    predictions = []
    #make a query in the DB for predictions by this user.
    #TODO exception handling
    qry = CTTukka.query(CTTukka.user == ct_user.key)
    #TODO make this a map()?
    for tukka in qry.iter():
        candidate = tukka.candidate.get()
        constituency = tukka.constituency.get()
        predictions.append({'cons':{'name':constituency.name,'slug':constituency.key.id()},'candidate':{'id':candidate.key.id(),'name':candidate.name,'party':candidate.party,'coalition': candidate.coalition}})
    return predictions

def get_constituency_info(contest_slug):
    conskey = ndb.Key(CTConstituency, contest_slug)
    #TODO exception handling
    cons = conskey.get()
    predictions = []
    for candidate_key in cons.candidates:
        c = candidate_key.get()
        predictions.append({'candidate':{'id':c.key.id(),'name':c.name,'party':c.party,'coalition': c.coalition},'support':get_support(conskey,candidate_key)})
    return {'name':cons.name, 'state': cons.state, 'predictions':predictions};

def get_support(conskey,candidate_key):
    '''overall support for a candidate in a constituency'''
    count = 0
    qry = CTTukka.query(CTTukka.candidate == candidate_key, CTTukka.constituency == conskey)
    tukkalist = qry.fetch()
    for tukka in qry.iter(keys_only=True):
        #no need of non-key things when we are only counting
        count = count + 1
    #TODO insert into memcache?
    return count
	
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
        cons_list = []
        #make a query in the DB for all constituencies.
        #TODO exception handling
        qry = CTConstituency.query()
        #TODO make this a map()?
        for cons in qry.iter(projection=['name']): #only getting name, update if you want more info in templates
            cons_list.append(cons)
        
        template_values = {
            'url': url,
            'ct_user': ct_user,
            'url_linktext': url_linktext,
            'cons_list': cons_list,
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
        userkey = ndb.Key(CTUser, int(user_id))
        user = userkey.get()
        if user:
            predictions = get_predictions(user)
            (ct_user, url, url_linktext) = user_setup(self)

            format = self.request.get("f")
            template_values = {
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
        else:
            self.response.status = '404 User does not exist'#not found


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
        user = users.get_current_user()

        if not user:
            return
        if not users.is_current_user_admin():
            return
        
        infos = []

        for (cons,candidates) in infos:
            (slug,name,state) = cons
            print slug, name, state
            print "candidates"
            candidate_list = []
            for (cname, cparty, ccoalition) in candidates:
                print "   ", cname, cparty, ccoalition
                candidate = CTCandidate(name=cname,party=cparty, coalition=ccoalition)
                candidate.put()
                candidate_list.append(candidate.key)
            conskey = ndb.Key(CTConstituency, slug)
            cons = CTConstituency(key=conskey,name=name,state=state, candidates=candidate_list)
            cons.put()


        
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=HomeHandler, name='home'),
    webapp2.Route(r'/constituencies/', handler=AllConsHandler, name='constituencies'),
    webapp2.Route(r'/c/<contest_slug>/', handler=ContestPageHandler, name='contest_page'),
    webapp2.Route(r'/s/', handler=SettingsPageHandler, name='settings_page'),
    webapp2.Route(r'/t/', handler=TukkaPageHandler, name='tukka_page'),
    webapp2.Route(r'/u/<user_id:\d+>/', handler=UserPageHandler, name='user_page'),
    webapp2.Route(r'/u/<user_id:\d+>/<contest_slug>/', handler=UserPredictionHandler, name='user_prediction'),
    # -- this is admin only webapp2.Route(r'/adddata/', handler=TempAddHandler, name='temp_addition'),
], debug=True)

# URL mapping, for reference
# /c/contest_slug - a contest's public page
# returns: list of public predictions about the contest, including summaries
# /u/user-id - a user's public page
# returns: list of public predictions by that user
# /u/user-id/contest-slug - user u's prediction about contest c
# returns: JSON object with candidate id, name, and party
