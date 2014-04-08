#!/usr/bin/env python3

"""
./e07asynccrawl.py http://camlistore.org 2
Found 37 urls
Depth  0  http://camlistore.org/                                   3681 bytes
Depth  1  http://camlistore.org/code                               4237 bytes
Depth  1  http://camlistore.org/community                          2180 bytes
...
"""

from sys import argv
from urllib.parse import urljoin

import asyncio
from e01fetch import canonicalize, same_domain, URL_EXPR
from e02crawl import print_crawl
from e06asyncfetch import get_url


@asyncio.coroutine
def fetch(url):
    data = yield from get_url(url)
    if data is None:
        return None, None, []  # Error
    found_urls = set()
    for match in URL_EXPR.finditer(data):
        found = canonicalize(match.group('url'))
        if same_domain(url, found):
            found_urls.add(urljoin(url, found))
    return url, data, sorted(found_urls)


@asyncio.coroutine
def crawl(start_url, max_depth):
    seen_urls = set()
    to_fetch = [(0, canonicalize(start_url))]
    results = []
    while to_fetch:
        futures = []
        for depth, url in to_fetch:
            if depth > max_depth: continue
            if url in seen_urls: continue
            seen_urls.add(url)
            futures.append(fetch(url))  # Parallel kickoff

        to_fetch = []
        for future in asyncio.as_completed(futures):
            url, data, found_urls = yield from future
            if data is not None:
                results.append((depth, url, data))
            for url in found_urls:
                to_fetch.append((depth+1, url))

    return results


def main():
    # Bridge the gap between sync and async
    future = asyncio.Task(crawl(argv[1], int(argv[2])))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()

    result = future.result()
    print_crawl(result)


if __name__ == '__main__':
    main()