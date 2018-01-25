from socket import *
import json


class LogstashConnector:

    def __init__(self):
        pass

    def log_tcp(self, logdata, loghost, logport, logtimeout):
        try:
            logdata['@source'] = 'logstash'
            tcp_socket = socket(AF_INET, SOCK_STREAM)
            tcp_socket.settimeout(logtimeout)
            tcp_socket.connect((loghost, int(logport)))
            logdata['clientip'] = tcp_socket.getsockname()[0]
            json_logdata = json.dumps(logdata)
            json_logdata = json_logdata + '\n'
            json_logdata = json_logdata.encode('utf-8')

            tcp_socket.send(json_logdata)

        except timeout as e:
            #print('\033[91mTimeout connecting to logserver\033[0m')
            #print(e)
            #tcp_socket.close()
            return False

        except error as e:
            #print('\033[91mNetwork unreachable / client disconnected\033[0m')
            #print(e)
            #tcp_socket.close()
            return False

        except UnboundLocalError as e:
            #print('Other error occured...')
            #tcp_socket.close()
            return False
        except:
            #tcp_socket.close()
            return False
        try:
            tcp_socket.close()
        except:
            pass
        return True





