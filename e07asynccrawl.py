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

import asyncio
from e01extract import canonicalize
from e02crawl import print_crawl
from e06asyncextract import extract_async


@asyncio.coroutine
def extract_multi_async(to_fetch, seen_urls):
    results = []
    for url in to_fetch:
        if url in seen_urls: continue
        seen_urls.add(url)
        try:
            results.append((yield from extract_async(url)))
        except Exception:
            continue
    return results


@asyncio.coroutine
def crawl_async(start_url, max_depth):
    seen_urls = set()
    to_fetch = [canonicalize(start_url)]
    results = []
    for depth in range(max_depth + 1):
        batch = yield from extract_multi_async(to_fetch, seen_urls)
        to_fetch = []
        for url, data, found_urls in batch:
            results.append((depth, url, data))
            to_fetch.extend(found_urls)

    return results


def main():
    # Bridge the gap between sync and async
    future = asyncio.Task(crawl_async(argv[1], int(argv[2])))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()

    result = future.result()
    print_crawl(result)


if __name__ == '__main__':
    main()
