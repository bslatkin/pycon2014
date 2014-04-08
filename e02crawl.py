#!/usr/bin/env python3

"""
./e02crawl.py http://camlistore.org 1
Found 10 urls
...
"""

from sys import argv

from e01fetch import fetch


def crawl(start_url, max_depth, _depth=0, _seen_urls=None):
    if _seen_urls is None: _seen_urls = set()
    if _depth > max_depth: return {}        # Reached max depth
    if start_url in _seen_urls: return {}   # Prevent loops

    _seen_urls.add(start_url)
    start_url, data, found_urls = fetch(start_url)
    if data is None: return {}              # Ignore error URLs

    result = {start_url: data}
    for url in found_urls:
        result.update(crawl(
            url, max_depth, _depth=_depth+1, _seen_urls=_seen_urls))
    return result


def main():
    result = crawl(argv[1], int(argv[2]))
    print('Found %d urls' % len(result))
    for url, data in result.items():
        print('%10d bytes: %s' % (len(data), url))


if __name__ == '__main__':
    main()
