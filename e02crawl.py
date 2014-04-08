#!/usr/bin/env python3

"""
./e02crawl.py http://camlistore.org 2
      4237 bytes: http://camlistore.org/docs/contributing
      4147 bytes: http://camlistore.org/docs/
      3681 bytes: http://camlistore.org/
     54345 bytes: http://camlistore.org/pkg/search
     55017 bytes: http://camlistore.org/pkg/schema
      1596 bytes: http://camlistore.org/docs/todo
     36372 bytes: http://camlistore.org/pkg/client
      2099 bytes: http://camlistore.org/docs/protocol
"""

from sys import argv

from e01fetch import fetch


def crawl(start_url, max_depth, _depth=0, _seen_urls=None):
    if _seen_urls is None:
        _seen_urls = set()
    if _depth > max_depth:
        return {}
    start_url, data, found_urls = fetch(start_url)
    if data is None:
        return {}
    result = {start_url: data}
    for url in found_urls:
        if url is None:
            continue  # Ignore error URLs
        if url in _seen_urls:
            continue  # Prevent infinite loops
        _seen_urls.add(url)
        result.update(crawl(
            url, max_depth, _depth=_depth+1, _seen_urls=_seen_urls))
    return result


def main():
    result = crawl(argv[1], int(argv[2]))
    for url, data in result.items():
        print('%10d bytes: %s' % (len(data), url))


if __name__ == '__main__':
    main()
