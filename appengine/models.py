#Models.py, for defining all data models
from google.appengine.ext import ndb

#candidate
#	- ID : ID
#	- Name : String
#	- Party : ref
#	- Coalition


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
  
  #TODO make this transactional
  @classmethod
  def get_or_insert(cls,google_user):
    '''Gets user with the given google_user object, or adds one'''
    #find a CT user with this google_user, and if it does not exist, create it
    qry = CTUser.query(CTUser.google_user == google_user)
    userlist = qry.fetch(1)
    if not userlist:
        #insert this user
        ct_user = CTUser(google_user = google_user, display_name='Unknown Display Name')
        ct_user.put()
    else:
        #this is the user
        ct_user = userlist[0]
    return ct_user


