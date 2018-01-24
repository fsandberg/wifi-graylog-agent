from connectivity import ConnectionCheck
#from gelf import GelfConnector
from logstash import LogstashConnector
from osxwifi import WifiStatus
from pathlib import Path
from functools import reduce
import os
import json
import datetime
import pytz
import threading
#import netifaces
#import re
#import uuid


class LogProcessing(object):

    def send_log_old(self, logfile, loghost, logport):
        with open(logfile, 'r') as readlog:

            line_content = readlog.read().splitlines(True)

            if ConnectionCheck().check_connection(loghost, logport, 0.200):
                counter = 0
                for lines in line_content:
                    counter = counter + 1
                    log_data_json = json.loads(lines)
                    #GelfConnector().log_tcp(log_data_json, loghost, logport)
                    LogstashConnector().log_tcp(log_data_json, loghost, logport)
                threading._start_new_thread(LogProcessing.rewrite_log, (self, logfile, line_content, counter))
            else:
                print('\033[91mNO CONNECTION TO LOGSERVER ' + loghost + ':' + logport + '\033[0m')

        return

    def send_log(self, logdata, loghost, logport):

        # Check connection to logserver
        if ConnectionCheck().check_connection(loghost, logport, 0.200):
            # Check if cache file exists
            cachefile = Path('CACHE')
            if cachefile.is_file():
                # Start a new thread and send cached log
                threading._start_new_thread(self.send_cache, (loghost, logport))

            # Send dict to logstash function
            LogstashConnector().log_tcp(logdata, loghost, logport)

        else:
            # Write logs to cache file
            self.write_log('CACHE', logdata)
            print('\033[91mNo connection to logserver ' + loghost + ':' + logport + '\033[0m')

        return

    def send_cache(self, loghost, logport):
        # Loop through CACHE file and send to logstash
        with open('CACHE', 'r') as cache:
            for lines in cache:
                log_data_json = json.loads(lines)
                LogstashConnector().log_tcp(log_data_json, loghost, logport)
        # Remove CACHE file
        os.remove('CACHE')

    def rewrite_log(self, logfile, logdata, count):
        with open(logfile, 'w') as writelog:
            writelog.writelines(logdata[count:])

        return

    def write_log(self, logfile, logdata):
        with open(logfile, 'a') as appendlog:
            logdata = json.dumps(logdata)
            appendlog.writelines(logdata)
            appendlog.writelines('\n')

        return

    def get_timestamp(self):
        timestamp = datetime.datetime.now(tz=pytz.utc)
        timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (timestamp.microsecond / 1000) + "Z"

        return timestamp

    def set_startvalues(self):
        global tempBSSID
        global tempRSSI
        global tempChannel
        global tempPacketLossTotal
        global tempPacketLossMax

        tempBSSID = None
        tempRSSI = None
        tempChannel = None
        tempPacketLossTotal = 0
        tempPacketLossMax = 0

        # initiate dicts
        logdata = {}
        logdata['wireless'] = {}
        logdata['connection'] = {}
        # set default dict values
        logdata['@message'] = ''
        logdata['startday'] = self.get_day()
        logdata['wireless']['roam from RSSI'] = 0

        #logdata['last_BSSID'] = '--'
        #logdata['last_roam_at'] = '--'
        #logdata['last_roam_to'] = '--'
        #logdata['roam_time'] = '--'
        #logdata['clientmac'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

        #gateways = netifaces.gateways()
        #logdata['defaultgateway'] = gateways['default']

        return logdata

    def get_day(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def get_time(self):
        return datetime.datetime.now().strftime('%H:%m:%S')

    def process_logdata(self, logdata):
        logdata['short_message'] = ''
        logdata['roamcount'] = 0

        if logdata['packetloss'] == 'TRUE':
            logdata['packetlosscount'] = 1
            logdata['sumpacketlost'] += 1
            logdata['short_message'] = 'LOST PACKET, TOTAL ' + str(logdata['sumpacketlost']) + ' '

            if logdata['sumpacketlost'] > logdata['maxpacketlost']:
                logdata['maxpacketlost'] = logdata['sumpacketlost']

        if logdata['packetloss'] == 'FALSE':
            logdata['packetlosscount'] = 0
            logdata['sumpacketlost'] = 0

        if logdata['roam'] == 'TRUE':
            logdata['roamcount'] = 1
            logdata['short_message'] = logdata['short_message'] + 'ROAMED FROM ' + logdata['last_BSSID'] + ' TO ' + logdata['BSSID'] + ' '

        if logdata['SSID'] == 'None':
            logdata['short_message'] = logdata['short_message'] + 'CLIENT IS NOT CONNECTED!'

        if logdata['short_message'] == '':
            logdata['short_message'] = '-'

        # Reset maxPacketLost on new day
        today = datetime.datetime.now().strftime('%Y-%m-%d')

        if today != logdata['startday']:
            logdata['maxpacketlost'] = 0

        #timenow = datetime.datetime.now(tz=pytz.utc)

        logdata['@timestamp'] = self.get_timestamp()

        return logdata

    def analyze_data(self, logdata):

        # set timestamp
        logdata['@timestamp'] = self.get_timestamp()

        # -------------------------------------------------------------------------------------
        # Analyze wifi data
        # -------------------------------------------------------------------------------------
        global tempBSSID
        global tempRSSI
        global tempChannel
        global tempPacketLossTotal
        global tempPacketLossMax

        # fixup value from None to 0
        if tempRSSI is None:
            tempRSSI = 0
        if tempChannel is None:
            tempChannel = 0

        # fixup value from None to 'None'
        if tempBSSID is None:
            tempBSSID = 'None'

        # reset tempPacketLossMax every new day
        if self.get_day() != logdata['startday']:
            tempPacketLossMax = 0

        if tempBSSID == logdata['wireless']['BSSID']:
            # no roam, write BSSID, RSSI and channel to temporary values
            tempBSSID = logdata['wireless']['BSSID']
            tempRSSI = logdata['wireless']['RSSI']
            tempChannel = logdata['wireless']['channel']
            logdata['wireless']['roam'] = 0

            # normal packet, set message to nothing
            logdata['@message'] = ''
        else:
            # client has roamed
            logdata['wireless']['roam'] = {}
            logdata['wireless']['roam'] = 1
            logdata['wireless']['roam from BSSID'] = tempBSSID
            logdata['wireless']['roam from RSSI'] = tempRSSI
            logdata['wireless']['roam from channel'] = tempChannel
            logdata['wireless']['roam to BSSID'] = logdata['wireless']['BSSID']
            logdata['wireless']['roam to RSSI'] = logdata['wireless']['RSSI']
            logdata['wireless']['roam to channel'] = logdata['wireless']['channel']
            logdata['wireless']['roam timestamp'] = self.get_time()
            logdata['@message'] = 'Client roamed from' \
                + ' ' + str(logdata['wireless']['roam from BSSID'])\
                + ' (' + str(logdata['wireless']['roam from RSSI']) + ')' \
                + ' to ' + str(logdata['wireless']['roam to BSSID']) \
                + ' (' + str(logdata['wireless']['roam to RSSI']) + ')'

            # reset tempvalues
            tempBSSID = logdata['wireless']['BSSID']
            tempRSSI = logdata['wireless']['RSSI']
            tempChannel = logdata['wireless']['channel']

        # -------------------------------------------------------------------------------------
        # Analyze connection data
        # -------------------------------------------------------------------------------------
        # Check packetloss
        if logdata['connection']['packetloss'] == 1:
            # Packet to testserver is lost, increment or create total counters
            tempPacketLossTotal = tempPacketLossTotal + 1
            logdata['connection']['total lost'] = tempPacketLossTotal
            # If @message is empty, set new message
            if logdata['@message'] != '':
                logdata['@message'] = 'Packet lost to testserver, total ' + str(tempPacketLossTotal) \
                + ' consecutive packet lost.'
        else:
            # No packetloss, reset total counter back to 0
            tempPacketLossTotal = 0
            logdata['connection']['total lost'] = tempPacketLossTotal
            logdata['connection']['max lost'] = tempPacketLossMax

        # Check max packetloss
        if tempPacketLossMax < tempPacketLossTotal:
            tempPacketLossMax = tempPacketLossTotal
            logdata['connection']['max lost'] = tempPacketLossMax

        return

    def print_log(self, logdata):
        global tempBSSID
        global tempRSSI
        global tempChannel
        global tempPacketLossTotal
        global tempPacketLossMax

        print ('{:<15} {:>20} {:>10} {:<15} {:>20}'.format
            ('Current BSSID:', logdata['wireless']['BSSID'], '', 'Last BSSID:', str(logdata['wireless']['roam from BSSID'])))
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format
            ('SSID:', logdata['wireless']['SSID'], '', 'Last roam time:', logdata['wireless']['roam timestamp']))

        if logdata['wireless']['roam'] == 1:
            print('{:<15} {:>20} {:>10} {:<15} {:>25} {:>3}'.format
                      ('Current RSSI:', logdata['wireless']['RSSI'], '', 'Roam:\033[92m', 'True', '\033[0m'))
        else:
            print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format
                  ('Current RSSI:', logdata['wireless']['RSSI'], '', 'Roam:', 'False'))
        print('{:<15} {:>19} {:>10} {:<15} {:>15}'.format
              ('Current channel:', logdata['wireless']['channel'], '', 'Last roam from RSSI:', str(logdata['wireless']['roam from RSSI'])))
        print('{:<15} {:>20} {:>10} {:<15} {:>17}'.format
              ('Current noise:', logdata['wireless']['noise'], '', 'Last roam to RSSI:', str(logdata['wireless']['roam to RSSI'])))

        if logdata['connection']['packetloss'] == 1:
            print('{:<15} {:>20} {:>10} {:<15} {:>16} {:>3}'.format
                  ('TX rate:', logdata['wireless']['transmitrate'], '', 'Total lost packets:\033[91m', logdata['connection']['total lost'], '\033[0m'))
            print('{:<15} {:>20} {:>10} {:<15} {:>9}'.format
                  ('RTT server:', logdata['connection']['RTT'], '', 'Max packets lost last 24H:', logdata['connection']['max lost']))
        else:
            print('{:<15} {:>20} {:>10} {:<15} {:>16}'.format
                  ('TX rate:', logdata['wireless']['transmitrate'], '', 'Total lost packets:', logdata['connection']['total lost']))
            print('{:<15} {:>20} {:>10} {:<15} {:>9}'.format
                  ('RTT server:', logdata['connection']['RTT'], '', 'Max packets lost last 24H:', logdata['connection']['max lost']))
        print('{:<15} {:>20} {:>10} {:<15} {:>12}'.format
        ('RTT gateway:', logdata['connection']['RTT gw'], '', 'Packet lost to gateway:', logdata['connection']['gw packetloss']))

        print('------------------------------------------------------------------------------------')

        return



