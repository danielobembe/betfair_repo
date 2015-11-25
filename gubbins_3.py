__version__ = 0.01

import os
import pickle
import settings
from logger import Logger
from time import time, sleep
from betfair.api_ng import API
from datetime import datetime, timedelta

class BetBot(object):
    """Betfair laying bot. Lays field using parameters in settings.py"""

    def __init__(self):
        self.username      = ''
        self.logger        = None
        self.api           = None
        self.abs_path      = os.path.abspath(os.path.dirname(__file__))
        self.ignores_path  = '%s/ignores.pkl' % self.abs_path
        self.ignores       = self.unpickle_data(self.ignores_path, [])
        self.betcount_path = '%s/betcount.pkl' % self.abs_path
        self.betcount      = self.unpickle_data(self.betcount_path, {})
        self.throttle      = {
            'next': time(),        #time we can send next request
            'wait': 1.0,           #time in seconds between requests
            'keep_alive': time()   #auto_updated in keep_alive()
            'update_closed':time() #auto_updated in update_ignores()
            }
        self.session = False


    def pickled_data(self, filepath='', data = None):
        """Pickle object to file"""
        f = open(filepath, 'wb')
        pickle.dump(data, f)
        f.close()


    def unpicke_data(self, filepath='', default_object = None):
        """Unpickle file to object, and return object"""
        if os.path.exists(filepath):
            f = open(filepath, 'rb')
            data = pickle.load(f)
            f.close()
            return data
        return default_object         #otherwise return empty default object



    def update_ignores(self, market_id = ''):
        """Update the 'Ignores' List"""
        if market_id:
            #add market to ignores list
            if market_id not in self.ignores:
                self.ignores.append(market_id)
                self.pickle_data(self.ignores_path, self.ignores)
        else:
            #check for closed markets (once every 2 hours)
            count = len(self.ignores)
            now = time()
            if count > 0 and now > self.throttle['update_closed']:
                secs = 2 * 60 * 60    #2hrs
                self.throttle['update_closed'] = now + secs
                msg = 'CHECKING %s MARKETS FOR CLOSED STATUS...' % count
                self.logger.xprint(msg)
                for i in range(0, count, 5):
                    market_ids = self.ignores[i:i+5] #list upto 5 market ids
                    self.do_throttle()
                    books = self.get_market_books(market_ids)
                    print(books)
                    for book in books:
                        if book['status'] == 'CLOSED':
                            #remove from ignores
                            self.ignores.remove(book['marketId'])
                            self.pickle_data(self.ignores_path, self.ignores)


    def update_betcount(self, betcount = 0):
        """Update bet count to avoid exceeding 1000 bets per hour"""
        hour = datetime.utcnow().hour
        if hour not in self.betcount:
            #new hour
            self.betcount[hour] = [betcount]
            #remove 'old' keys
            for key in self.betcount:
                if key != hour: self.betcount.pop(key)
        else:
            #current hour
            self.betcount[hour].append(betcount)
        #pickle
        self.pickle_data(self.betcount_path, self.betcount)


    def get_betcount(self):
        """Returns bet count for hour as integer"""
        betcount = 0
        hour = datetime.utcnow().hour
        if hour in self.betcount:
            betcount = sum(self.betcount[hour])
        return betcount


    def do_throttle(self):
        """Return when it's safe to continue"""
        now = time()
        if now < self.throttle['next']:
            wait = self.throttle['next'] - now
            sleep(wait)
        self.throttle['next'] = time()+self.throttle['wait']
        return


    def do_login(self, username='', password=''):
        """Return when it's safe to continue"""
        self.session = False
        resp = self.api.login(username, password)
        if resp == 'SUCCESS':
            self.session = True
        else:
            self.session = False  # failed login
            msg = 'api.login() resp = %s' % resp
            raise Exception(msg)
        

    def keep_alive(self):
        """Refresh Login session. They typically expire after 20 mins"""
        """Betfair throttle = 1 request ever 7 mins"""
        now = time()
        if now > self.throttle['keep_alive']:
            #refresh
            self.session = False
            res = self.api.keep_alive()
            if resp == 'SUCCESS':
                self.throttle['keep_alive'] = now + (15 * 60)  #add15 mins
                self.session = True
            else:
                self.session = False
                msg = 'api.keep_alive() resp = %s' % resp
                raise Exception(msg)


    def get_markets(self, market_ids = None):
        """Returns a list of markets"""
        if market_ids:
            params = {
                'filter': {
                    'marketTypeCodes': settings.market_types,
                    'marketBettingTypes': ['ODDS'],
                    'turnInPlayEnabled': True,  #will go in-play
                    'inPlayOnly': False,        #market NOT currently in play
                    'marketIds': market_ids
                },
                'marketProjection': ['RUNNER_DESCRIPTION'],
                'maxResults': 1000,
                'sort': 'FIRST_TO_START'
            }
            #send the requests
            markets = self.api.get_markets(params)
            if type(markets) is list:
                return markets
            else:
                msg = 'api.get_market() resp = %s' % markets
                raise Exception(msg)

            
    def create_bets(self, makets = None, market_paths = None):
        """Returns a dict of bets. keys=Market ids, vals = list of bets"""
        market_bets={}
        #loop through markets
        for market in markets:
            #get bet seting sor this market 
            if market_id in market_paths:
                bets_index = market_paths[market_id]['bets_index']
                bets = setting.market_bets[bets_index]
                #creae bets for this market
                market_path = market+paths[market_id]['market_path']
                market_bets[market_id]={'bets':[],'market_path':market_path}
                for runner in market['runners']:
                    for bet in bets:
                        new_bet={}
                        new_bet['selectionId'] = runner['selectionId']
                        new_bet['side'] = bet['side']
                        new_bet['orderType'] = 'LIMIT'
                        new_bet['limitOrder'] = {
                            'size': bet['stake'],
                            'price': bet['price'],
                            'persistenceType': 'PERSIST' #Keep at in-play. Set as 'LAPSE' to cancel.
                        }
                        market_bets[market_id]['bets'].append(new_bet)
        return market_bets #max bet count = 1000


    def place_bets(self, market_bets = None):
    """Loop through markets and place bets"""
        for market_id in market_bets:
            bet = market_bets[market_id]['bets']
            if bets:
                new_betcount = len(bets)
                self.update_betcount(new_betcount)
                betcount = self.get_betcount()  #total bets placed in curren hour
                if betcount >= settings.max_transactions: return
                #place bets
                market_path = market_bets[market_id]['market_path']
                msg = 'MARKET PATH: %s\n' % market_path
                msg += 'PLACING % BETS ...\n' % len(bets)
                for i, bet in enumerate(bets):
                    msg += '%s: %s\n' % (i, bet)
                self.logger.xprint(msg)
                self.do_throttle()
                resp = self.api.place_bets(market_id, bets)
                if (type(resp) is dict
                    and 'status' in resp
                    ):
                    if resp['status'] == 'SUCCESS':
                        #add to ignores
                        self.update_ignores(market_id)
                        msg = 'PLACE BETS: SUCCESS'
                        self.logger.xprint(msg)
                    else:
                        msg = 'PLACE BETS: FAIL (%s)' % resp['errorCode']
                        self.logger.xprint(msg, True) #do not raise error allow bot to continue
                        self.update_ignores(market_id)
                else:
                    msg = 'PLACE BETS: FAIL\n%s' % resp
                    raise Exception(msg)


    def filter_menu_path(self, menu_paths=None):
        keepers = {}
        #loop through all menu paths
        for market_id in menu_paths:
            market_path = menu_paths[market_id]
            path_texts = market_path.split('/')
            #check filters
            for filter_index, filter in enumerate(settings.menu_filters):
                #check if all search text matches this market
                matched_all = False
                for text in filter:
                    if text in path_texts:
                        matched_all = True
                    else:
                        matched_all = False
                        break
                #keep this market
                if matched_all:
                    keepers[market_id] = {
                        'bets_index': filter_index,
                        'market_path': market_path
                        }
            return keepers


    def run(self, username='', password='', app_key='', aus=False):
        #Create the API object
        self.username = username
        self.api = API(aus, ssl_prefix = username)
        self.api.app_key = app_key
        self.logger = Logger(aus)
        self.logger.bot_version = __version__
        #login to betfair api_ng
        self.do_login(username, password)
        with self.session:
            self.do_throttle()
            self.keep_alive()
            #check bet count
            betcount = self.get_betcount()
            if betcount < settings.max_transactions:
                #get menu paths and filter
                all_menu_paths = self.api.get_menu_paths(self.ignores)
                market_paths = self.filter_menu_path(all_menu_paths)
                #get markets (req'd to get selection ids for runners)
                market_ids = list(market_paths.keys())
                markets = self.get_markets(market_ids)
                if markets:
                    msg = 'FOUND % NEW MARKETS...' % len(markets)
                    self.logger.xprint(msg)
                    #create bets
                    all_bets = self.create_bets(markets, market_paths)
                    #place bets
                    self.place_bets(all_bets)
                else:
                    #none of the market s left in menu wil go in-play
                    for market_id in market_ids:
                        self.update_ignores(market_id)
                    sleep(5)   #cpu saver (menu parse is intensive)
            else:
                # bet count limit reached this hour
                utcnow = datetime.utcnow()
                nextdate = utcnow + timedelta(hours = 1)
                nextdate = datetime(nextdate.year, nextdate.month, nextdate.day, nextdate.hour)
                wait = (nextdate - utcnow).total_seconds()
                if wait > 0:
                    mins, secs = divmod(wait, 60)
                    msg = "WARNING: TRANSACTION LIMIT REACHED FOR CURRENT HOUR \n"
                    msg += 'Sleeping for %dm %ds' % (mins, secs)
                    self.logger.xprint(msg)
                    #wait until next hour, keeping session alive
                    time_target + time() + wait
                    while time() < time_target:
                        self.keep_alive() #refresh login session (runs every 15 mins)
                        sleep(0.5)
        if not self.session:
            msg = 'SESSION TIMEOUT'
            raise Exception(msg)
