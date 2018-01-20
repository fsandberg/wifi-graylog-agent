
import json
import datetime
import netifaces
import pytz
import re
import uuid
from GELF import GELF
import configreader

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

    def set_startvalues(self):
        logdata = {}
        logdata['maxpacketlost'] = 0
        logdata['sumpacketlost'] = 0
        logdata['startday'] = datetime.datetime.now().strftime('%Y-%m-%d')

        logdata['last_BSSID'] = ''
        logdata['last_roam_at'] = ''
        logdata['last_roam_to'] = ''
        logdata['roam_time'] = ''
        logdata['clientmac'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        #gateways = netifaces.gateways()
        #logdata['defaultgateway'] = gateways['default']



        return logdata

    def get_time(self):
        time_now = datetime.datetime.now().strftime('%H:%M:%S')

        return time_now

    def process_logdata(self, logdata):

        logdata['short_message'] = ''

        if logdata['packetloss'] == 'TRUE':
            logdata['short_message'] = 'LOST PACKET, TOTAL ' + str(logdata['sumpacketlost']) + ' '
            logdata['packetlosscount'] = 1
            logdata['sumpacketlost'] += 1
            if logdata['sumpacketlost'] > logdata['maxpacketlost']:
                logdata['maxpacketlost'] = logdata['sumpacketlost']
        if logdata['packetloss'] == 'FALSE':
            logdata['packetlosscount'] = 0
            logdata['sumpacketlost'] = 0
        if logdata['roam'] == 'TRUE':
            logdata['short_message'] = logdata['short_message'] + 'ROAMED FROM ' + logdata['last_BSSID'] + ' TO ' + logdata['BSSID'] + ' '
        if logdata['SSID'] == None:
            logdata['short_message'] = 'CLIENT DISCONNECTED '

        if logdata['short_message'] == '':
            logdata['short_message'] = '-'




        # Reset maxPacketLost on new day
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if today != logdata['startday']:
            logdata['maxpacketlost'] = 0

        timenow = datetime.datetime.now(tz=pytz.utc)
        logdata['timestamp'] = timenow.timestamp()

        return logdata

    def print_log(self, status, sleeptimer):

        print(status['timestamp'])
        print('')
        print ('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('CURRENT BSSID:', status['BSSID'], '', 'LAST BSSID:', status['last_BSSID']))
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('SSID:', status['SSID'], '', 'ROAM TIME:', status['roam_time']))
        if status['roam'] == 'TRUE':
            print('{:<15} {:>20} {:>10} {:<15} {:>25} {:>3}'.format('CURRENT RSSI:', status['RSSI'], '', 'ROAM:\033[92m', status['roam'], '\033[0m'))
        else:
            print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('CURRENT RSSI:', status['RSSI'], '', 'ROAM NOW:', status['roam']))
        print('{:<15} {:>19} {:>10} {:<15} {:>17}'.format('CURRENT CHANNEL:', status['channel'], '', 'LAST ROAM AT RSSI:', status['last_roam_at']))
        print('{:<15} {:>20} {:>10} {:<15} {:>17}'.format('CURRENT NOISE:', status['noise'], '', 'LAST ROAM TO RSSI:', status['last_roam_to']))
        if status['packetloss'] == 'TRUE':
            print('{:<15} {:>20} {:>10} {:<15} {:>23} {:>3}'.format('TX RATE:', status['transmitrate'], '', 'PACKET LOST:\033[91m', status['packetloss'], '\033[0m'))
            print('{:<15} {:>20} {:>10} {:<15} {:>16}'.format('RTT:', status['RTT'], '', 'MAX PKT LOST (24H):', status['maxpacketlost']))
        else:
            print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('TX RATE:', status['transmitrate'], '', 'PACKET LOST:', status['packetloss']))
            print('{:<15} {:>20} {:>10} {:<15} {:>16}'.format('RTT:', status['RTT'], '', 'MAX PKT LOST (24H):', status['maxpacketlost']))

        #print(status['gateway'])
        print('------------------------------------------------------------------------------------')

        return status



