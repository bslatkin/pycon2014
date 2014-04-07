import asyncio
import socket

class EchoServer(asyncio.Protocol):
    def connection_made(self, transport):
        ############ XXX: DETECT BROKEN SOCKETS ############################
        sock = transport.get_extra_info('socket')
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        ####################################################################

        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        print('data received: {}'.format(data))
        self.transport.write(data)

    def connection_lost(self, exc):
        print('connection_lost')

loop = asyncio.get_event_loop()
coro = loop.create_server(EchoServer, '0.0.0.0', 8888)
server = loop.run_until_complete(coro)
loop.run_forever()
