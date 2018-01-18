from osxwifi import wifistatus
from connectivity import connectivity
from logging import *

wifi = wifistatus()
connection = connectivity()
logdata = logdata()

logToServer = True

sleepTimer = 0.5  # Time in s between logging cycles
remoteHost = '192.168.23.1'
remotePort = 22
timeout = 2  # Timeout in ms

timeout = float(timeout)/1000

clientMAC = wifi.get_hardwareaddress()
roamingLimit = -10

# Initiate status dictionary and set 'first run' parameters
status = {}
status['_LAST_BSSID'] = ''
status['_LAST_ROAM'] = '0'

logdata.set_startday()

while True:
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
    if status['_LAST_BSSID'] == '':
        # First run, initiate parameter
        status['_LAST_BSSID'] = wifi.get_bssid()
        status['_ROAM'] = 'FALSE'
    elif status['_BSSID'] == 'None':
        # Disconnected, keep last known BSSID
        status['_ROAM'] = 'FALSE'
    elif status['_LAST_BSSID'] == status['_BSSID']:
        # Same BSSID as before, no roaming
        status['_ROAM'] = 'FALSE'
    else:
        # BSSID does not match previous, client has roamed
        status['_ROAM'] = 'TRUE'
        status['_LAST_BSSID'] = status['_BSSID']
        status['_LAST_ROAM'] = status['_RSSI']

    logdata.print_log(status, sleepTimer)

    if logToServer:
        logdata.write_log('logbuffer.tmp', status)
