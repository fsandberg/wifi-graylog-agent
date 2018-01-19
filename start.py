from osxwifi import wifistatus
from connectivity import connectivity
from logdata import *
from sendgraylog import sendgraylog

wifi = wifistatus()
connection = connectivity()
logdata = logdata()
sendgraylog = sendgraylog()

logToServer = False

sleepTimer = 1  # Time in s between logging cycles
remoteHost = 'www.google.se'
remotePort = 80
timeout = 200  # Timeout in ms
logHost = '10.20.200.157'
logPort = '5045'

timeout = float(timeout)/1000

clientMAC = wifi.get_hardwareaddress()
roamingLimit = -10

# set initial values
status = {}
status['last BSSID'] = ''
status['last roam at'] = ''
status['last roam to'] = '--'
status['roam time'] = '--'
lastRoamValue = 0
lastBSSIValue = ''
logdata.set_startday()

try:

    while True:
        timestamp = logdata.get_timestamp()
        #status['timestamp'] = timestamp['UTC'].isoformat()
        status['timestamp'] = timestamp['epoch']
        #status['_EPOCH'] = timestamp['_EPOCH']
        status['BSSID'] = str(wifi.get_bssid())
        status['SSID'] = str(wifi.get_ssid())
        status['noise'] = wifi.get_aggregatenoise()
        status['RSSI'] = wifi.get_rssi()
        status['channel'] = wifi.get_channel()
        status['transmitrate'] = wifi.get_transmitrate()
        connectionStatus = connection.get_connection(remoteHost, remotePort, timeout)
        status['packetloss'] = connectionStatus['packetloss']
        status['RTT'] = connectionStatus['RTT']

        # Check roaming and last BSSID
        if lastBSSIValue == '':
            # First run, initiate parameter

            status['roam'] = 'FALSE'
            status['last BSSID'] = '--'
            status['last roam at'] = '--'
            lastRoamValue = status['RSSI']
            lastBSSIValue = status['BSSID']
        elif status['BSSID'] == 'None':
            # Disconnected, keep last known BSSID
            status['roam'] = 'FALSE'
            lastRoamValue = status['RSSI']
            lastBSSIValue = status['BSSID']
        elif status['BSSID'] == lastBSSIValue:
            # Same BSSID as before, no roaming
            if ['roam'] == 'TRUE':
                # First loop after a roam
                status['last roam to'] = status['RSSI']
            status['roam'] = 'FALSE'
            lastRoamValue = status['RSSI']
            lastBSSIValue = status['BSSID']
        elif status['BSSID'] != lastBSSIValue:
            # BSSID does not match previous, client has roamed
            status['roam'] = 'TRUE'
            status['last BSSID'] = lastBSSIValue
            status['last roam at'] = lastRoamValue
            status['last roam to'] = status['RSSI']
            status['roam time'] = logdata.get_time()
            # Reset BSSID and RSSI
            lastBSSIValue = status['BSSID']
            lastRoamValue = status['RSSI']

        logdata.print_log(status, sleepTimer)
        sendgraylog.send_to_graylog(logHost, logPort, status)
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
            logdata.write_log('logbuffer.tmp', status)

except KeyboardInterrupt:
        print('\nUser interrupted process with CTRL-C\n')

