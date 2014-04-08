#!/usr/bin/env python3

"""
./e11asyncmultitenant.py 9999

Navigate your browser to http://localhost:9999
"""

from html import escape
from sys import argv
from urllib.parse import parse_qsl

from aiohttp import Response
from aiohttp.server import ServerHttpProtocol
import asyncio
from e05threadfanin import get_top_words
from e10asyncfanin import crawl


MY_FORM = """
<h1>Crawl a URL</h1>
<form method="POST">
<input type="text" name="url" size="60" placeholder="Type a URL here">
<input type="submit" value="Crawl">
</form>
"""


class MyServer(ServerHttpProtocol):

    @asyncio.coroutine
    def handle_request(self, message, payload):
        response = Response(self.writer, 200)
        response.add_header('Content-Type', 'text/html')
        response.send_headers()

        if message.method == 'GET':
            response.write(MY_FORM.encode('utf-8'))
        elif message.method == 'POST':
            data = yield from payload.read()
            data = data.decode('utf-8')
            url = dict(parse_qsl(data)).get('url')
            result = yield from crawl(url, 1, 6)
            response.write(b'<pre>')
            response.write(escape(get_top_words(result)).encode('utf-8'))
            response.write(b'</pre>')
        else:
            response.write('Bad method')

        response.write_eof()


def main():
    port = int(argv[1])
    loop = asyncio.get_event_loop()
    future = loop.create_server(MyServer, '0.0.0.0', port)
    server = loop.run_until_complete(future)
    print('Server running on', server.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
