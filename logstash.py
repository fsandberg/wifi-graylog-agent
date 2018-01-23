from socket import *
import json


class LogstashConnector:

    def __init__(self):
        pass

    def log_tcp(self, logdata, loghost, port):
        try:
            # GELF "Header"

            message = {
                '@timestamp': logdata['timestamp'],
                '@message': logdata['short_message'],
                '@source': gethostname(),
                '@source_host': gethostname(),
                'level': 'INFO',
                '@type': 'Logstash',
                'RSSI': logdata['RSSI'],
                'BSSID': logdata['BSSID'],
                'SSID': logdata['SSID'],
                '@fields': {
                       'logger': 'QLS wifi agent',
                   },
            }
            logdata['@timestamp'] = logdata['timestamp']
            logdata['@source'] = 'logstash'
            logdata['@message'] = logdata['short_message']
            #logdata['short_message'].pop()
            message = logdata

            # logdata['host'] = gethostname()
            # logdata['facility'] = 'QLS wireless agent'
            # logdata['clienthostname'] = gethostname()

            tcp_socket = socket(AF_INET, SOCK_STREAM)
            tcp_socket.settimeout(.2)
            tcp_socket.connect((loghost, int(port)))
            message['clientip'] = tcp_socket.getsockname()[0]
            logmessage = json.dumps(message)
            logmessage = logmessage + '\n'
            logmessage = logmessage.encode('utf-8')

            tcp_socket.send(logmessage)

        except timeout:
            print('\033[91mTIMEOUT CONNECTING TO LOGSERVER\033[0m')
            return False

        except error:
            print('\033[91mNETWORK UNREACHABLE / CLIENT DISCONNECTED\033[0m')
            return False

        finally:
            tcp_socket.close()

        return True





