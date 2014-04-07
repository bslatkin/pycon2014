__author__ = 'chrisprobst'

import unittest
import time
import traceback
import asyncio


HOST = '127.0.0.1'
PORT = 1337
ADDRESS = (HOST, PORT)


class UdpProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        print('Datagram received')

    def error_received(self, exc):
        traceback.print_exc()

    def pause_writing(self):
        print('UDP overwhelmed')
        # Actually never called!

    def resume_writing(self):
        print('UDP ready for more')
        # Actually never called!

class TestUdp(unittest.TestCase):

    @asyncio.coroutine
    def start_udp(self):
        pair = yield from self.loop.create_datagram_endpoint(UdpProtocol,
                                                             remote_addr=('172.16.195.133', 1337))
        self.transport, self.protocol = pair
        self.transport.set_write_buffer_limits(0)

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.start_udp())

    def tearDown(self):
        self.transport.close()

    def test_heavy_writing(self):
        for _ in range(1024 * 1024):
            self.transport.sendto(b'x' * 1400)
            x = self.transport.get_write_buffer_size()
            if x: print(x)

unittest.main()
