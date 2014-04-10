#!/usr/bin/env python3

"""
./e10asyncfanin.py http://camlistore.org 1 6
#0 word,  107 occurrences: camlistore
#1 word,   39 occurrences: content
...


First integer arg is depth, second is minimum word count.
"""

import re
from sys import argv

import asyncio
from e01extract import canonicalize
from e05threadfanin import print_top_words
from e06asyncextract import fetch_async


@asyncio.coroutine
def wordcount(data, word_length):
    counts = {}
    for match in re.finditer('\w{%d,100}' % word_length, data):
        word = match.group(0).lower()
        counts[word] = counts.get(word, 0) + 1
    return counts


@asyncio.coroutine
def fetch_and_wordcount(url, word_length):
    _, data, found_urls = yield from fetch_async(url)
    counts = yield from wordcount(data, word_length)
    return url, counts, found_urls


@asyncio.coroutine
def crawl(start_url, max_depth, word_length):
    seen_urls = set()
    to_fetch = [(0, canonicalize(start_url))]
    counts = {}
    while to_fetch:
        futures = []
        for depth, url in to_fetch:
            if depth > max_depth: continue
            if url in seen_urls: continue
            seen_urls.add(url)
            futures.append(fetch_and_wordcount(url, word_length))

        to_fetch = []

        for future in asyncio.as_completed(futures):
            try:
                url, words_dict, found_urls = yield from future
            except Exception:
                continue

            for word, count in words_dict.items():
                counts[word] = counts.get(word, 0) + count
            for url in found_urls:
                to_fetch.append((depth+1, url))

    return counts


def main():
    # Bridge the gap between sync and async
    future = asyncio.Task(crawl(argv[1], int(argv[2]), int(argv[3])))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()

    result = future.result()
    print_top_words(result)


if __name__ == '__main__':
    main()
