#!/opt/vegas/bin/python2.6
def main():
    datafile=open('/tmp/kepler/log.txt', 'w')
    datafile.write('hey there\n')
    datafile.close()

if __name__=="__main__":
    main()
