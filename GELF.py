from socket import *
import json
import zlib
import configreader

class GELF:

    #def __init__(self):

    #Send GELF data in UDP Datagram
    def log_udp(self, data, loghost, port ):
        try:
            # GELF "Header"

            data['short_message'] = '-'
            data['host'] = gethostname()
            data['clienthostname'] = gethostname()
            data['facility'] = 'QLS Wireless agent'


            udp_socket = socket(AF_INET,SOCK_DGRAM)
            data = json.dumps(data).encode('utf-8')
            compressed_data = zlib.compress(data)
            udp_socket.sendto(compressed_data,(loghost, port))
            udp_socket.close()
        except Exception:
            raise

    def log_tcp(self, logdata, loghost, port):
        try:
            # GELF "Header"

            logdata['short_message'] = '-'
            logdata['host'] = gethostname()
            logdata['facility'] = 'QLS wireless agent'
            logdata['clienthostname'] = gethostname()

            tcp_socket = socket(AF_INET, SOCK_STREAM)
            tcp_socket.settimeout(.5)
            tcp_socket.connect((loghost, port))
            logdata['clientip'] = tcp_socket.getsockname()[0]
            logdata = json.dumps(logdata).encode('utf-8')
            tcp_socket.send(logdata)

        except timeout:
            print('\033[91mTIMEOUT CONNECTING TO LOGSERVER\033[0m')

        except error:
            print('\033[91mNETWORK UNREACHABLE / CLIENT DISCONNECTED\033[0m')

        finally:
            tcp_socket.close()





