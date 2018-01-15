from tcpping import tcpping
from pygelf import GelfTcpHandler
import platform
import socket
import uuid
import pytz
import re
import time
import datetime
import logging
import json
import dateutil.parser as dp


# DECLARE CONSTANTS & VARIABLES

LOGFILE = 'logbuffer.tmp'
REMOTEHOST = 'www.google.se'
REMOTEPORT = 80
TIMEOUT = 0.3

LOGHOST = '10.20.200.157'
LOGTCP = '9923'

global prevBSSID
prevBSSID = ''



# DECLARE FUNCTIONS

def initLog():
    logFile = open(LOGFILE, 'w')
    logFile.close()
    return

def writeLog(logData):
    logFile = open(LOGFILE, 'a')
    logData = json.dumps(logData)
    logFile.write(str(logData))
    logFile.write('\n')
    logFile.close()
    return

def sendLog(logData):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.addHandler(GelfTcpHandler(host=LOGHOST, port=LOGTCP))


    return

def TCPPing(hostName, tcpPort, timeOut):
    startTime = time.time()
    sendTCP = tcpping(host=hostName, port=tcpPort, timeout=timeOut)

    clientConnection = {}

    if sendTCP:
        clientConnection['_PACKETLOSS'] = 0
        timeDiff = (time.time() - startTime) * 1000
        timeDiff = float("{0:.2f}".format(timeDiff))
        clientConnection['_RTT'] = timeDiff
    else:
        clientConnection['_PACKETLOSS'] = 1
        clientConnection['_RTT'] = -1.00

    return clientConnection

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect((REMOTEHOST, 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def utcnow():
    return datetime.datetime.now(tz=pytz.utc)

def getClientStatus(OS):
    global prevBSSID
    clientStatus = {}

    LOCALHOSTNAME = socket.gethostname()
    LOCALIP = getIP()
    LOCALMAC = ':'.join(re.findall('..', '%012x' % uuid.getnode()))


    clientStatus['_LOCALMAC'] = LOCALMAC
    clientStatus['_LOCALHOSTNAME'] = LOCALHOSTNAME
    clientStatus['_LOCALIP'] = LOCALIP
    clientStatus['_REMOTEHOST'] = REMOTEHOST
    clientStatus['_REMOTEPORT'] = str(REMOTEPORT)
    clientStatus['_TIMESTAMP'] = utcnow().isoformat()
    clientStatus['_EPOCH'] = dp.parse(clientStatus['_TIMESTAMP']).strftime('%s')

    if OS == 'Darwin':
        import objc

        objc.loadBundle('CoreWLAN',
                        bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                        module_globals=globals())

        for iname in CWInterface.interfaceNames():
            interface = CWInterface.interfaceWithName_(iname)
            clientStatus['_BSSID'] = str(interface.bssid())
            clientStatus['_SSID'] = str(interface.ssid())
            clientStatus['_CHANNEL'] = str(interface.channel())
            clientStatus['_RSSI'] = str(interface.rssi())
            clientStatus['_TRANSMITRATE'] = interface.transmitRate()

            if interface.bssid() == None:
                clientStatus['_CONNECTED'] = 'FALSE'
            else:
                clientStatus['_CONNECTED'] = 'TRUE'

            if prevBSSID == '':
                # PREVIOUS BSSID EMPTY - FIRST RUN
                prevBSSID = str(interface.bssid())
                clientStatus['_ROAM'] = 'FALSE'
                clientStatus['_LAST_BSSID'] = 'CONNECTED'
            elif interface.bssid() == None:
                # DISCONNECTED, KEEP LAST BSSID
                clientStatus['_ROAM'] = 'FALSE'
                clientStatus['_LAST_BSSID'] = prevBSSID
            elif prevBSSID == interface.bssid():
                # BSSID IS SAME AS LAST RUN - NO ROAM
                clientStatus['_ROAM'] = 'FALSE'
                clientStatus['_LAST_BSSID'] = str(interface.bssid())
            else:
                # BSSID IS DIFFERENT FROM LAST RUN - CLIENT ROAM
                clientStatus['_ROAM'] = 'TRUE'
                clientStatus['_LAST_BSSID'] = prevBSSID
                prevBSSID = str(interface.bssid())


    elif OS == 'Windows':
        print('Windows not implemented yet')

    else:
        print('Unsupported OS!')

    clientConnectivity = TCPPing(REMOTEHOST, REMOTEPORT, TIMEOUT)
    clientStatus['_PACKETLOSS'] = clientConnectivity['_PACKETLOSS']
    clientStatus['_RTT'] = clientConnectivity['_RTT']

    return clientStatus

initLog()

while True:
    # GET STATUS BASED ON OS
    status = getClientStatus(platform.system())
    writeLog(status)
    jsonarray = json.dumps(status)


    time.sleep(1)