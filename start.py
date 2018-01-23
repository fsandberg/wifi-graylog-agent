from osxwifi import WifiStatus
from logdata import LogProcessing
from connectivity import ConnectionCheck
import datetime
import pytz
import configparser
import time
import sys
import os
import threading

Wifi = WifiStatus()
Connection = ConnectionCheck()
LogHandler = LogProcessing()

try:
    Config = configparser.ConfigParser()
    ConfigFile = os.path.dirname(os.path.abspath(__file__))+"/config.ini"
    Config.read(ConfigFile)

    LogHost = Config['Logging']['Host']
    LogPort = Config['Logging']['Port']

    PrintToConsole = Config['Output']['Console']
    SendToLogHost = Config['Output']['Logserver']
    SleepTimer = float(Config['Output']['Pause'])

    TestServer = Config['Connectivity']['Testserver']
    TestPort = int(Config['Connectivity']['Port'])
    TimeOut = int(Config['Connectivity']['Timeout'])
    TimeOut = float(TimeOut)/1000

except KeyError:
    print('\033[91mERROR READING VALUES IN CONFIGURATION FILE\033[0m')
    sys.exit(0)

except configparser.NoSectionError:
    print('\033[91mBAD FORMAT IN CONFIGURATION FILE\033[0m')
    sys.exit(0)

except configparser.Error:
    print('\033[91mERROR READING CONFIGURATION FILE\033[0m')
    sys.exit(0)

LastRoamValue = 0
LastBSSIValue = ''

LogData = LogHandler.set_startvalues()

try:

    while True:
        LogData['BSSID'] = str(Wifi.get_bssid())
        LogData['SSID'] = str(Wifi.get_ssid())
        LogData['noise'] = Wifi.get_aggregatenoise()
        LogData['RSSI'] = Wifi.get_rssi()
        LogData['channel'] = Wifi.get_channel()
        LogData['transmitrate'] = Wifi.get_transmitrate()

        ConnectionStatus = Connection.get_connection(TestServer, TestPort, TimeOut)

        LogData['packetloss'] = ConnectionStatus['packetloss']
        LogData['RTT'] = ConnectionStatus['RTT']

        # Check roaming and last BSSID
        if LastBSSIValue == '':
            # First run, initiate parameter

            LogData['roam'] = 'FALSE'
            LogData['last BSSID'] = '--'
            LogData['last roam at'] = '--'
            LastRoamValue = LogData['RSSI']
            LastBSSIValue = LogData['BSSID']
        elif LogData['BSSID'] == 'None':
            # Disconnected, keep last known BSSID
            LogData['roam'] = 'FALSE'
            LastRoamValue = LogData['RSSI']
            LastBSSIValue = LogData['BSSID']
        elif LogData['BSSID'] == LastBSSIValue:
            # Same BSSID as before, no roaming
            if LogData['roam'] == 'TRUE':
                # First loop after a roam
                LogData['last roam to'] = LogData['RSSI']
                LogData['roam'] = 'FALSE'
            LastRoamValue = LogData['RSSI']
            LastBSSIValue = LogData['BSSID']
        elif LogData['BSSID'] != LastBSSIValue:
            # BSSID does not match previous, client has roamed
            LogData['roam'] = 'TRUE'
            LogData['last_BSSID'] = LastBSSIValue
            LogData['last_roam_at'] = LastRoamValue
            LogData['last_roam_to'] = LogData['RSSI']
            LogData['roam_time'] = str(datetime.datetime.now(tz=pytz.utc).strftime('%H:%M:%S.%f'))
            # Reset BSSID and RSSI
            LastBSSIValue = LogData['BSSID']
            LastRoamValue = LogData['RSSI']

        LogHandler.process_logdata(LogData)

        if PrintToConsole.upper() == 'TRUE':
            LogHandler.print_log(LogData)

        if SendToLogHost.upper() == 'TRUE':
            LogHandler.send_log(LogData, LogHost, LogPort)

        time.sleep(SleepTimer)

# Print out BSSID in cache
#
#        if roamingLimit >= int(status['_RSSI']):
#            cachedESS = {}
#            cachedResults = wifi.get_cachedscanresults()
#
#            for cwnetworks in cachedResults:
#
#                if cwnetworks.ssid() == status['_SSID'] and cwnetworks.bssid() != status['_BSSID']:
#
#                    print('{:<6} {:<19} {:<6} {:<5} {:<6} {:<5}'.format('BSSID:', cwnetworks.bssid(), 'RSSI:', cwnetworks.rssi(), 'CHANNEL: ', '--'))
#        print('------------------------------------------------------------------------------------')


except KeyboardInterrupt:
        print('\nUser interrupted process with CTRL-C\n')

