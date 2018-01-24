from connectivity import ConnectionCheck
#from gelf import GelfConnector
from logstash import LogstashConnector
from osxwifi import WifiStatus
from pathlib import Path
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
        logdata = {}
        logdata['maxpacketlost'] = 0
        logdata['sumpacketlost'] = 0
        logdata['startday'] = datetime.datetime.now().strftime('%Y-%m-%d')

        logdata['last_BSSID'] = '--'
        logdata['last_roam_at'] = '--'
        logdata['last_roam_to'] = '--'
        logdata['roam_time'] = '--'
        #logdata['clientmac'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        logdata['clientmac'] = WifiStatus().get_hardwareaddress()
        #gateways = netifaces.gateways()
        #logdata['defaultgateway'] = gateways['default']

        return logdata

    def get_time(self):
        time_now = datetime.datetime.now().strftime('%H:%M:%S')

        return time_now

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

    def print_log(self, status):
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

        # print(status['gateway'])
        print('------------------------------------------------------------------------------------')

        return status


