def init_list_type(datafile_dir, task_type='submitted'):
    with open(datafile_dir + task_type + '_tasks.pickle', 'w') as pk_file:
        pickle.dump({'n_tasks':0}, pk_file)
    with open(datafile_dir + task_type + '_tasks.txt', 'w') as pk_file:
        pk_file.write('The number of ' + task_type + ' tasks is : 0\n')

def clean_list(datafile_dir):
    init_list_type(datafile_dir, 'submitted')
    init_list_type(datafile_dir, 'completed')

