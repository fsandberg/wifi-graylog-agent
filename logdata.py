
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
        returnValue['UTC'] = datetime.datetime.now(tz=pytz.utc)
        returnValue['epoch'] = returnValue['UTC'].timestamp()

        return returnValue

  #  def get_epoch(self, timestamp):
  #      return get_timestamp.timestamp()

    def set_startday(self):
        global startDay
        global maxPacketLost
        global sumPacketLost

        maxPacketLost = 0
        sumPacketLost = 0
        startDay = datetime.datetime.now().strftime('%Y-%m-%d')

        return
    def get_time(self):
        time_now = datetime.datetime.now().strftime('%H:%M:%S')

        return time_now

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
        #print(status['timestamp'] + '\n')
        print ('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('CURRENT BSSID:', status['BSSID'], '', 'LAST BSSID:', status['last BSSID']))
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('SSID:', status['SSID'], '', 'ROAM TIME:', status['roam time']))
        if status['roam'] == 'TRUE':
            print('{:<15} {:>20} {:>10} {:<15} {:>25} {:>3}'.format('CURRENT RSSI:', status['RSSI'], '', 'ROAM:\033[92m', status['roam'], '\033[0m'))
        else:
            print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('CURRENT RSSI:', status['RSSI'], '', 'ROAM NOW:', status['roam']))
        print('{:<15} {:>19} {:>10} {:<15} {:>17}'.format('CURRENT CHANNEL:', status['channel'], '', 'LAST ROAM AT RSSI:', status['last roam at']))
        print('{:<15} {:>20} {:>10} {:<15} {:>17}'.format('CURRENT NOISE:', status['noise'], '', 'LAST ROAM TO RSSI:', status['last roam to']))
        if status['packetloss'] == 'TRUE':
            status['loss count'] = 1
            sumPacketLost += 1
            if sumPacketLost > maxPacketLost:
                maxPacketLost = sumPacketLost
            print('{:<15} {:>20} {:>10} {:<15} {:>23} {:>3}'.format('TX RATE:', status['transmitrate'], '', 'PACKET LOST:\033[91m', status['packetloss'], '\033[0m'))
            print('{:<15} {:>20} {:>10} {:<15} {:>16}'.format('RTT:', status['RTT'], '', 'MAX PKT LOST (24H):', maxPacketLost))
        else:
            status['loss count'] = 0
            sumPacketLost = 0
            print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('TX RATE:', status['transmitrate'], '', 'PACKET LOST:', status['packetloss']))
            print('{:<15} {:>20} {:>10} {:<15} {:>16}'.format('RTT:', status['RTT'], '', 'MAX PKT LOST (24H):', maxPacketLost))

        print('------------------------------------------------------------------------------------')
        #time.sleep(sleeptimer)

        return status

