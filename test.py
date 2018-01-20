import socket


TCP_IP = '10.20.200.157'
TCP_PORT = 5045
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!".encode('utf-8')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
s.close()

print("received data: " + data)