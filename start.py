from osxwifi import wifistatus
from connectivity import connectivity
from logdata import *
from GELF import GELF
import time

wifi = wifistatus()
connection = connectivity()
loghandler = logdata()

logToServer = False

sleepTimer = 0.5  # Time in s between logging cycles
remoteHost = 'www.google.se'
remotePort = 80
timeout = 200  # Timeout in ms
loghost = '10.20.200.157'
logport = 5045

timeout = float(timeout)/1000

clientMAC = wifi.get_hardwareaddress()
roamingLimit = -10

# set initial values


lastRoamValue = 0
lastBSSIValue = ''

logdata = loghandler.set_startvalues()

try:

    while True:
        logdata['BSSID'] = str(wifi.get_bssid())
        logdata['SSID'] = str(wifi.get_ssid())
        logdata['noise'] = wifi.get_aggregatenoise()
        logdata['RSSI'] = wifi.get_rssi()
        logdata['channel'] = wifi.get_channel()
        logdata['transmitrate'] = wifi.get_transmitrate()

        connectionStatus = connection.get_connection(remoteHost, remotePort, timeout)

        logdata['packetloss'] = connectionStatus['packetloss']
        logdata['RTT'] = connectionStatus['RTT']

        # Check roaming and last BSSID
        if lastBSSIValue == '':
            # First run, initiate parameter

            logdata['roam'] = 'FALSE'
            logdata['last BSSID'] = '--'
            logdata['last roam at'] = '--'
            lastRoamValue = logdata['RSSI']
            lastBSSIValue = logdata['BSSID']
        elif logdata['BSSID'] == 'None':
            # Disconnected, keep last known BSSID
            logdata['roam'] = 'FALSE'
            lastRoamValue = logdata['RSSI']
            lastBSSIValue = logdata['BSSID']
        elif logdata['BSSID'] == lastBSSIValue:
            # Same BSSID as before, no roaming
            if logdata['roam'] == 'TRUE':
                # First loop after a roam
                logdata['last roam to'] = logdata['RSSI']
                logdata['roam'] = 'FALSE'
            lastRoamValue = logdata['RSSI']
            lastBSSIValue = logdata['BSSID']
        elif logdata['BSSID'] != lastBSSIValue:
            # BSSID does not match previous, client has roamed
            logdata['roam'] = 'TRUE'
            logdata['last BSSID'] = lastBSSIValue
            logdata['last roam at'] = lastRoamValue
            logdata['last roam to'] = logdata['RSSI']
            logdata['roam time'] = datetime.datetime.now(tz=pytz.utc)
            # Reset BSSID and RSSI
            lastBSSIValue = logdata['BSSID']
            lastRoamValue = logdata['RSSI']

        loghandler.process_logdata(logdata)
        loghandler.print_log(logdata, sleepTimer)
        GELF().log_tcp(logdata, loghost, logport)

        #sendgraylog.send_to_graylog(logHost, logPort, status)
        time.sleep(sleepTimer)

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

        if logToServer:
            logdata.write_log('logbuffer.tmp', logdata)

except KeyboardInterrupt:
        print('\nUser interrupted process with CTRL-C\n')

