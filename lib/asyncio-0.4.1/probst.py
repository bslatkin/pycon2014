from socket import *

udp = socket(AF_INET, SOCK_DGRAM)
udp.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)

udp.bind(('0.0.0.0', 1337))
udp.setblocking(False)
udp.setsockopt(SOL_IP, IP_TTL, 4)
udp.connect(('8.8.8.8', 12345))

buf = b'x' * 400
for _ in range(1024 * 1024 * 10):
    udp.send(buf)
    print('.', end='', flush='')
