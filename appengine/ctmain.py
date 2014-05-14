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
from models import CTOverallTukka 
from models import CTLeague 

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
    
def get_constituency_info(ct_user, contest_slug):
    '''check if ct_user is none!'''
    conskey = ndb.Key(CTConstituency, contest_slug)
    #TODO exception handling
    cons = conskey.get()
    predictions = []

    #initialize to None
    selected_candidate_key = None
    selected_candidate = None
    #this may be a tukka, or None
    if ct_user:
        tukka = CTTukka.get_tukka(ct_user,cons)
        if tukka: 
            selected_candidate_key = tukka.candidate

    for candidate_key in cons.candidates:
        c = candidate_key.get()
        predictions.append({'candidate':{'id':c.key.id(),'name':c.name,'party':c.party,'coalition': c.coalition},'support':get_support(conskey,candidate_key)})
        if candidate_key == selected_candidate_key:
            selected_candidate = c
                
    #figure out if ct_user already voted for this one
    return {'name':cons.name, 'state': cons.state, 'predictions':predictions, 'selected_candidate': selected_candidate};

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
		
class FAQHandler(webapp2.RequestHandler):
    '''Shows the FAQ page'''
    def get(self):
        (ct_user, url, url_linktext) = user_setup(self)
        template_values = {
            'url': url,
            'ct_user': ct_user,
            'url_linktext': url_linktext,
        }        
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/faq.html')
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

