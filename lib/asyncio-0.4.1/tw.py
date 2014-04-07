#
# $ PYTHONPATH=~/hg/tulip python3.3 tulipwork3.py
#
# In coro2 change range(12) to range(15) and observe difference.

from asyncio import *
loop = get_event_loop()

traces = ['start']

def xprint(arg):
    global traces
    traces += [ arg ]
    print(arg)

def dump():
    print(traces)

def do_work():
    sum = 0
    for i in range(10000):
        sum += sum + i
    return sum

def coro1():
    for i in range(10):
        xprint("coro1:%d" % i)
        do_work()
        yield None

    return "CORO1:done"

def coro2():
    for i in range(15):
        xprint("coro2:%d" % i)
        do_work()
        yield None

    return "CORO2:done"

def main():
    f1 = Task(coro1())
    f2 = Task(coro2())

    # g = gather(f1, f2)
    g = Task(wait([f1, f2], return_when=FIRST_COMPLETED))

    loop.run_until_complete(g)

    print("Loop is done")
    print("g.result() = %s" % (g.result(),) )
    dump()

if __name__ == "__main__":
    main()
