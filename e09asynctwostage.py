#!/usr/bin/env python3

"""
./e09asynctwostage.py http://camlistore.org 1 6
Found 10 urls
http://camlistore.org/ frequencies: [('camlistore', 13), ...]
...


First integer arg is depth, second is minimum word count.
"""

import re
from sys import argv

import asyncio
from e01extract import canonicalize
from e04twostage import print_popular_words
from e06asyncextract import extract_async


@asyncio.coroutine
def wordcount_async(data, word_length):
    counts = {}
    for match in re.finditer('\w{%d,100}' % word_length, data):
        word = match.group(0).lower()
        counts[word] = counts.get(word, 0) + 1
    return counts


@asyncio.coroutine
def extract_count_async(url, word_length):
    _, data, found_urls = yield from extract_async(url)
    top_word = yield from wordcount_async(data, word_length)
    return url, top_word, found_urls


@asyncio.coroutine
def twostage_async(to_fetch, seen_urls, word_length):
    futures, results = [], []
    for url in to_fetch:
        if url in seen_urls: continue
        seen_urls.add(url)
        futures.append(extract_count_async(url, word_length))

    for future in asyncio.as_completed(futures):
        try:
            results.append((yield from future))
        except Exception:
            continue

    return results


@asyncio.coroutine
def crawl_async(start_url, max_depth, word_length):
    seen_urls = set()
    to_fetch = [canonicalize(start_url)]
    results = []
    for depth in range(max_depth + 1):
        batch = yield from twostage_async(to_fetch, seen_urls, word_length)
        to_fetch = []
        for url, data, found_urls in batch:
            results.append((url, data))
            to_fetch.extend(found_urls)

    return results


def main():
    # Bridge the gap between sync and async
    future = asyncio.Task(crawl_async(argv[1], int(argv[2]), int(argv[3])))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()

    result = future.result()
    print_popular_words(result)


if __name__ == '__main__':
    main()
