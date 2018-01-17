
import json

class logdata(object):
    ''' Check connection'''

    def send_log(self, logfile):
        with open(logfile, 'r') as readlog:
            data = readlog.read().splitlines(True)
        # connect to logserver to send line

        # if connection to logserver is successful, run code below to delete transmitted line
        with open(logfile, 'w') as writelog:
            writelog.writelines(data[1:])

        return

    def write_log(self, logfile, data):

        with open(logfile, 'a') as appendlog:
            statusdata = json.dumps(data)
            appendlog.writelines(statusdata)
            appendlog.writelines('\n')

        return