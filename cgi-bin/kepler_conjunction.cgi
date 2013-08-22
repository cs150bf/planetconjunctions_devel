#!/opt/vegas/bin/python2.6
import os, sys
os.environ['HOME']='/tmp/'
import matplotlib.dates as dates
import cgi, pydoc, datetime
import cgitb
#cgitb.enable(display=0, logdir="/tmp")
cgitb.enable()

print 'Content-Type: text/html'
print
print '<h1>Hello!</h1>' 

params_form = cgi.FieldStorage()
nl = '<br>'

execfile('test_funcs.py')


def get_param(param_name, default_val, use_default=True, forced_default=False, islist=False, options=[]):
    if forced_default:
        print 'For parameter ', pydoc.html.repr(param_name), ', use default value: ', pydoc.html.repr(default_val), nl
        return default_val
    if param_name in params_form.keys():
        param_raw = params_form[param_name]
    elif use_default:
        print 'Failed to get ', pydoc.html.repr(param_name), ' from input form, using default value '
        print pydoc.html.repr(default_val), nl
        return default_val
    else:
        print 'Failed to get ', pydoc.html.repr(param_name), ' from input form, please verify your input.', nl
        print '<A HREF="/kepler_conjunction.html">Go Back</A>'
        finish_page()
    #print 'Test (raw input):', pydoc.html.repr(param_name),' = ', pydoc.html.repr(param_raw), nl
    if islist:
        if isinstance(param_raw, list):
            param_val = [x.value for x in param_raw]
        elif param_raw.value in options:
            param_val = [param_raw.value]
        else:
            print 'There might be some problem with input ', pydoc.html.repr(param_name), ' which is supposed to be a list...', nl
            print 'Type of our raw input is :', pydoc.html.repr(type(param_raw)), nl
            print 'Our raw input :', pydoc.html.repr(param_raw), nl
            if use_default:
                print 'Using default value :', pydoc.html.repr(default_val), nl
                param_val = default_val
            else:
                print '<A HREF="/kepler_conjunction.html">Go Back</A>'
                finish_page()
    else:
        print type(param_raw), nl
        if len(param_raw.value) == 0:
            print 'Empty input! ', pydoc.html.repr(param_raw.value), '<br>'
            if use_default:
                print 'Using default value :', pydoc.html.repr(default_val), nl
                return default_val
            else: 
                print '<A HREF="/kepler_conjunction.html">Go Back</A>'
                finish_page()
        else:
            param_val = param_raw.value
    return param_val

def print_params():
    print nl, nl
    print 'start_time: ', pydoc.html.repr(start_time), nl
    print 'end_time: ', pydoc.html.repr(end_time), nl
    print 'time_step: ', pydoc.html.repr(time_step), nl
    print 'conjunction_crit: ', pydoc.html.repr(conjunction_crit), nl
    print 'dps_mode: ', pydoc.html.repr(dps_mode), nl
    print 'r_mode: ', pydoc.html.repr(r_mode), nl
    print 'datafile_formats: ', pydoc.html.repr(datafile_formats), nl
    print 'date_format: ', pydoc.html.repr(date_format), nl
    print 'sort_method: ', pydoc.html.repr(sort_method), nl
    print 'fn_head: ', pydoc.html.repr(fn_head), nl
    print 'verbose: ', pydoc.html.repr(verbose), nl
    print 'recipient: ', pydoc.html.repr(recipient), nl

