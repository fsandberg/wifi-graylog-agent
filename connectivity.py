from tcpping import tcpping
import time
import sys
import netifaces
from platform import system as system_name
from os import system as system_call
import re
import subprocess

timer = time.clock if sys.platform == 'win32' else time.time

#start = timer()



class ConnectionCheck(object):

    def check_connection(self, host, port, timeout):
        result = tcpping(host, port, timeout)

        return result

    def ping_gateway(self, logdata):
        try:
            defaultgateway = netifaces.gateways()['default'][netifaces.AF_INET][0]
            if defaultgateway == '':
                logdata['connection']['gw packetloss'] = 1
                logdata['connection']['RTT gw'] = 0
                return False
            if system_name().lower() == 'windows':
                ping = subprocess.Popen(
                    ["ping", '-n', '1', '-w', '1', defaultgateway],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                ping = subprocess.Popen(
                    ['ping', '-c', '1', '-W', '1', defaultgateway],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            out, error = ping.communicate()
            try:
                matcher = re.compile("round-trip min/avg/max/stddev = (\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)")
                response = (matcher.search(out.decode('utf-8')).groups())
            except:
                logdata['connection']['gw packetloss'] = 1
                logdata['connection']['RTT gw'] = 0
                return False
            # get min value (1 = avg, 2 = max)
            rtt = float(response[0])
            logdata['connection']['gw packetloss'] = 0
            logdata['connection']['RTT gw'] = rtt
        except:
            logdata['connection']['gw packetloss'] = 1
            logdata['connection']['RTT gw'] = 0
            return False
        return True

    def get_connection(self, host, port, timeout):
        startTime = timer()
        result = tcpping(host, port, timeout)
        stopTime = timer()
        rtt = (stopTime-startTime) * 1000
        rtt = float("{0:.2f}".format(rtt))
        returnValue = {}

        if result:
            # Packetloss = False
            returnValue['packetloss'] = 'FALSE'
            returnValue['RTT'] = rtt
            return returnValue
        else:
            # Packetloss = True
            returnValue['packetloss'] = 'TRUE'
            returnValue['RTT'] = 0
            return returnValue

    def get_connection_status(self, logdata, host, port, timeout):
        startTime = timer()
        result = tcpping(host, port, timeout)
        stopTime = timer()
        rtt = (stopTime-startTime) * 1000
        rtt = float("{0:.2f}".format(rtt))

        if result:
            # Packetloss = False
            logdata['connection']['packetloss'] = 0
            logdata['connection']['RTT'] = rtt
        else:
            # Packetloss = True
            logdata['connection']['packetloss'] = 1
            logdata['connection']['RTT'] = 0

        return


