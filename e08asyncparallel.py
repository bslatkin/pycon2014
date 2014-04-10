#!/usr/bin/env python3

"""
./e08asyncparallel.py http://camlistore.org 2
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
from e06asyncfetch import fetch_async


@asyncio.coroutine
def parallel_fetch(to_fetch, seen_urls):
    futures, results = [], []
    for url in to_fetch:
        if url in seen_urls: continue
        seen_urls.add(url)
        futures.append(fetch_async(url))          # Parallel kickoff

    for future in asyncio.as_completed(futures):  # Prioritized wait
        try:
            results.append((yield from future))
        except Exception:
            continue

    return results


@asyncio.coroutine
def crawl(start_url, max_depth):
    seen_urls = set()
    to_fetch = [canonicalize(start_url)]
    results = []
    for depth in range(max_depth + 1):
        batch = yield from parallel_fetch(to_fetch, seen_urls)
        to_fetch = []
        for url, data, found_urls in batch:
            to_fetch.extend(found_urls)
            results.append((depth, url, data))

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
