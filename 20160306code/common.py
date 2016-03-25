# -*- coding: UTF-8 -*-
import datetime
import time
def datetime_toString(dt):
    return dt.strftime("%Y-%m-%d")
    
def datetime_toStringYMDHMS(dt):
    return dt.strftime("%Y%m%d%H%M%S")
        
def string_toDatetime(str):
    return time.strptime(str, "%Y-%m-%d")
 
def date_toTimestamp(dt):
    time_tuple = dt.timetuple()
    ts = time.mktime(time_tuple)
    return ts

def timestamp_toDate(ts):
    time_tuple = time.localtime(ts)
    dt= datetime.datetime(*time_tuple[0:6])
    return dt

def mergeDict(dict1, dict2):
    dictMerged=dict1.copy()
    dictMerged.update(dict2)
    return dictMerged

if __name__ == '__main__':

    print timestamp_toDate(1456279680.0)
    '''
    print date_toTimestamp(datetime.datetime.now())
    '''