
import functools

from tornado import ioloop

try:
    import tulip
    Base = tulip.AbstractEventLoop
except ImportError:
    Base = object


def ignore_args(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func()
    return wrapper


class TornadoLoop(Base):

    _loop = ioloop.IOLoop().current()

    def run_forever(self):
        self._loop.start()

    def run_until_complete(self, p):
        p.add_done_callback(ignore_args(self.stop))
        self.run_forever()

    def stop(self):
        self._loop.stop()

    def call_soon(self, callback, *args):
        self._loop.add_callback(callback, *args)

    def call_later(self, delay, callback, *args):
        deadline = self._loop.time() + delay
        callback = functools.partial(callback, *args)
        self._loop.add_timeout(deadline, callback)
