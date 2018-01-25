import objc

objc.loadBundle('CoreWLAN',
                bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                module_globals=globals())

class WifiStatus(object):
    ''' WiFI object'''

    def __init__(self):
        self.wifi = CWInterface.interfaceNames()
        for iname in self.wifi:
            self.interface = CWInterface.interfaceWithName_(iname)

    def get_wifistatus(self):
        if self.interface.powerOn() == 1:
            return "Yes"
        return "No"

    def get_ssid(self):
        return self.interface.ssid()

    def get_interface(self):
        return self.interface.interfaceName()

    def get_hardwareaddress(self):
        return self.interface.hardwareAddress()

    def get_aggregatenoise(self):
        return self.interface.aggregateNoise()

    def get_rssi(self):
        return self.interface.aggregateRSSI()

    def get_bssid(self):
        return self.interface.bssid()

    def get_channel(self):
        return self.interface.channel()

    def get_transmitrate(self):
        return self.interface.transmitRate()

    def get_transmitpower(self):
        return self.interface.transmitPower()

    def get_mcsindex(self):
        return self.interface.mcsIndex()

    def get_phymode(self):
        return self.interface.activePHYMode()

    def get_cachedscanresults(self):
        return self.interface.cachedScanResults()

    def get_countrycode(self):
        return self.interface.countryCode()

    def get_security(self):
        return self.interface.security()

    def get_serviceactive(self):
        return self.interface.serviceActive()

    def get_current_information(self, logdata):

        #logdata['wireless'] = {}

        logdata['wireless']['BSSID'] = str(self.get_bssid())
        logdata['wireless']['SSID'] = str(self.get_ssid())
        logdata['wireless']['noise'] = self.get_aggregatenoise()
        logdata['wireless']['RSSI'] = self.get_rssi()
        logdata['wireless']['channel'] = self.get_channel()
        # set client band
        if logdata['wireless']['channel'] > 13:
            logdata['wireless']['band'] = '5 Ghz'
        else:
            logdata['wireless']['band'] = '2.4 Ghz'
        logdata['wireless']['transmitrate'] = self.get_transmitrate()
        try:
            logdata['clientmac'] = WifiStatus().get_hardwareaddress()
        except:
            logdata['clientmac'] = '00:00:00:00:00:00'

        return logdata
