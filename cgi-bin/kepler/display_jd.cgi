#!/opt/vegas/bin/python2.6
import os, sys
os.environ['HOME']='/tmp/'
import matplotlib.dates as dates
import cgi, pydoc, datetime

current_time = datetime.datetime.utcnow()
current_time_num = dates.date2num(current_time)
current_jd = dates.num2julian(current_time_num)

print 'var jd_date = "hellow world"; var utc_date = "Great!";'
#return 'var jd_date = "hello world";'
#return 'var jd_date = '+str(current_jd)+'; var utc_date = '+str(current_time)+';'
