#!/usr/bin/env python3

"""
./e02crawl.py http://camlistore.org 2
Found 37 urls
Depth  0  http://camlistore.org/                                   3681 bytes
Depth  1  http://camlistore.org/code                               4237 bytes
Depth  1  http://camlistore.org/community                          2180 bytes
Depth  1  http://camlistore.org/contributors                       2037 bytes
...
"""

from sys import argv

from e01fetch import fetch


def crawl(start_url, max_depth):
    seen_urls = set()
    to_fetch = [(0, start_url)]
    results = []
    while to_fetch:
        depth, url = to_fetch.pop(0)
        if depth > max_depth: continue
        if url in seen_urls: continue
        url, data, found_urls = fetch(url)
        seen_urls.add(url)  # Canonicalized
        if data is not None:
            results.append((depth, url, data))
        for url in found_urls:
            to_fetch.append((depth+1, url))

    return results


def print_crawl(result):
    result.sort()
    print('Found %d urls' % len(result))
    for depth, url, data in result:
        print('Depth %2d  %-50s %10d bytes' % (depth, url, len(data)))


def main():
    result = crawl(argv[1], int(argv[2]))
    print_crawl(result)


if __name__ == '__main__':
    main()
