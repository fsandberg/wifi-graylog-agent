from tcpping import tcpping
import platform
import socket
import uuid
import re
import time
import datetime

# DECLARE CONSTANTS & VARIABLES

LOGFILE = 'logbuffer.tmp'
REMOTEHOST = 'www.google.se'
REMOTEPORT = 80
TIMEOUT = 0.3

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

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def getClientStatus(OS):
    global prevBSSID
    clientStatus = {}

    LOCALHOSTNAME = socket.gethostname()
    LOCALMAC = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    LOCALIP = getIP()

    clientStatus['LOCALMAC'] = LOCALMAC
    clientStatus['LOCALHOSTNAME'] = LOCALHOSTNAME
    clientStatus['LOCALIP'] = LOCALIP
    clientStatus['REMOTEHOST'] = REMOTEHOST
    clientStatus['REMOTEPORT'] = str(REMOTEPORT)

    if OS == 'Darwin':
        import objc

        objc.loadBundle('CoreWLAN',
                        bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                        module_globals=globals())

        for iname in CWInterface.interfaceNames():
            interface = CWInterface.interfaceWithName_(iname)
            clientStatus['TIMESTAMP'] = str(datetime.datetime.utcnow())
            clientStatus['BSSID'] = str(interface.bssid())
            clientStatus['SSID'] = str(interface.ssid())
            clientStatus['CHANNEL'] = str(interface.channel())
            clientStatus['RSSI'] = str(interface.rssi())
            clientStatus['TRANSMITRATE'] = interface.transmitRate()

            if interface.bssid() == None:
                clientStatus['CONNECTED'] = 'FALSE'
            else:
                clientStatus['CONNECTED'] = 'TRUE'

            if prevBSSID == '':
                # PREVIOUS BSSID EMPTY - FIRST RUN
                prevBSSID = str(interface.bssid())
                clientStatus['ROAM'] = 'FALSE'
                clientStatus['LAST_BSSID'] = 'CONNECTED'
            elif interface.bssid() == None:
                # DISCONNECTED, KEEP LAST BSSID
                clientStatus['ROAM'] = 'FALSE'
                clientStatus['LAST_BSSID'] = prevBSSID
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
        print('Unsupported OS!')

    clientConnectivity = TCPPing(REMOTEHOST, REMOTEPORT, TIMEOUT)
    clientStatus['PACKETLOSS'] = clientConnectivity['PACKETLOSS']
    clientStatus['RTT'] = clientConnectivity['RTT']

    return clientStatus

initLog()

while True:
    # GET STATUS BASED ON OS
    status = getClientStatus(platform.system())
    writeLog(status)
    time.sleep(1)