import timeit

import tornloop
import tulip


loop = tornloop.TornadoLoop()
tulip.set_event_loop(loop)


def async_func(value):
    p = tulip.Future()
    loop.call_later(0.01, p.set_result, value)
    return p


@tulip.coroutine
def sub_sub():
    yield from async_func(1)
    yield from async_func(1)


@tulip.coroutine
def sub():
    yield from async_func(1)
    yield from async_func(1)
    yield from sub_sub()


@tulip.task
def main():
    yield from async_func(1)
    yield from sub()
    yield from sub()


def bench():
    loop.run_until_complete(main())


if __name__ == '__main__':
    print(timeit.timeit('bench()', 'from __main__ import bench', number=400))
