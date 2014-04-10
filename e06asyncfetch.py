#!/usr/bin/env python3

"""
./e06asyncfetch.py http://camlistore.org
http://camlistore.org/ is 3681 bytes, 11 urls:
...

Also try the error case and check out the legible traceback:
./e06asyncfetch.py http://camlistore.bad
...
"""

import logging
logging.getLogger().setLevel(logging.INFO)
import re
from sys import argv
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

import aiohttp
import asyncio
from e01extract import canonicalize, same_domain, URL_EXPR


@asyncio.coroutine
def get_url_async(url):
    logging.info('Fetching %s', url)
    response = yield from aiohttp.request('get', url, timeout=5)
    try:
        assert response.status == 200
        data = yield from response.read()
        assert data
        return data.decode('utf-8')
    finally:
        response.close()


@asyncio.coroutine
def fetch_async(url):
    data = yield from get_url_async(url)
    found_urls = set()
    for match in URL_EXPR.finditer(data):
        found = canonicalize(match.group('url'))
        if same_domain(url, found):
            found_urls.add(urljoin(url, found))
    return url, data, sorted(found_urls)


def main():
    url = canonicalize(argv[1])

    # Bridge the gap between sync and async
    future = asyncio.Task(fetch_async(url))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()

    _, data, found_urls = future.result()  # Will raise exception
    print('%s is %d bytes, %d urls:\n%s' %
          (url, len(data), len(found_urls), '\n'.join(found_urls)))


if __name__ == '__main__':
    main()
