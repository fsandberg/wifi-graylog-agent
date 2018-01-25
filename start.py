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
import resource

#if platform.system() == 'Windows':
#    import win32file
#    win32file._setmaxstdio(2048)


soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
#print(soft)
#print(hard)
resource.setrlimit(resource.RLIMIT_NOFILE, (3000, hard))
#print(soft)
#print(hard)

Wifi = WifiStatus()
Connection = ConnectionCheck()
LogHandler = LogProcessing()

#os.system('clear')

try:
    Config = configparser.ConfigParser()
    ConfigFile = os.path.dirname(os.path.abspath(__file__))+"/config.ini"
    Config.read(ConfigFile)

    LogHost = Config['Logging']['Host']
    LogPort = int(Config['Logging']['Port'])
    LogTimeOut = int(Config['Logging']['Timeout'])
    LogTimeOut = float(LogTimeOut) / 1000

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

# Set initial values
LogData = LogHandler.set_startvalues()

try:

    while True:
        # Get current wifi info from API - populates wireless 'sub-dict'
        Wifi.get_current_information(LogData)
        # Run connection tests - populates connection 'sub-dict'
        Connection.get_connection_status(LogData, TestServer, TestPort, TimeOut)
        Connection.ping_gateway(LogData)
        # Analyze collected data and calculate new information - populates all dicts
        LogHandler.analyze_data(LogData)

        if PrintToConsole.upper() == 'TRUE':
            LogHandler.print_log(LogData)

        if SendToLogHost.upper() == 'TRUE':
            LogHandler.send_log(LogData, LogHost, LogPort, LogTimeOut)

        time.sleep(SleepTimer)
        os.system('clear')

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

