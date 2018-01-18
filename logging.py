
import json
import datetime
import time
import pytz

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

    def get_timestamp(self):
        returnValue = {}
        returnValue['_UTC'] = datetime.datetime.now(tz=pytz.utc)
        returnValue['_EPOCH'] = returnValue['_UTC'].timestamp()

        return returnValue

    def get_epoch(self, timestamp):
        return get_timestamp.timestamp()

    def set_startday(self):
        global startDay
        global maxPacketLost
        global sumPacketLost

        maxPacketLost = 0
        sumPacketLost = 0
        startDay = datetime.datetime.now().strftime('%Y-%m-%d')

        return

    def get_startday(self):
        global startDay

        return startDay

    def print_log(self, status, sleeptimer):

        global sumPacketLost
        global maxPacketLost

        # Reset maxPacketLost on new day
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if today != logdata.get_startday(self):
            maxPacketLost = 0
        print(status['_TIMESTAMP'] + '\n')
        print ('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('CURRENT BSSID:', status['_BSSID'], '', 'LAST BSSID:', status['_LAST_BSSID']))
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('SSID:', status['_SSID'], '', 'NOISE:', status['_NOISE']))
        if status['_ROAM'] == 'TRUE':
            print('{:<15} {:>20} {:>10} {:<15} {:>25} {:>3}'.format('RSSI:', status['_RSSI'], '', 'ROAM:\033[92m', status['_ROAM'], '\033[0m'))
        else:
            print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('RSSI:', status['_RSSI'], '', 'ROAM:', status['_ROAM']))
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('LAST ROAM AT:', status['_LAST_ROAM_AT'], '', 'TX SPEED:', status['_TRANSMITRATE']))
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('LAST ROAM TO:', status['_LAST_ROAM_TO'], '', 'TX SPEED:', status['_TRANSMITRATE']))
        if status['_PACKETLOSS'] == 'TRUE':
            status['_LOSS_COUNT'] = 1
            sumPacketLost += 1
            if sumPacketLost > maxPacketLost:
                maxPacketLost = sumPacketLost
            print('{:<15} {:>20} {:>10} {:<15} {:>23} {:>3}'.format('CHANNEL:', status['_CHANNEL'], '', 'PACKET LOST:\033[91m', status['_PACKETLOSS'], '\033[0m'))
            print('{:<15} {:>20} {:>10} {:<15} {:>17}'.format('RTT:', status['_RTT'], '', 'MAX LOST LAST 24H:', maxPacketLost))
        else:
            status['_LOSS_COUNT'] = 0
            sumPacketLost = 0
            print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('CHANNEL:', status['_CHANNEL'], '', 'PACKET LOST:', status['_PACKETLOSS']))
            print('{:<15} {:>20} {:>10} {:<15} {:>17}'.format('RTT:', status['_RTT'], '', 'MAX LOST LAST 24H:', maxPacketLost))
        # No idea how to parse the return values :(
        # if roamingLimit >= int(status['_RSSI']):
        #    cachedResults = wifi.get_cachedscanresults()

        print('------------------------------------------------------------------------------------')
        time.sleep(sleeptimer)

        return status

