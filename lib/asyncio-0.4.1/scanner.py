#!/usr/bin/env python3

import os
import signal
import sys

assert sys.version >= '3.3', 'Please use Python 3.3 or higher.'

import tulip

class Scanner(tulip.Protocol):

    def connection_made(self, transport):
        self.transport = transport
        self.peer = self.transport.get_extra_info('peername')
        print(); print(self.peer)

    def data_received(self, data):
        print(); print(data, 'from', self.peer)
        self.transport.close()

    def connection_lost(self, exc):
        print('\nlost', self.peer)

def scanport(port):
    ippat = '10.1.10.%d'
    loop = tulip.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, loop.stop)
    futs = []
    for x in range(1, 255):
        host = ippat % x
        print('trying', host, port, end='\r', flush=True)
        fut = tulip.Task(loop.create_connection(Scanner, host, port),
                          timeout=1)
        futs.append(fut)
        loop.run_until_complete(tulip.sleep(0.001))
    print()
    for fut in futs:
        try:
            loop.run_until_complete(fut)
        except tulip.CancelledError:
            pass
        except os.error as exc:
            if exc.errno == 24:
                print()
                print(exc)
        except Exception as exc:
            print()
            print(exc)
    print()
    loop.call_later(1, loop.stop)
    loop.run_forever()

def main():
##    for port in range(20, 100):
    for port in [22, 80]:
        print('\n\n*** port', port, '***')
        scanport(port)

if __name__ == '__main__':
    main()
