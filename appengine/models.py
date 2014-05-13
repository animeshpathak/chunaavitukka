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
        qry = CTTukka.query(CTTukka.user == ct_user.key, CTTukka.constituency == ct_cons.key)
        tukkalist = qry.fetch(1)
        if not tukkalist:
            return None
        else:
            return tukkalist[0]
