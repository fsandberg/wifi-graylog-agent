from tcpping import tcpping
import time
import sys
timer = time.clock if sys.platform == 'win32' else time.time

start = timer()



class ConnectionCheck(object):

    def check_connection(self, host, port, timeout):
        result = tcpping(host, port, timeout)

        return result

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
        logdata['connection'] = {}
        startTime = timer()
        result = tcpping(host, port, timeout)
        stopTime = timer()
        rtt = (stopTime-startTime) * 1000
        rtt = float("{0:.2f}".format(rtt))

        if result:
            # Packetloss = False
            logdata['connection']['packetlosscount'] = 0
            logdata['connection']['RTT'] = rtt
        else:
            # Packetloss = True
            logdata['connection']['packetlosscount'] = 1
            logdata['connection']['RTT'] = 0

        return


