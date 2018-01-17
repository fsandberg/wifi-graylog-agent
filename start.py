from osxwifi import wifistatus
from connectivity import connectivity
from logging import logdata
import time
import datetime





wifi = wifistatus()
connection = connectivity()
logdata = logdata()

remoteHost = '192.168.23.1'
remotePort = 22
timeout = 2  # Timeout in ms

timeout = float(timeout)/1000
sumPacketLost = 0
maxPacketLost = 0

clientMAC = wifi.get_hardwareaddress()
roamingLimit = -10

# Initiate status dictionary and set 'first run' parameters
status = {}
status['_LAST_BSSID'] = ''
status['_LAST_ROAM'] = '0'

startDay = datetime.datetime.now().strftime('%Y-%m-%d')

def printlog(statusdict, sleeptimer):
    global sumPacketLost
    global maxPacketLost

    # Reset maxPacketLost on new day
    runDay = datetime.datetime.now().strftime('%Y-%m-%d')
    if runDay != startDay:
        maxPacketLost = 0

    print ('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('BSSID:', status['_BSSID'], '', 'LAST BSSID:', status['_LAST_BSSID']))
    print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('SSID:', status['_SSID'], '', 'NOISE:', status['_NOISE']))
    if status['_ROAM'] == 'TRUE':
        print('{:<15} {:>20} {:>10} {:<15} {:>25} {:>3}'.format('RSSI:', status['_RSSI'], '', 'ROAM:\033[91m', status['_ROAM'], '\033[0m'))
    else:
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('RSSI:', status['_RSSI'], '', 'ROAM:', status['_ROAM']))
    print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('LAST ROAM RSSI:', status['_LAST_ROAM'], '', 'TX SPEED:', status['_TRANSMITRATE']))
    if status['_PACKETLOSS'] == 'TRUE':
        status['_LOSS_COUNT'] = 1
        sumPacketLost += 1
        if sumPacketLost > maxPacketLost:
            maxPacketLost = sumPacketLost
        print('{:<15} {:>20} {:>10} {:<15} {:>23} {:>3}'.format('CHANNEL:', status['_CHANNEL'], '', 'PACKET LOST:\033[91m', status['_PACKETLOSS'], '\033[0m'))
        print('{:<15} {:>20} {:>10} {:<15} {:>17}'.format('RTT:', status['_RTT'], '', 'MAX LOST LAST 24H:', maxPacketLost))
    else:
        status['_LOSS_COUNT'] = 0
        sumPacketLost = 0
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('CHANNEL:', status['_CHANNEL'], '', 'PACKET LOST:', status['_PACKETLOSS']))
        print('{:<15} {:>20} {:>10} {:<15} {:>17}'.format('RTT:', status['_RTT'], '', 'MAX LOST LAST 24H:', maxPacketLost))
    # No idea how to parse the return values :(
    #if roamingLimit >= int(status['_RSSI']):
    #    cachedResults = wifi.get_cachedscanresults()

    print('------------------------------------------------------------------------------------')
    time.sleep(sleeptimer)

    return



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

    printlog(status, 0.1)
    logdata.write_log('logbuffer.tmp', status)

    #sendlog('logbuffer.tmp')