class TopConsHandler(webapp2.RequestHandler):
    '''Shows the top 20 constituencies page'''
    def get(self):
        (ct_user, url, url_linktext) = user_setup(self)
        cons_list = []
        toplist = [
('ajmer','Ajmer','Rajasthan'),
('amethi','Amethi','Uttar Pradesh'),
('amritsar','Amritsar','Punjab'),
('bangalore-s','Bangalore (South)','Karnataka'),
('baramati','Baramati','Maharashtra'),
('barmer','Barmer','Rajasthan'),
('bastar','Bastar','Chhattisgarh'),
('chandigarh','Chandigarh','Chandigarh'),
('delhi-chandnichowk','Chandni Chowk','Delhi'),
('gandhinagar','Gandhinagar','Gujarat'),
('guna','Guna','Madhya Pradesh'),
('gurdaspur','Gurdaspur','Punjab'),
('gurgaon','Gurgaon','Haryana'),
('jaipur-rural','Jaipur (Rural)','Rajasthan'),
('kanpur-urban','Kanpur (Urban)','Uttar Pradesh'),
('lucknow','Lucknow','Uttar Pradesh'),
('madhepura','Madhepura','Bihar'),
('mumbai-ne','Mumbai (North East)','Maharashtra'),
('delhi-new','New Delhi','Delhi'),
('shimoga','Shimoga','Karnataka'),
('varanasi','Varanasi','Uttar Pradesh'),
]
        for (slug,name,state) in toplist:
            cons_list.append({'slug':slug,'name':name,'state':state})
        
        template_values = {
            'toplist' : True,
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
        (ct_user, url, url_linktext) = user_setup(self)
        cons_info = get_constituency_info(ct_user, contest_slug)
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
            overall_predictions = CTOverallTukka.get_overall_tukka(user)
            my_leagues = None #init to none

            (ct_user, url, url_linktext) = user_setup(self)
            follows = [] #list of people whom this guy follows, but only if it is me!

            my_overall_predictions = None

            if not ct_user:
                can_follow = True
            else:
                id_list = []
                for key in ct_user.follows:
                    id_list.append(int(key.id()))
                follow_set = set(id_list)
                can_follow = (userkey != ct_user.key) and not (userkey.id() in follow_set)
                if user == ct_user:
                    my_leagues = [key.get() for key in ct_user.leagues]
                    for (other_id) in follow_set:
                        #TODO properly cast this object
                        other = ndb.Key(CTUser, int(other_id)).get()
                        follows.append({'id':other_id, 'display_name':other.display_name})
                else:
                    my_overall_predictions = CTOverallTukka.get_overall_tukka(ct_user)
            
            format = self.request.get("f")
            template_values = {
                'ct_user': ct_user,
                'other_user': user,
                'my_leagues': my_leagues,
                'follows': follows,
                'url': url,
                'url_linktext': url_linktext,
                'predictions': predictions,
                'overall_predictions': overall_predictions,
                'can_follow': can_follow,
                'my_overall_predictions': my_overall_predictions,
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
            'url_linktext': 'Logout ' + ct_user.display_name, #hard hack for issue#15
        }
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/settings.html')
        self.response.write(template.render(template_values))
    def is_display_name_disallowed(self,user_dn):
        invalid_users = set(['about','account','admin','administrator','administration','app','api','backup','bin','bot','bots','cache','chi','config','db','dev','download','edit','forum','feed','faq','ftp','help','home','index','login','logout','php','public','settings','system','task','username','xxx','you'])
        if user_dn.lower() in invalid_users :
            return True
        else:
            p = re.compile('^[a-zA-Z0-9#@_][a-zA-Z0-9#@_ ]*$') #chars,nums,and some others allowed, no spaces in beginning
            return not p.match(user_dn)
    

class UserFollowHandler(webapp2.RequestHandler):
    '''Follow. Only accessible by POST, user_id needed. 200 if all is well, 404 is other user not found. 409 if re-try adding'''
    def post(self):
        (ct_user, url, url_linktext) = user_setup(self)
        #not signed in, sorry.
        if not ct_user:
            return webapp2.redirect(url)

        status = 500 #defaults to error
        other_id = self.request.get("user_id")
        
        follow_response = {'message':''} # empty response object

        #TODO exception handling
        # if constituency not found, send 404
        other_user_key = ndb.Key(CTUser, other_id)
        #TODO check if he exists
        if not other_user_key :
            status = 404
            follow_response['message'] = "User with ID " + other_id + " not found"
        else:
            #add him to my list of follows
            ct_user.follows.append(other_user_key)
            ct_user.put()
            #TODO check other candidate key in the list of candidates for this cons!
            status = 200
            
                
        self.response.headers['Content-Type'] = 'application/json'   
        self.response.status = status
        json.dump(follow_response,self.response.out)


        
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
                tukka_response['message'] = "Candidate not participating in this constituency."
            elif CTTukka.get_tukka(ct_user,cons):
                # if user+const has already voted for this, say he has already voted. Send 409
                status = 409
                tukka_response['message'] = "You have already made a prediction for this constituency."
            else:
                # insert, send 200 and the sum (for now, send a 42) TODO
                # get total before insert
                prev_total = get_support(cons.key,candidate_key)
                tukka = CTTukka(user=ct_user.key,constituency = cons.key, candidate = candidate_key)
                tukka.put()
                status = 200 
                tukka_response['total'] = prev_total + 1
                
        self.response.headers['Content-Type'] = 'application/json'   
        self.response.status = status
        json.dump(tukka_response,self.response.out)

class OverallTallyHandler(webapp2.RequestHandler):
    '''Show and process predictions form'''
    def get(self):
        (ct_user, url, url_linktext) = user_setup(self)
        if not ct_user:
            return webapp2.redirect(url)
            
        if CTOverallTukka.get_overall_tukka(ct_user):
            #already make a tukka
            return webapp2.redirect('/u/' + str(ct_user.key.id())+'/')

        conslist = [
 ('UPA', 'UPA', 538, 'coalition'),
('NDA', 'NDA', 542, 'coalition'),
('INC',	'INC',	464, 'party'),
('BJP',	'BJP',	428, 'party'),
('AAP',	'AAP',	432, 'party'),
('TMC',	'AITC', 131, 'party'),
('DMK',	'DMK',	35, 'party'),
('AIADMK', 'AIADMK',	40, 'party'),
('SP',	'SP',	197, 'party'),
('BSP',	'BSP',	503, 'party'),
('JD',	'JDU',	93, 'party'),
('RJD',	'RJD',	29, 'party'),
('CPI',	'CPI',	68, 'party'),
('BJD',	'BJD',	21, 'party'),
('SS',	'SS',	58, 'party'),
('MNS',	'MNS',	10, 'party'),
('NCP',	'NCP',	36, 'party'),
('Others',	'Others',	543, 'party'),
]
        consinfo = [{'key': key, 'title': title, 'max':max, 'teamtype': teamtype} for (key, title, max, teamtype) in conslist]
            
        template_values = {
            'ct_user': ct_user,
            'url': url,
            'url_linktext': url_linktext,
            'conslist': consinfo,
        }
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/overalltally.html')
        self.response.write(template.render(template_values))
    def post(self):
        (ct_user, url, url_linktext) = user_setup(self)
        if not ct_user:
            return webapp2.redirect(url)

        status = 500 #defaults to error
        
        tukka_response = {'message':''} # empty response object

        #TODO exception handling
        if CTOverallTukka.get_overall_tukka(ct_user):
            # if user has already voted for this, say he has already voted. Send 409
            status = 409
            tukka_response['message'] = "You have already made an overall prediction."
        else:
            # insert, send 200 
            overall_tukka = CTOverallTukka(user=ct_user.key,
                upa = int(self.request.get("UPA")),
                nda = int(self.request.get("NDA")),
                inc = int(self.request.get("INC")),
                bjp = int(self.request.get("BJP")),
                aap = int(self.request.get("AAP")),
                tmc = int(self.request.get("TMC")),
                dmk = int(self.request.get("DMK")),
                aiadmk = int(self.request.get("AIADMK")),
                sp = int(self.request.get("SP")),
                bsp = int(self.request.get("BSP")),
                jd = int(self.request.get("JD")),
                rjd = int(self.request.get("RJD")),
                cpi = int(self.request.get("CPI")),
                bjd = int(self.request.get("BJD")),
                ss = int(self.request.get("SS")),
                mns = int(self.request.get("MNS")),
                ncp = int(self.request.get("NCP")),
                others = int(self.request.get("Others"))
            )
            overall_tukka.put()
            status = 200 
            return webapp2.redirect('/u/' + str(ct_user.key.id())+'/')
                
        self.response.headers['Content-Type'] = 'application/json'   
        self.response.status = status
        json.dump(tukka_response,self.response.out)
    
class NewLeagueFormHandler(webapp2.RequestHandler):
    '''Handles creation of a new league'''
    def get(self):
        (ct_user, url, url_linktext) = user_setup(self)
        if not ct_user:
            return webapp2.redirect(url)
            
        template_values = {
            'ct_user': ct_user,
            'url': url,
            'url_linktext': url_linktext,
        }
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/newleague.html')
        self.response.write(template.render(template_values))

    def post(self):
        ''' Create a new league with league_name as name'''
        (ct_user, url, url_linktext) = user_setup(self)
        if not ct_user:
            self.response.status = 401 #unauthorized
            return

        league_name = self.request.get('league_name')
        p = re.compile('^[a-zA-Z0-9#@_][a-zA-Z0-9#@_ ]*$') #chars,nums,and some others allowed, no spaces in beginning
        if league_name != None and p.match(league_name):
            league = CTLeague(creator = ct_user.key, name = league_name, members = [ct_user.key])
            league.put()
            ct_user.leagues.append(league.key)
            ct_user.put()
            #send to the league
            return webapp2.redirect('/l/' + str(league.key.id()) + '/')
        else:
            self.response.status = 400 #unauthorized
            self.response.write('Invalid league name "' + league_name + '". Please go back and try again, with only letters, numbers, spaces, @,#, and _. Note that the league name cannot begin with a space.')
        
class LeaguePageHandler(webapp2.RequestHandler):
    def get(self,league_id):
        (ct_user, url, url_linktext) = user_setup(self)
        
        league_key = ndb.Key(CTLeague, int(league_id))
        league = league_key.get()
        
        if not league:
            self.response.status = 404
            return
        
        predictions = [] # {user:user;overall_pred:overall_pred}
        
        league_members = [key.get() for key in league.members]
        
        for user in league_members:
            predictions.append({'user': user, 'overall_tukka': CTOverallTukka.get_overall_tukka(user)})
        
        template_values = {
            'ct_user': ct_user,
            'url': url,
            'url_linktext': url_linktext,
            'league_id': league_id,
            'league_name': league.name,
            'league_creator': league.creator.get(),
            'league_members': league_members,
            'predictions': predictions,
        }
        self.response.headers['Content-Type'] = 'text/html'
        template = JINJA_ENVIRONMENT.get_template('templates/league.html')
        self.response.write(template.render(template_values))
    def post(self,league_id):
        '''The currently logged in user wants to join this league'''
        (ct_user, url, url_linktext) = user_setup(self)
        if not ct_user:
            self.response.status = 401 #unauthorized
            return
            
        league_key = ndb.Key(CTLeague, int(league_id))
        league = league_key.get()
        if not league:
            self.response.status = 404
            return
            
        #TODO transaction?    
        league.members.append(ct_user.key)
        league.put()
        ct_user.leagues.append(league_key)
        ct_user.put()
        return webapp2.redirect('/l/' + str(league.key.id()) + '/')

class TempAddHandler(webapp2.RequestHandler):
    '''Temp adding bit'''
    def get(self):
        user = users.get_current_user()

        if not user:
            return
        if not users.is_current_user_admin():
            return
        
        gsqry = CTCandidate.query(CTCandidate.name== 'Geetha Shivrajkumar')
        gs = gsqry.fetch(1)[0]

        shimoga = ndb.Key(CTConstituency, 'shimoga').get()

        shimoga.candidates.append(gs.key)
        shimoga.put()
        
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=HomeHandler, name='home'),
    webapp2.Route(r'/faq/', handler=FAQHandler, name='faq'),
    webapp2.Route(r'/constituencies/', handler=AllConsHandler, name='constituencies'),
    webapp2.Route(r'/top20/', handler=TopConsHandler, name='top20'),
    webapp2.Route(r'/c/<contest_slug>/', handler=ContestPageHandler, name='contest_page'),
    webapp2.Route(r'/s/', handler=SettingsPageHandler, name='settings_page'),
    webapp2.Route(r'/t/', handler=TukkaPageHandler, name='tukka_page'),
    webapp2.Route(r'/u/<user_id:\d+>/', handler=UserPageHandler, name='user_page'),
    webapp2.Route(r'/u/<user_id:\d+>/<contest_slug>/', handler=UserPredictionHandler, name='user_prediction'),
    webapp2.Route(r'/follow/', handler=UserFollowHandler, name='follow_user'),
    webapp2.Route(r'/overall-tally/', handler=OverallTallyHandler, name='overall-tally'),
    webapp2.Route(r'/l/new/', handler=NewLeagueFormHandler, name='new_league_page'),
    webapp2.Route(r'/l/<league_id:\d+>/', handler=LeaguePageHandler, name='league_page'),
    # -- this is admin only 
    #webapp2.Route(r'/adddata/', handler=TempAddHandler, name='temp_addition'),
], debug=True)

# URL mapping, for reference
# /c/contest_slug - a contest's public page
# returns: list of public predictions about the contest, including summaries
# /u/user-id - a user's public page
# returns: list of public predictions by that user
# /u/user-id/contest-slug - user u's prediction about contest c
# returns: JSON object with candidate id, name, and party
