from tcpping import tcpping
import time

class connectivity(object):
    ''' Check connection'''

    def get_connection(self, host, port, timeout):
        startTime = time.time()
        result = tcpping(host, port, timeout)
        stopTime = time.time()
        rtt = (stopTime - startTime)*1000
        rtt = float("{0:.2f}".format(rtt))
        returnValue = {}
        returnValue['RTT'] = rtt
        if result:
            # Packetloss = False
            returnValue['packetloss'] = 'FALSE'
            return returnValue
        else:
            # Packetloss = True
            returnValue['packetloss'] = 'TRUE'
            return returnValue


