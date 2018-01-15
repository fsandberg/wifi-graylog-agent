from tcpping import tcpping
import platform
import time
import datetime

# DECLARE CONSTANTS & VARIABLES

LOGFILE = 'buffered.log'
HOSTNAME = 'www.google.se'
PORT = 80
TIMEOUT = 0.2

global prevBSSID
prevBSSID = ''


# DECLARE FUNCTIONS

def initLog():
    logFile = open(LOGFILE, 'w')
    logFile.close()
    return

def writeLog(logData):
    logFile = open(LOGFILE, 'a')
    logFile.write(str(logData))
    print(logData)
    logFile.write('\n')
    logFile.close()
    return

def TCPPing(hostName, tcpPort, timeOut):
    startTime = time.time()
    sendTCP = tcpping(host=hostName, port=tcpPort, timeout=timeOut)

    clientConnection = {}

    if sendTCP:
        clientConnection['PACKETLOSS'] = 0
        timeDiff = (time.time() - startTime) * 1000
        timeDiff = float("{0:.2f}".format(timeDiff))
        clientConnection['RTT'] = timeDiff
    else:
        clientConnection['PACKETLOSS'] = 1
        clientConnection['RTT'] = -1.00

    return clientConnection

def getClientStatus(OS):
    global prevBSSID
    clientStatus = {}
    if OS == 'Darwin':
        import objc

        objc.loadBundle('CoreWLAN',
                        bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                        module_globals=globals())

        for iname in CWInterface.interfaceNames():
            interface = CWInterface.interfaceWithName_(iname)
            clientStatus['GMT'] = time.strftime('%Y-%m-%d %H:%m:%S', time.gmtime())
            clientStatus['BSSID'] = str(interface.bssid())
            clientStatus['SSID'] = str(interface.ssid())
            clientStatus['CHANNEL'] = str(interface.channel())
            clientStatus['RSSI'] = str(interface.rssi())
            clientStatus['TRANSMITRATE'] = interface.transmitRate()


            if prevBSSID == '':
                # PREVIOUS BSSID EMPTY - FIRST RUN
                prevBSSID = str(interface.bssid())
                clientStatus['ROAM'] = 'FALSE'
                clientStatus['LAST_BSSID'] = 'CONNECTED'

            elif prevBSSID == interface.bssid():
                # BSSID IS SAME AS LAST RUN - NO ROAM
                clientStatus['ROAM'] = 'FALSE'
                clientStatus['LAST_BSSID'] = str(interface.bssid())
            else:
                # BSSID IS DIFFERENT FROM LAST RUN - CLIENT ROAM
                clientStatus['ROAM'] = 'TRUE'
                clientStatus['LAST_BSSID'] = prevBSSID
                prevBSSID = str(interface.bssid())


    elif OS == 'Windows':
        print('Windows not implemented yet')

    else:
        print('Unknown OS!')


    clientConnectivity = TCPPing(HOSTNAME,PORT,TIMEOUT)
    clientStatus['PACKETLOSS'] = clientConnectivity['PACKETLOSS']
    clientStatus['RTT'] = clientConnectivity['RTT']

    return clientStatus




initLog()


for steps in range(10):
    status = getClientStatus(platform.system())
    writeLog(status)
    time.sleep(1)