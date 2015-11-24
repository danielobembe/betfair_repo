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

class SoccerBot(object):
    """Maps soccer market relationships"""
    def __init__(self):
        self.username= ''  
        self.loggr = None  
        self.api = None
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.ignores_path = '%s/ignores.pkl' % self.abs_path
        self.ignores = self.unpickle_data(self.ignores_path,[]) #whatitdo?
        self.betcount_path = '%s/betcount.pkl' % self.abs_path
        self.betcount = self.unpickle_data(self.betcount_path,{})#{hrs,Mkt_id}
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
