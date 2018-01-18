from osxwifi import wifistatus
from connectivity import connectivity
from logging import *

wifi = wifistatus()
connection = connectivity()
logdata = logdata()

logToServer = True

sleepTimer = 0.5  # Time in s between logging cycles
remoteHost = 'www.google.se'
remotePort = 80
timeout = 200  # Timeout in ms

timeout = float(timeout)/1000

clientMAC = wifi.get_hardwareaddress()
roamingLimit = -10

# set initial values
status = {}
status['_LAST_BSSID'] = ''
status['_LAST_ROAM'] = ''
lastRoamValue = 0
lastBSSIValue = ''
logdata.set_startday()

try:

    while True:
        timestamp = logdata.get_timestamp()
        status['_TIMESTAMP'] = timestamp['_UTC'].isoformat()
        status['_EPOCH'] = timestamp['_EPOCH']
        status['_BSSID'] = str(wifi.get_bssid())
        status['_SSID'] = str(wifi.get_ssid())
        status['_NOISE'] = wifi.get_aggregatenoise()
        status['_RSSI'] = wifi.get_rssi()
        status['_CHANNEL'] = wifi.get_channel()
        status['_TRANSMITRATE'] = wifi.get_transmitrate()
        connectionStatus = connection.get_connection(remoteHost, remotePort, timeout)
        status['_PACKETLOSS'] = connectionStatus['_PACKETLOSS']
        status['_RTT'] = connectionStatus['_RTT']

        # Check roaming and last BSSID
        if lastBSSIValue == '':
            # First run, initiate parameter
            #status['_LAST_BSSID'] = wifi.get_bssid()
            status['_ROAM'] = 'FALSE'
            status['_LAST_BSSID'] = '--'
            status['_LAST_ROAM'] = '--'
            lastRoamValue = status['_RSSI']
            lastBSSIValue = status['_BSSID']
        elif status['_BSSID'] == 'None':
            # Disconnected, keep last known BSSID
            status['_ROAM'] = 'FALSE'
            lastRoamValue = status['_RSSI']
            lastBSSIValue = status['_BSSID']
        elif status['_BSSID'] == lastBSSIValue:
            # Same BSSID as before, no roaming
            status['_ROAM'] = 'FALSE'
            lastRoamValue = status['_RSSI']
            lastBSSIValue = status['_BSSID']
        elif status['_BSSID'] != lastBSSIValue:
            # BSSID does not match previous, client has roamed
            status['_ROAM'] = 'TRUE'
            status['_LAST_BSSID'] = lastBSSIValue
            status['_LAST_ROAM'] = lastRoamValue
            # Reset BSSID and RSSI
            lastBSSIValue = status['_BSSID']
            lastRoamValue = status['_RSSI']

        logdata.print_log(status, sleepTimer)

        if logToServer:
            logdata.write_log('logbuffer.tmp', status)

except KeyboardInterrupt:
        print('\nUser interrupted process with CTRL-C\n')

