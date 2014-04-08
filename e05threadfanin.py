#!/usr/bin/env python3

"""
./e05threadfanin.py http://camlistore.org 1 5
#0 word,  107 occurrences: camlistore
#1 word,   45 occurrences: class
...


First integer is depth, second is minimum word count.
"""

from queue import Queue
import re
from sys import argv
from threading import Thread

from e04twostage import canonicalize, fetcher


def wordcount(start_url, max_depth, word_length):
    fetch_queue = Queue()  # (crawl_depth, url)
    fetch_queue.put((0, canonicalize(start_url)))
    count_queue = Queue()  # (url, data)

    seen_urls = set()
    func = lambda: fetcher(fetch_queue, max_depth, seen_urls, count_queue)
    for _ in range(3):
        Thread(target=func, daemon=True).start()

    result_queue = Queue()  # (url, {word: count})
    func = lambda: counter(count_queue, word_length, result_queue)
    for _ in range(3):
        Thread(target=func, daemon=True).start()

    done_object = object()
    output_queue = Queue()  # Will contain the single, final result
    func = lambda: fan_in(result_queue, output_queue, done_object)
    Thread(target=func, daemon=True).start()

    fetch_queue.join()
    count_queue.join()
    result_queue.put(done_object)  # Special signal for "done" :/

    return output_queue.get()


def counter(count_queue, word_length, result_queue):
    while True:
        url, data = count_queue.get()
        try:
            counts = {}
            for match in re.finditer('\w{%d,100}' % word_length, data):
                word = match.group(0).lower()
                counts[word] = counts.get(word, 0) + 1
            result_queue.put((url, counts))
        finally:
            count_queue.task_done()


def fan_in(result_queue, output_queue, done_object):
    total_counts = {}
    while True:
        found = result_queue.get()
        if found is done_object: break  # Receive stop signal :((
        url, counts = found
        for word, count in counts.items():
            total_counts[word] = total_counts.get(word, 0) + count
        # XX How else could you leave this loop? Output results every time?

    output_queue.put(total_counts)


def get_top_words(counts):
    ranked_words = list(counts.items())
    ranked_words.sort(key=lambda x: x[1], reverse=True)
    message = []
    for rank, (word, count) in enumerate(ranked_words[:10]):
        message.append('#%d word, %4d occurrences: %s\n' % (rank, count, word))
    return ''.join(message)


def print_top_words(counts):
    print(get_top_words(counts))


def main():
    counts = wordcount(argv[1], int(argv[2]), int(argv[3]))
    print_top_words(counts)


if __name__ == '__main__':
    main()
