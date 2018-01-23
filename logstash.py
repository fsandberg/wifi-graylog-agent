from socket import *
import json


class LogstashConnector:

    def __init__(self):
        pass

    def log_tcp(self, logdata, loghost, port):
        try:
            # GELF "Header"

            #logdata['@timestamp'] = logdata['timestamp']
            logdata['@source'] = 'logstash'
            logdata['@message'] = logdata['short_message']
            #logdata['short_message']

            # logdata['host'] = gethostname()
            # logdata['facility'] = 'QLS wireless agent'
            # logdata['clienthostname'] = gethostname()

            tcp_socket = socket(AF_INET, SOCK_STREAM)
            tcp_socket.settimeout(.2)
            tcp_socket.connect((loghost, int(port)))
            logdata['clientip'] = tcp_socket.getsockname()[0]
            json_logdata = json.dumps(logdata)
            json_logdata = json_logdata + '\n'
            json_logdata = json_logdata.encode('utf-8')

            tcp_socket.send(json_logdata)

        except timeout:
            print('\033[91mTIMEOUT CONNECTING TO LOGSERVER\033[0m')
            return False

        except error:
            print('\033[91mNETWORK UNREACHABLE / CLIENT DISCONNECTED\033[0m')
            return False

        finally:
            tcp_socket.close()

        return True





