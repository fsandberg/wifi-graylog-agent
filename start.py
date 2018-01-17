from osxwifi import wifistatus
import time
import socket

wifi = wifistatus()

clientMAC = wifi.get_hardwareaddress()

# Initiate status dictionary and set 'first run' parameters
status = {}
status['_LAST_BSSID'] = ''

def print_console(statusdict, sleeptimer):
    print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('BSSID:', status['_BSSID'], '', 'LAST BSSID:', status['_LAST_BSSID']))
    if status['_ROAM'] == 'TRUE':
        sys.stdout.write('\a')
        sys.stdout.flush()
        print('{:<15} {:>20} {:>10} {:<15} {:>20} {:>3}'.format('RSSI:', status['_RSSI'], '', 'ROAM:', status['_ROAM'], '*'))
    else:
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('RSSI:', status['_RSSI'], '', 'ROAM:', status['_ROAM']))
        print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('CHANNEL:', status['_CHANNEL'], '', 'TX SPEED:', status['_TRANSMITRATE']))
        #   print('{:<15} {:>20} {:>10} {:<15} {:>20}'.format('RTT:', status['_RTT'], '', 'PACKETLOSS:', status['_PACKETLOSS']))
        print('------------------------------------------------------------------------------------')
        time.sleep(sleeptimer)

        return

while True:
    status['_BSSID'] = str(wifi.get_bssid())
    status['_RSSI'] = wifi.get_rssi()
    status['_CHANNEL'] = wifi.get_channel()
    status['_TRANSMITRATE'] = wifi.get_transmitrate()

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

    print_console(status, 1)
