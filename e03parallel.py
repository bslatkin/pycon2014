#!/usr/bin/env python3

"""
./e03parallel.py http://camlistore.org 2
Found 37 urls
...
"""

from queue import Queue
from sys import argv
from threading import Thread

from e01fetch import fetch


def crawl_parallel(start_url, max_depth):
    fetch_queue = Queue()  # (crawl_depth, url)
    fetch_queue.put((0, start_url))

    seen_urls, result = set(), {}
    func = lambda: consumer(fetch_queue, max_depth, seen_urls, result)
    for _ in range(3):
        Thread(target=func, daemon=True).start()

    fetch_queue.join()
    return result


def consumer(fetch_queue, max_depth, seen_urls, result):
    while True:
        depth, url = fetch_queue.get()
        try:
            if depth > max_depth: continue  # Ignore URLs that are too deep
            if url in seen_urls: continue   # Prevent infinite loops

            seen_urls.add(url)              # Relies on the GIL :/
            url, data, found_urls = fetch(url)
            if data is None: continue       # Ignore error URLs

            result[url] = data              # Relies on the GIL :(
            for found in found_urls:
                fetch_queue.put((depth + 1, found))
        finally:
            fetch_queue.task_done()


def main():
    result = crawl_parallel(argv[1], int(argv[2]))
    print('Found %d urls' % len(result))
    for url, data in result.items():
        print('%10d bytes: %s' % (len(data), url))


if __name__ == '__main__':
    main()