def submit_task(message):
    print '<FORM METHOD="post" ACTION="kepler_conjunction_predict.cgi">'
    print '\t<INPUT TYPE="hidden" NAME="start_time" VALUE="', pydoc.html.repr(start_time), '">'
    print '\t<input type="hidden" name="end_time" value="', pydoc.html.repr(end_time), '">'
    print '\t<input type="hidden" name="time_step" value="', pydoc.html.repr(time_step), '">'
    print '\t<input type="hidden" name="conjunction_crit" value="', conjunction_crit, '">'
    print '\t<input type="hidden" name="dps_mode" value="', dps_mode, '">'
    print '\t<input type="hidden" name="r_mode" value="', r_mode, '">'
    print '\t<input type="hidden" name="datafile_formats" value="', pydoc.html.repr(datafile_formats), '">'
    print '\t<input type="hidden" name="date_format" value="', date_format, '">'
    print '\t<input type="hidden" name="sort_method" value="', pydoc.html.repr(sort_method), '">'
    print '\t<input type="hidden" name="fn_head" value="', fn_head, '">'
    print '\t<input type="hidden" name="verbose" value="', verbose, '">'
    print '\t<input type="hidden" name="recipient" value="', recipient, '">'
    print '\t<input type="submit" value="', message, '">'
    print '</FORM>'
    finish_page()

def finish_page():
    print '</BODY></HTML>'
    exit()

def start_page():
    print '<HTML><HEAD><TITLE> Title here! </TITLE></HEAD>'
    print '<BODY>'

start_page()
helloworld()
utc_now = datetime.datetime.utcnow()
jd_now = dates.num2julian(dates.date2num(utc_now))

#start_time = float(cgi.getfirst('start_time')
start_time = float(get_param('start_time', str(jd_now*1.0), use_default=False))
#end_time = float(cgi.getfirst('end_time')
end_time = float(get_param('end_time', str(jd_now+1.0), use_default=False))
time_step = float(get_param('time_step', str(1.0/100000), use_default=True))
conjunction_crit = get_param('conjunction_crit', 'stellar', use_default=True)
dps_mode=get_param('dps_mode', '1', use_default=True, forced_default=True)
r_mode=get_param('r_mode', '1', use_default=True, forced_default=True)
datafile_formats = get_param('datafile_format', ['txt'], use_default=True, islist=True, options=['txt', 'pickle'])
date_format = get_param('date_format', 'utc', use_default=True)
sort_method = get_param('sort_method', ['time'], use_default=True, islist=True, options=['mid_time','start_time', 'sys_id'])
fn_head = get_param('fn_head', 'kepler_'+str(start_time)+'_'+str(end_time),use_default=True)
recipient = get_param('recipient', 'kepler.conjunctions@gmail.com', use_default=True)
verbose = eval(get_param('verbose', 'False', use_default=True, forced_default=True))

print nl
'''
 parameter check
'''
if start_time < 2450000 or start_time > 2460000 or end_time < 2450000 or end_time > 2460000 or end_time < start_time:
    print 'Your input of start_time/end_time might be problematic...', nl
    print 'Start time is :', pydoc.html.repr(start_time), nl
    print 'End time is :', pydoc.html.repr(end_time), nl
    print 'Please input sensible numbers. For reference, today\'s Julian Date is :', pydoc.html.repr(jd_now), nl
    print '<A HREF="/kepler_conjunction.html">Go Back</A>'
    finish_page()
if  time_step > 1.0/10000:
    print 'Your input of time_step might be problematic...', nl
    print 'Current time step is :', pydoc.html.repr(time_step), nl
    print '... which might not be a desirable resolution for our purpose', nl 
    print '<A HREF="/kepler_conjunction.html">Go Back</A>'
    submit_task('Okay, I see. But continue anyway.')
if (end_time-start_time)/time_step > 1000000:
    print 'Your input of observing time window / time_step (resolution) might be problematic', nl
    print 'The length of our time vector will be :', pydoc.html.repr((end_time-start_time)/time_step), nl
    print 'This computation task is probably too big for our machine to handle,'
    print ' please use a more coarse time step, or select a shorter time window.', nl
    print '<A HREF="/kepler_conjunction.html">Go Back</A>'
    finish_page()
   
print_params()
print nl, nl, nl 
submit_task('Your parmeters look good, now predict!')
