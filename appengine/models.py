#Models.py, for defining all data models
from google.appengine.ext import ndb

import logging


#CTUser
#profile
#	- user : Google User object
#	- photo -- coming later
#	- displayname : unique
#	- ID = key

class CTUser(ndb.Model):
  '''Models an individual Guestbook entry with content and date.'''
  google_user = ndb.UserProperty(required=True)
  display_name = ndb.StringProperty(required=False)
  created_at = ndb.DateTimeProperty(auto_now_add=True)
  updated_at = ndb.DateTimeProperty(auto_now=True)
  follows = ndb.KeyProperty(kind='CTUser',repeated=True)
  leagues = ndb.KeyProperty(kind='CTLeague',repeated=True)
  
  #TODO make this transactional
  @classmethod
  def get_or_insert(cls,google_user):
    '''Gets user with the given google_user object, or adds one'''
    #find a CT user with this google_user, and if it does not exist, create it
    qry = CTUser.query(CTUser.google_user == google_user)
    userlist = qry.fetch(1)
    if not userlist:
        #insert this user
        ct_user = CTUser(google_user = google_user, display_name='NoName')
        ct_user.put()
    else:
        #this is the user
        ct_user = userlist[0]
    return ct_user
    
  @classmethod
  def is_display_name_taken(cls,name):
    '''returns the user whose name is provided'''
    qry = CTUser.query(CTUser.display_name == name)
    userlist = qry.fetch(2)
    if not userlist:
        return False
    else:
        if (len(userlist) > 1):
            logging.error("Username " + name + " multiple assigned!!")
        return True
    
#candidate
#	- ID : ID
#	- Name : String
#	- Party : String
#	- Coalition : String, none possible
class CTCandidate(ndb.Model):
    '''Models a candidate'''
    name = ndb.StringProperty(required=True)
    party = ndb.StringProperty(required=True)
    coalition = ndb.StringProperty(required=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)
    
# constituency
# slug - key
# name - string
# state - string
# candidates - keys of candidates
# sums are stored elsewhere
class CTConstituency(ndb.Model):
    '''Models a constituency, always use the slug as the key'''
    name = ndb.StringProperty(required=True)
    state = ndb.StringProperty(required=True)
    candidates = ndb.KeyProperty(kind=CTCandidate,repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

# tukka
# - CTUser ref
# - CTCons ref
# - CTCandidate ref
class CTTukka(ndb.Model):
    '''Models a prediction'''
    user = ndb.KeyProperty(kind=CTUser,repeated=False)
    constituency = ndb.KeyProperty(kind=CTConstituency,repeated=False)
    candidate = ndb.KeyProperty(kind=CTCandidate,repeated=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def get_tukka(cls,ct_user,ct_cons):
        '''Returns the tukka if a prediction exists for this constituency by this user'''
        if not ct_user:
            return None
        if not ct_cons:
            return None
        qry = CTTukka.query(CTTukka.user == ct_user.key, CTTukka.constituency == ct_cons.key)
        tukkalist = qry.fetch(1)
        if not tukkalist:
            return None
        else:
            return tukkalist[0]

# overall tukka
# - CTUser ref
class CTOverallTukka(ndb.Model):
    '''Models a prediction for overall scores'''
    user = ndb.KeyProperty(kind=CTUser,repeated=False)
    upa = ndb.IntegerProperty(repeated=False)
    nda = ndb.IntegerProperty(repeated=False)
    inc = ndb.IntegerProperty(repeated=False)
    bjp = ndb.IntegerProperty(repeated=False)
    aap = ndb.IntegerProperty(repeated=False)
    tmc = ndb.IntegerProperty(repeated=False)
    dmk = ndb.IntegerProperty(repeated=False)
    aiadmk = ndb.IntegerProperty(repeated=False)
    sp = ndb.IntegerProperty(repeated=False)
    bsp = ndb.IntegerProperty(repeated=False)
    jd = ndb.IntegerProperty(repeated=False)
    rjd = ndb.IntegerProperty(repeated=False)
    cpi = ndb.IntegerProperty(repeated=False)
    bjd = ndb.IntegerProperty(repeated=False)
    ss = ndb.IntegerProperty(repeated=False)
    mns = ndb.IntegerProperty(repeated=False)
    ncp = ndb.IntegerProperty(repeated=False)
    ysrc = ndb.IntegerProperty(repeated=False)
    trs = ndb.IntegerProperty(repeated=False)
    tdp = ndb.IntegerProperty(repeated=False)
    cpim = ndb.IntegerProperty(repeated=False)
    others = ndb.IntegerProperty(repeated=False)
    
    @classmethod
    def get_overall_tukka(cls,ct_user):
        '''Returns the tukka if a prediction exists by this user, or None'''
        if not ct_user:
            return None
        qry = CTOverallTukka.query(CTOverallTukka.user == ct_user.key)
        tukkalist = qry.fetch(1)
        if not tukkalist:
            return None
        else:
            return tukkalist[0]
    
    
    nda = ndb.IntegerProperty(repeated=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)
            
class CTLeagueComment(ndb.Model):
    '''Models a constituency, always use the slug as the key'''
    contents = ndb.StringProperty(required=True)
    author = ndb.KeyProperty(kind=CTUser,repeated=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)
            
# League
#  - creator
#  - name (OK with repetitions)
#  - create and update dates
#  - members
class CTLeague(ndb.Model):
    '''Models a constituency, always use the slug as the key'''
    name = ndb.StringProperty(required=True)
    creator = ndb.KeyProperty(kind=CTUser,repeated=False)
    members = ndb.KeyProperty(kind=CTUser,repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)
    comments = ndb.KeyProperty(kind=CTLeagueComment, repeated=True)

    