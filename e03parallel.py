#!/usr/bin/env python3

"""
./e03parallel.py http://camlistore.org 2
Found 37 urls
...
"""

from queue import Queue
from sys import argv
from threading import Thread

from e01extract import canonicalize, extract
from e02crawl import print_crawl


def crawl_parallel(start_url, max_depth):
    fetch_queue = Queue()  # (crawl_depth, url)
    fetch_queue.put((0, canonicalize(start_url)))

    seen_urls, result = set(), []
    func = lambda: consumer(fetch_queue, max_depth, seen_urls, result)
    for _ in range(3):
        Thread(target=func, daemon=True).start()

    fetch_queue.join()
    return result


def consumer(fetch_queue, max_depth, seen_urls, result):
    while True:
        depth, url = fetch_queue.get()
        try:
            if depth > max_depth: continue
            if url in seen_urls: continue      # GIL :|

            seen_urls.add(url)                 # GIL :/
            try:
                _, data, found_urls = extract(url)
            except Exception:
                continue

            result.append((depth, url, data))  # GIL :(
            for found in found_urls:
                fetch_queue.put((depth + 1, found))
        finally:
            fetch_queue.task_done()


def main():
    result = crawl_parallel(argv[1], int(argv[2]))
    print_crawl(result)


if __name__ == '__main__':
    main()
