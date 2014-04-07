import profile
import sys
import timeit

import tulip

loop = tulip.get_event_loop()

@tulip.coroutine
def nest(depth, dt):
    if depth > 0:
        yield from nest(depth-1, dt/2)
        yield from nest(depth-1, dt/2)
    else:
        yield from tulip.sleep(dt)

@tulip.coroutine
def flat(depth, dt):
    n = 2**depth
    dt_n = dt/ n
    for _ in range(n):
        yield from tulip.sleep(dt_n)

@tulip.coroutine
def main():
    if '-f' in sys.argv:
        yield from flat(10, 0.001)
    else:
        yield from nest(10, 0.001)

def bench():
    loop.run_until_complete(main())

if __name__ == '__main__':
    if '-p' in sys.argv:
        profile.run('bench()')
    else:
        print(timeit.timeit('bench()', 'from __main__ import bench',
                            number=10))
