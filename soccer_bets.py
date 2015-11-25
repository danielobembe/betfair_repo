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
        if resp = 'SUCCESS':
            self.session = True
        else:
            self.session = False #login failed
            msg = 'api.login() resp = %s' % resp
            raise Exception(msg)

    ''' Refresh login session. Sessions expire after 20 mins
        Betfair throttle = 1 request every 7 mins
    '''
    def keep_alive(self):
        now = time()
        if now > self.throttle['keep_alive']:
            #refresh
            self.session = False
            resp = self.api.keep_alive()
            if resp == 'SUCCESS':
                self.throttle['keep_alive'] = now + (15 * 60) #add 15 mins
                self.session = True
            else:
                self.session = False
                msg = 'api.keep_alive() resp = %s' % resp
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

    def create_bets(self, markets=None, market_paths=None):
        market_bets = {}
        for market in markets:
            market_id = market['marketId']
            if market_id in market_paths:
                bets_index = market_paths[market_id]['bets_index']
                bets = setings.market_bets[bets_index]
                #create bets for this market
                market_path = market_paths[market_id]['market_path']
                market_bets[market_id] = {'bets': [], 'market_path': market_path}
                for runner in market['runners']:
                    for bet in bets:
                        new_bet = {}
                        new_bet['selectionId'] = runner['selectionId']
                        new_bet['side'] = bet['side']
                        new_bet['orderType'] = 'LIMIT'
                        new_bet['limitOrder'] = {
                            'size': bet['stake'],
                            'price': bet['price'],
                            'persistenceType': 'PERSIST'
                            }
                        market_bets[market_id]['bets'].append(new_bet)

        return market_bets

    #Function: Loops through market and places bets
    def place_bets(self, market_bets = None):
        for market_id in market_bets:
            bets = market_bets[market_id]['bets']
            if bets:
                #update and check bet count
                new_betcount = len(bets)
                self.update.betcount(new_betcount)
                betcount = self.get_betcount()#total bets placed in crrnt hr
                if betcount >= setting.max_transactions: return
                market_path = market_bets[market_id]['market_path']
                msg = 'MARKET PATH: %s\n' % market_path
                msg += 'PLACING %s BETS ...\n' % len(bets)
                for i, bet in enumerate(bets):
                    msg += '%s: %s\n' % (i, bet)
                self.logger.xprint(msg)
                self.do_throttle()
                resp = self.api.place_bets(market_id, bets)
                if (type(resp) is dict and 'status' in resp):
                    if resp['status'] == 'SUCCESS':
                        #add to ignores
                        self.update_ignores(market_id)
                        msg = 'PLACE BETS: SUCCESS'
                        self.logger.xprint(msg)
                    else:
                        if resp['errorCode'] == 'INSUFFICIENT_FUNDS':
                            msg = 'PLACE BETS: FAIL (%s)' % resp['errorCode']
                            self.logger.xprint(msg)
                            sleep(180)
                        else:
                            msg = 'PLACE BETS: FAIL (%s)' % resp['errorCode']
                            self.logger.xprint(msg, True)
                            self.update_ignores(market_id)
                else:
                    msg = 'PLACE BETS: FAIL\n%s' % resp
                    raise Exception(msg)
        

    #Function: Returns list of path matching filters specified in settings.py
    def filter_menu_path(self, menu_paths = None):
        #@menu_paths: dict of menu paths
        keepers = {}
        for market_id in menu_paths:
            market_path = menu_paths[market_id]
            path_texts = market_path.split('/')
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
                            'bets_index': filter_index
                            'market_path': market_path
                            }
        return keepers


    def run(self, username='', password='', app_key='', aus= False):
        #create the API object
        self.username = username
        self.api = API(aus, ssl_prefix = username)
        self.api.app_key = app_key
        self.logger = Logger(aus)
        self.logger.bot_version = __version__
        #login to betfair api-ng
        self.do_login(username, password)
        while self.session:
            self.do_throttle()
            self.keep_alive() #refresh login session every 15 mins
            #check bet count
            betcount = self.get_betcount()
            if betcount < settings.max_transactions:
                #get menu path and filter
                all_menu_paths = self.api.get_menu_paths(self.ignores)
                market_paths = self.filter_menu_path(all_menu_paths)
                #get markets (req'd to get selection ids for runners)
                market_ids = list(market_paths.keys())
                markets = self.get_markets(market_ids) #max size = 1000
                if markets:
                    msg = 'FOUND %S NEW MARKETS ...' % len(markets)
                    self.logger.xprint(msg)
                    # create bets
                    all_bets = self.create_bets(markets, market_paths)
                    #place bets
                    self.place_bets(all_bets)
                else:
                    # bet count limit reached for this hour
                    utcnow = datetime.utcnow()
                    nextdate = utcnow + timedelta(hours=1)
                    nextdate = datetime(nextdate.year, nextdate.month, nextdate.day, nextdate.hour)
                    wait = (nextdate - utcnow).total_seconds()
                    if wait > 0:
                        mins, secs = divmod(wait, 60)
                        msg = 'WARNING: TRANSACTION LIMIT REACHED FOR CURRENT HOUR\n'
                        msg += 'Sleeping for %dm %ds' % (mins, secs)
                        self.logger.xprint(msg)
                        #wait until next hour, keeping session alive
                        time_target = time() + wait
                        while time() < time_target:
                            self.keep_alive() #refresh login sessuib (runs every 15 mins)
                            sleep(0.5) #CPU saver!
                if not self.session:
                    msg = 'SESSION TIMEOUT'
                    raise Exception(msg)
    
#Testing Object Initialization




