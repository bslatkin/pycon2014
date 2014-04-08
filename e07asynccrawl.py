#!/usr/bin/env python3

"""
./e01fetch.py http://camlistore.org
http://camlistore.org/ is 3681 bytes, 11 urls:
...
"""

from sys import argv
from urllib.parse import urljoin

import asyncio
from e01fetch import canonicalize, same_domain, URL_EXPR
from e06asyncfetch import get_url


@asyncio.coroutine
def fetch(url):
    url = canonicalize(url)
    data = yield from get_url(url)
    if data is None:
        return None, None, []  # Error
    found_urls = set()
    for match in URL_EXPR.finditer(data):
        found = canonicalize(match.group('url'))
        if same_domain(url, found):
            found_urls.add(urljoin(url, found))
    return url, data, found_urls


@asyncio.coroutine
def crawl(start_url, max_depth, _depth=0, _seen_urls=None):
    if _seen_urls is None: _seen_urls = set()
    if _depth > max_depth: return {}        # Reached max depth
    if start_url in _seen_urls: return {}   # Prevent loops

    _seen_urls.add(start_url)
    start_url, data, found_urls = yield from fetch(start_url)
    if data is None: return {}              # Ignore error URLs

    futures = []
    for url in found_urls:
        futures.append(crawl(
            url, max_depth, _depth=_depth+1, _seen_urls=_seen_urls))

    result = {start_url: (_depth, data)}
    for future in asyncio.as_completed(futures):
        result.update((yield from future))

    return result


def main():
    # Bridge the gap between sync and async
    future = asyncio.Task(crawl(argv[1], int(argv[2])))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()

    result = future.result()
    print('Found %d urls' % len(result))
    for url, (depth, data) in result.items():
        print('%10d bytes, depth %2d: %s' % (len(data), depth, url))


if __name__ == '__main__':
    main()
