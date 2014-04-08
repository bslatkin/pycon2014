#!/usr/bin/env python3

"""
./e04twostage.py http://camlistore.org 1 6
Found 10 urls
http://camlistore.org/ most popular word : ('Camlistore', 9)
http://camlistore.org/download most popular word : ('release', 10)
...


First integer is depth, second is minimum word count.
"""

from queue import Queue
import re
from sys import argv
from threading import Thread

from e01fetch import canonicalize, fetch


def wordcount(start_url, max_depth, word_length):
    fetch_queue = Queue()  # (crawl_depth, url)
    fetch_queue.put((0, canonicalize(start_url)))
    count_queue = Queue()  # (url, data)

    seen_urls = set()
    func = lambda: fetcher(fetch_queue, max_depth, seen_urls, count_queue)
    for _ in range(3):
        Thread(target=func, daemon=True).start()

    result = {}
    func = lambda: counter(count_queue, word_length, result)
    for _ in range(3):
        Thread(target=func, daemon=True).start()

    fetch_queue.join()
    count_queue.join()
    return result


def fetcher(fetch_queue, max_depth, seen_urls, output_queue):
    while True:
        depth, url = fetch_queue.get()
        try:
            if depth > max_depth: continue  # Ignore URLs that are too deep
            if url in seen_urls: continue   # Prevent infinite loops

            seen_urls.add(url)              # GIL :/
            data, found_urls = fetch(url)
            if data is None: continue       # Ignore error URLs

            output_queue.put((url, data))
            for found in found_urls:
                fetch_queue.put((depth + 1, found))
        finally:
            fetch_queue.task_done()


def counter(count_queue, word_length, result):
    while True:
        url, data = count_queue.get()
        try:
            counts = {}
            for match in re.finditer('\w{%d,100}' % word_length, data):
                word = match.group(0)
                counts[word] = counts.get(word, 0) + 1

            ranked_words = list(counts.items())
            ranked_words.sort(key=lambda x: x[1], reverse=True)
            if not ranked_words:
                result[url] = ''
            else:
                result[url] = ranked_words[0]  # GIL :(
        finally:
            count_queue.task_done()


def main():
    result = wordcount(argv[1], int(argv[2]), int(argv[3]))
    print('Found %d urls' % len(result))
    for url, popular_word in result.items():
        print('%s most popular word : %s' % (url, popular_word))


if __name__ == '__main__':
    main()
