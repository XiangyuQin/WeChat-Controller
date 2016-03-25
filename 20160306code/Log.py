# -*- coding: UTF-8 -*-

import datetime
import common
import logging
import config
from logging.handlers import RotatingFileHandler

class Log(object):
    def __init__(self, dt):
        now = common.datetime_toStringYMDHMS(dt)
        app_name = config.logSrc+'%s.log' %(now)
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=app_name,
                filemode='w')
        Rthandler = RotatingFileHandler(app_name, maxBytes=config.logMaxBytes, backupCount=config.logBackupCount)
        Rthandler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        Rthandler.setFormatter(formatter)
        logging.getLogger('').addHandler(Rthandler)
        
    def printDebug(self, str):
            logging.debug(str)
    
    def printInfo(self, str):
            logging.info(str)
            
    def printWarning(self, str):
            logging.warning(str)
            
    def printError(self, str):
            logging.error(str)

    def test(self):
        for i in range(1, 10):
            logging.debug('This is debug message')
            logging.info('This is info message')
            logging.warning('This is warning message')
    

            
 
            
if __name__ == '__main__':
    log=Log()
    log.test()
