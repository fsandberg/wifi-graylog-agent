from tcpping import tcpping
import time


class ConnectionCheck(object):

    def check_connection(self, host, port, timeout):
        result = tcpping(host, port, timeout)

        return result

    def get_connection(self, host, port, timeout):
        startTime = time.time()
        result = tcpping(host, port, timeout)
        stopTime = time.time()
        rtt = (stopTime - startTime)*1000
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


