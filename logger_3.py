import os
from datetime import datetime

class Logger(object):
"""Prints info to terminal and saves to a log file"""
    def __init__(self, aus = False):
        self.prefix = '[UK]'
        if aus: self.prefix = '[AUS]'
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.log_path = self.abs_path + '/log.txt'
        self.err_path = self.abs_path + '/err_lot.txt'
        self.max_logs = 5000       #Max no. of data entries
        self.bot_version = None    #set extrnally e.gself.logger.bot_.ve.. =1

    def xprint(self, data='', err = False):
        if data:
            #set file path
            fpath = self.log_path
            if err: fpath = self.err_path
            #build data string
            data = str(data)
            str_date = datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S.%f GMT')
            div = '%s\n' % ('-' * 40)
            bot_version = 'Bot version: %s' % self.bot_version
            temp = '%s %s\n' % (self.prefix, str_date)
            temp += '%s\n' % bot_version
            temp += '%s\n' % data
            temp += div
            #check if log file exists
            if os.path.exists(fpath):
                #read file + append new data
                fd = open(fpath, 'r').read() + temp
                #check data length
                while fd.count(div) > self.max_logs:
                    #remove first (oldest) entry
                    fd = fd.partition(div)[2]
                #write new file data
                open(fpath, 'w').write(fd)
                else:
                    #create new path
                    open(fpath, 'w').write(temp)
                #print to terminal
                try: #required for when remote terminal is closed
                    print(temp)
                except:
                    pass
