__version__ = 0.0

import os
import pickle
import settings
from logger import Logger
from time import time, sleep
from betfair.api_ng import API
from datetime import datetime, timedelta

#test
from login_config import login_info
''' 
Function List:
    __init__(): DONE
    pickle_data(): DONE
    unpickle_data(): DONE
    update_ignores()
    update_betcount()
    get_betcount()
    do_throttle()
    do_login()
    keep_alive()
    get_markets()
    create_bets()
    place_bets()
    filter_menu_path()
    run()
'''
class SoccerBot(object):
    """Maps soccer market relationships"""
    def __init__(self):
        self.username= ''  
        self.loggr = None  
        self.api = None
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.ignores_path = '%s/ignores.pkl' % self.abs_path
        self.ignores = self.unpickle_data(self.ignores_path,[]) #coverts pickled ignores data into array.
        self.betcount_path = '%s/betcount.pkl' % self.abs_path
        self.betcount = self.unpickle_data(self.betcount_path,{})#{hrs,Mkt_id} converts pickled betcount data in dictionary.
        self.throttle = { 'next': time(), #time we can send next request
                          'wait': 1.0,    #time between requests
                          'keep_alive': time(), 
                          'update_closed': time()
         }
        self.session = False

    def pickle_data(self, filepath='', data = None):
        '''pickle object to a file'''
        f = open(filepath, 'wb')
        pickle.dump(data, f)
        f.close()

    def unpickle_data(self, filepath='', default_object = None):
        '''unpickle file to an object, and return object'''
        if os.path.exists(filepath):
            f = open(filepath, 'rb')
            data = pickle.load(f)
            f.close()
            return data
        return default_object #i.e None

    #Function: adds market to ignores list if bet successfully placed
    def update_ignores(self, market_id=''):
        ''' updates ignores list'''
        if market_id:
            #add market to ignores dict
            if market_id not in self.ignores:
                self.ignores.append(market_id)
                self.pickle_data(self.ignores_path, self.ignores)
        else:
            #check for closed market once every 2 hours
            count = len(self.ignores)
            now = time()
            if count > 0 and now > self.throttle['update_closed']:
                secs = 2 * 60 * 60 #2 hours
                self.throttle['update_closed'] = now + secs
                msg = 'Checking %s MARKETS FOR CLOSED STATUS ...' %count
                print(msg)
                for i in range(0, count, 5):
                    market_ids = self.ignores[i:i+5] #list upto 5 market ids
                    self.do_throttle()
                    books = self.get_market_books(market_ids) #anasema nini?
                    for book in books:
                        if book['status'] == 'CLOSED':
                            self.ignores.remove(book['marketId'])
                            self.pickle_data(self.ignores_path, self.ignores)

    #Function: Updates bet count to avoid exceeding 1000 per hours
    def update_betcount(self, betcount = 0):
        hour = datetime.utcnow().hour
        if hour not in self.betcount:
            self.betcount[hour] = [betcount] #add new hour
            for key in self.betcount:
                if key!= hour: self.betcount.pop(key)
        else:
            self.betcount[hour].append(betcount)
        self.pickle_data(self.betcount_path, self.betcount)


    #Function: Gets bet-count for current hour as integer
    def get_betcount(self):
        betcount = 0
        hour = datetime.utcnow().hour
        if hour in self.betcount:
            betcount = sum(self.betcount[hour])
        reurn betcount

    #Function: Return when it's safe to continue
    def do_throttle(self):
        now = time()
        if now < self.throttle['next']:
            wait = self.throttle['next'] - now
            sleep(wait)
        self.throttle['next'] = time() + self.throttle['wait']
        return


    #Login to betfair and set session status 
    def do_login(self, username='', password=''):
        self.session = False
        resp = self.api.login(username, password)
        if resp = 'Success':
            self.session = True
        else:
            self.session = False #login failed
            msg = 'api.login() resp = %s' % resp
            raise Exception(msg)


    #Returns a list of markets"
    def get_markets(self, market_ids=None):
        if market_ids:
            params = {
                'filter': {
                    'marketTypeCodes': setings.market_types,
                    'marketBettingTypes': ['ODDS'],
                    'turnInPlayEnabled': True, #will go in-play
                    'inPlayOnly': False, #market NOT currently in-play
                    'marketIds': market_ids
                    },
                'marketProjection': ['RUNNER_DESCRIPTION'],
                'maxResults': 1000, #maximum allowed by betfair
                'sort': 'FIRST_TO_START'
                }
            markets = self.api.get_markets(params)
            if type(markets) is list:
                return markets
            else:
                msg = 'api.get_markets() resp = %s' % markets
                raise Exception(msg)

    

    
    
#Testing Object Initialization
USERNAME = login_info['username']
PASSWORD = login_info['password']
APP_KEY = login_info['app_key_live']
AUS = False
log = Logger(AUS)
log.xprint("Testing Bot")
soccer_bot = SoccerBot()
print(soccer_bot.abs_path)
print(soccer_bot.betcount_path)
print(soccer_bot.throttle)
print(soccer_bot.betcount)
print(soccer_bot.ignores)

