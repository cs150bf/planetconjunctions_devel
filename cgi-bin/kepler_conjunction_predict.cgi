#!/opt/vegas/bin/python2.6
import os, sys, subprocess, time
#os.environ['HOME']='/tmp/'
os.environ['MPLCONFIGDIR']='/tmp/'
import matplotlib.dates as dates
import cgi, pydoc, datetime, string, pickle
import cgitb
#cgitb.enable(display=0, logdir="/tmp")
cgitb.enable()

print 'Content-Type: text/html'
print
print '<h1>Hello!</h1>'

params_form = cgi.FieldStorage()
nl = '<br>'

#execfile('test_funcs.py')
fromaddrs = 'kepler.conjunctions@gmail.com'
username = 'kepler.conjunctions'
password = 'kepler.planets.conjunctions'

execfile('./kepler/emailresults.py')
execfile('kepler_conjunction_web_funcs.py')
execfile('./kepler/conj_funcs.py')
execfile('./kepler/auto_conjunction.py')
execfile('./kepler/planet_conj.py')
execfile('./kepler/conj_stats_funcs.py')
execfile('./kepler/conj_stats.py')
execfile('./kepler/planet_categorize.py')
execfile('./kepler/planet_d_r_comparison.py')

def print_params():
    print nl, nl
    print 'start_time: ', pydoc.html.repr(start_time), nl
    print 'end_time: ', pydoc.html.repr(end_time), nl
    print 'time_step: ', pydoc.html.repr(time_step), nl
    print 'conjunction_crit: ', pydoc.html.repr(conjunction_crit), nl
    print 'dps_mode: ', pydoc.html.repr(dps_mode), nl #, 'dps_mode == \'1\'?', dps_mode=='1', nl
    print 'r_mode: ', pydoc.html.repr(r_mode), nl
    print 'datafile_formats: ', pydoc.html.repr(datafile_formats), nl
    print 'date_format: ', pydoc.html.repr(date_format), nl
    print 'sort_method: ', pydoc.html.repr(sort_method), nl
    print 'fn_head: ', pydoc.html.repr(fn_head), nl
    print 'verbose: ', pydoc.html.repr(verbose), nl
    print 'recipient: ', pydoc.html.repr(recipient), nl

def cleanup(messystr):
    return string.replace(messystr, ' ', '')

def update_tasks_list(submitted_task_id='', task_type='submitted'):
    """
    submitted_tasks.pickle=
			{'n_tasks': INTEGER,
			 'task_1': {'type':submitted, 
					'event_time': <time>, 
					'fn_head': STRING, 
					'start_time': FLOAT, ...
					},
			 'task_2': {}, ...
    """
    event_time = str(datetime.datetime.utcnow())
    #with open('count_'+task_type+'.txt', 'r+') as count_file:
    #    n_task_count = int(count_file.readline())
    with open(datafile_dir + task_type + '_tasks.pickle', 'r') as tasks_pickle:
        tasks_dict = pickle.load(tasks_pickle)
    new_task, tasks_dict = update_task_dict(tasks_dict, event_time, submitted_task_id, task_type=task_type)
    with open(datafile_dir + task_type + '_tasks.pickle', 'w') as tasks_pickle:
        pickle.dump(tasks_dict, tasks_pickle)
    with open(datafile_dir + task_type + '_tasks.txt', 'r+') as tasks_txt:
        old = tasks_txt.read()
	old_2line_on = old[old.find('\n')+1:]
        tasks_txt.seek(0)
        newline = 'The number of ' + task_type + ' tasks is : ' + str(tasks_dict['n_tasks']) + '\n'
        tasks_txt.write(newline + old_2line_on)
    with open(datafile_dir + task_type + '_tasks.txt', 'a+b') as tasks_txt:
        new_text = update_tasks_txt(new_task, tasks_txt, task_type)
    return new_task['task_id'], new_text 
 
def update_task_dict(tasks_dict, event_time, submitted_task_id='', task_type='submitted'):
    n_tasks = tasks_dict['n_tasks']
    if task_type == 'submitted':
        new_task_id = 'task_'+str(n_tasks+1)
    else:
        new_task_id = submitted_task_id
    tasks_dict['n_tasks'] = n_tasks+1
    new_task = {'task_id':new_task_id, 'type': task_type,  'event_time':event_time}
    new_task['start_time'] = start_time
    new_task['end_time'] = end_time
    new_task['time_step'] = time_step
    new_task['conjunction_crit'] = conjunction_crit
    new_task['dps_mode'] = dps_mode
    new_task['r_mode'] = r_mode
    new_task['datafile_formats'] = datafile_formats
    new_task['date_format'] = date_format
    new_task['sort_method'] = sort_method
    new_task['fn_head'] = fn_head
    new_task['verbose'] = verbose
    if recipient:
        new_task['recipient']=[recipient,fromaddrs] 
    else:
        new_task['recipient']=fromaddrs
    if task_type == 'completed':
        new_task['output_files_dir'] = datafile_dir+fn_head+'*'
        new_task['n_conjunctions'] = n_conjunctions
    tasks_dict[new_task_id] = new_task
    return new_task, tasks_dict
    
