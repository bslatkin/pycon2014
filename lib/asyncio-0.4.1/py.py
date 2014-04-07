from tulip import *

@coroutine
def fetch():
    r, w = yield from open_connection('python.org', 80)
    # r is a StreamReader, w is a Transport
    w.write(b'GET / HTTP/1.0\r\n\r\n')
    while True:  # read until blank line
        line = yield from r.readline()
        if not line.strip():
            break
    contents = yield from r.read()
    return contents

print(get_event_loop().run_until_complete(fetch()))
