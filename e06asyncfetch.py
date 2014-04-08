#!/usr/bin/env python3

"""
./e06asyncfetch.py http://camlistore.org
http://camlistore.org/ is 3681 bytes, 11 urls:
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
from e01fetch import canonicalize, same_domain, URL_EXPR


@asyncio.coroutine
def get_url(url):
    logging.info('Fetching %s', url)
    try:
        response = yield from aiohttp.request('get', url, timeout=5)
    except Exception as e:
        logging.error('Error fetching %s. %s: %s',
                      url, e.__class__.__name__, e)
        return None
    try:
        if response.status != 200:
            logging.error('Error fetching %s. HTTP Status: %d',
                          url, response.status)
            return None
        data = yield from response.read()
        if not data:
            logging.error('Error fetching %s. No data.', url)
            return None
        try:
            return data.decode('utf-8')
        except:
            return None
    finally:
        response.close()


def fetch(url):
    url = canonicalize(url)

    # Bridge the gap between sync and async
    future = asyncio.Task(get_url(url))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()
    data = future.result()

    if data is None:
        return None, None, []  # Error
    found_urls = set()
    for match in URL_EXPR.finditer(data):
        found = canonicalize(match.group('url'))
        if same_domain(url, found):
            found_urls.add(urljoin(url, found))
    return url, data, found_urls


def main():
    url, data, found_urls = fetch(argv[1])
    print('%s is %d bytes, %d urls:\n%s' %
          (url, len(data), len(found_urls), '\n'.join(found_urls)))


if __name__ == '__main__':
    main()