def update_tasks_txt(new_task_dict, tasks_txt_file, task_type):
    new_text = ''
    new_text = new_text + '-------------------------------------------------\n'
    new_text = new_text + 'task id: '+new_task_dict['task_id']+'\n'
    new_text = new_text + 'task type: '+new_task_dict['type']+'\n'
    new_text = new_text + task_type+' time: '+new_task_dict['event_time']+'\n'
    listed_keys = ['start_time', 'end_time', 'time_step', \
		 'conjunction_crit', 'dps_mode', 'r_mode', \
		 'datafile_formats', 'date_format', 'sort_method',\
		 'fn_head', 'verbose', 'recipient']
    for key in listed_keys:
        if new_task_dict.has_key(key):
            new_text = new_text + '\t'+key+' : '+str(new_task_dict[key])+'\n'
    if task_type == 'completed':
        new_text = new_text + 'A total number of '+str(new_task_dict['n_conjunctions'])+' conjunctions have occurred.\n'
        new_text = new_text + 'Output files can be found at: '+new_task_dict['output_files_dir']+'\n'
    new_text = new_text + '-------------------------------------------------\n'
    tasks_txt_file.write(new_text)
    return new_text
 
def finish_page():
    print '</BODY></HTML>'

def start_page():
    print '<HTML><HEAD><TITLE> Title here! </TITLE></HEAD>'
    print '<BODY>'


start_page()
datafile_dir ='/tmp/kepler/'

start_time = float(params_form.getfirst('start_time'))
end_time = float(params_form.getfirst('end_time'))
time_step = float(params_form.getfirst('time_step'))
conjunction_crit = params_form.getfirst('conjunction_crit')
dps_mode = params_form.getfirst('dps_mode')
r_mode = params_form.getfirst('r_mode')
datafile_formats = eval(params_form.getfirst('datafile_formats'))
date_format = params_form.getfirst('date_format')
sort_method = eval(params_form.getfirst('sort_method'))
fn_head = params_form.getfirst('fn_head')
verbose = eval(params_form.getfirst('verbose'))
recipient = params_form.getfirst('recipient')

conjunction_crit = cleanup(conjunction_crit)
dps_mode = cleanup(dps_mode)
r_mode = cleanup(r_mode)
date_format = cleanup(date_format)
fn_head = cleanup(fn_head)
recipient = cleanup(recipient)

print_params()
task_id, newtext = update_tasks_list(task_type='submitted')
#proc = subprocess.Popen(["at", "now", "<<<", "\'python2.6 kepler/auto_conjunction_script.py", \
#			str(start_time),  str(end_time), str(time_step), str(conjunction_crit), \
#			str(datafile_foramts), str(date_format), str(sort_method), str(fn_head), \
#			str(verbose), str(task_id), "\'"], shell=True, stdin=subprocess.PIPE, \
#			stdout=subprocess.PIPE)

#omsg = os.system("touch kepler/touch_test")
#omsg = os.system("python2.6 kepler/test.py")
#omsg = os.system("python2.6 kepler/auto_conjunction_script.py")
#omsg = os.system("at now <<< \'python2.6 /var/www/cgi-bin/kepler/auto_conjunction_script.py "+str(2454900)+"\'")
#omsg = os.system("at now <<< \'python2.6 kepler/auto_conjunction_script.py "+str(start_time)+" "+str(end_time)+\
#	" "+str(time_step)+" "+str(conjunction_crit)+" "+str(datafile_formats)+" "+str(date_format)+" "+\
#	str(sort_method)+" "+str(fn_head)+" "+str(verbose)+" "+str(task_id)+"\'")
#print ot, nl
#os.system("at now <<< 'python2.6 /kepler/auto_conjunction_script.py'")
if recipient:
    emailresults(datafile_dir, [], 'Your submitted task [Kepler]', newtext, fromaddrs, recipient, username, password)
print 'Your task has been successfully submitted, we\'ll now start to process it.', nl
print 'This will take a while, please check back later...', nl
print 'You can find the list of submitted tasks at ', datafile_dir ,'submitted_tasks.txt', nl
print '... and the list of completed tasks at ', datafile_dir ,'completed_tasks.txt', nl
print 'And the result of your completed tasks should also exist in ', datafile_dir ,' and has file names start with your assigned value:', nl
print datafile_dir ,fn_head,'*.*'
print nl
print 'If you chose to get notifications via emails, we\'ve sent you an email about your submitted task.', nl
print 'When your task is completed, we\'ll send you another email with the results attached.', nl
print nl
#print 'The message that we just sent to you is: ', nl
#print pydoc.html.repr(newtext)
print 'If you chose to enable the \'verbose\' feature, you can also find a detailed log file at /tmp/kepler/',fn_head,'_log.txt'
finish_page()



sys.stdout.flush()
os.close(sys.stdout.fileno())
if os.fork():
    sys.exit()

time.sleep(1)
os.setsid()

stdout = sys.stdout
logfilename=datafile_dir+fn_head+'_log.txt'
with open(logfilename, 'w') as sys.stdout:
    n_conjunctions, fns = auto_conjunction(start_time, end_time, time_step, \
		dps_mode, r_mode, conjunction_crit, \
		datafile_formats, date_format, sort_method, \
		datafile_dir, fn_head, verbose)

sys.stdout = stdout

if verbose:
    fns.append(logfilename)
#print 'Task finished!'	
task_id, newtext = update_tasks_list(task_id, task_type='completed')
if recipient:
    emailresults(datafile_dir, fns, 'Your task has been completed! [Kepler]', newtext, fromaddrs, recipient, username, password)
exit()
