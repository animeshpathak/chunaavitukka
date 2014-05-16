"""A webapp2 server for ChunaaviTukka cron jobs"""

import os
import urllib
import json
import logging
import re

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import urlfetch

from models import CTUser 
from models import CTCandidate 
from models import CTConstituency
from models import CTTukka 
from models import CTOverallTukka 
from models import CTLeague 
from models import CTLeagueComment 
from models import CTFinalTally 

import webapp2

class TallyUpdateHandler(webapp2.RequestHandler):
    '''Temp adding bit'''
    def get(self):
        ndtv_url = "http://electionsdata.ndtv.com/feeds/ge/2014/json/PartyStanding_INDIA.json"
        result = urlfetch.fetch(ndtv_url)
        if result.status_code == 200:
            tally_id = "overall_tally"
            self.response.write('Updating Tally...')
            #get JSON
            #parse JSON
            raw_results =  json.loads(result.content)       
            results = dict()
            #if not null, update the tally object
            for alliance in raw_results['PS']['A']:
                aname = alliance['nm']
                results[aname] = alliance['ALPR']
                if aname == 'Cong+' or aname == 'BJP+' or aname == 'Others':
                    for party in alliance['p']:
                        results[party['nm']] = party['LPR'] 
            
            tally_key = ndb.Key(CTFinalTally, tally_id)
            r = tally_key.get()
            if not r:
                r = CTFinalTally(key=tally_key)
            r.upa = int(results['Cong+'])
            r.nda = int(results['BJP+'])
            r.inc = int(results['Cong'])
            r.bjp = int(results['BJP'])
            r.aap = int(results['AAP'])
            r.tmc = int(results['TMC'])
            r.dmk = int(results['DMK'])
            r.aiadmk = int(results['ADMK'])
            r.sp = int(results['SP'])
            r.bsp = int(results['BSP'])
            r.jd = int(results['JDU'])
            r.rjd = int(results['RJD'])
            r.cpim = int(results['CPI'])
            r.bjd = int(results['BJD'])
            r.ss = int(results['SS'])
            r.mns = int(results['MNS'])
            r.ncp = int(results['NCP'])
            r.ysrc = int(results['YSRC'])
            r.trs = int(results['TRS'])
            r.tdp = int(results['TDP'])
            r.cpm = int(results['CPM'])
            
            r.put()
            self.response.write('..done!<br/>')
            self.response.write(r)
        else:
            self.response.write("Something went wrong in fetching URL " + ndtv_url)
            logging.error("Something went wrong in fetching URL " + ndtv_url)

        
application = webapp2.WSGIApplication([
    webapp2.Route(r'/admin/tallyupdate/', handler=TallyUpdateHandler, name='tally_update'),
], debug=True)

