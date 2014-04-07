#!/usr/bin/env python3.3
import tulip
from time import time

class DummyProtocol(tulip.Protocol):
    def __init__(self):
        self.future = tulip.Future()

    def connection_made(self, transport):
        pass

    def data_received(self, data):
        pass

    def eof_received(self):
        pass

    def connection_lost(self, exc):
        pass

    def pipe_connection_lost(self, fd, exc):
        pass

    def process_exited(self):
        self.future.set_result(None)

l = tulip.get_event_loop()

ts = time()
def elapsed():
    return "%.1f" %(time() - ts)

t, first = l.run_until_complete(l.subprocess_exec(DummyProtocol, "sleep", "1"))
t, third = l.run_until_complete(l.subprocess_exec(DummyProtocol, "sleep", "3"))

l.call_later(2, lambda: print("second", elapsed()))
l.call_later(4, l.stop)


l.run_until_complete(first.future)
print("first", elapsed())

l.run_until_complete(third.future)
print("third", elapsed())


l.run_forever()
print("end", elapsed())
