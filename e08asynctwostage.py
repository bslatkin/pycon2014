#!/usr/bin/env python3

"""
./e07asynccrawl.py http://camlistore.org 2
Found 37 urls
Depth  0  http://camlistore.org/                                   3681 bytes
Depth  1  http://camlistore.org/code                               4237 bytes
Depth  1  http://camlistore.org/community                          2180 bytes
...
"""

import re
from sys import argv

import asyncio
from e01fetch import canonicalize
from e04twostage import print_popular_word
from e06asyncfetch import fetch_async


@asyncio.coroutine
def wordcount(data, word_length):
    counts = {}
    for match in re.finditer('\w{%d,100}' % word_length, data):
        word = match.group(0)
        counts[word] = counts.get(word, 0) + 1

    if not counts:
        return ''

    ranked_words = list(counts.items())
    ranked_words.sort(key=lambda x: x[1], reverse=True)
    return ranked_words[0]


@asyncio.coroutine
def fetch_and_wordcount(url, word_length):
    _, data, found_urls = yield from fetch_async(url)
    top_word = yield from wordcount(data, word_length)
    return url, top_word, found_urls


@asyncio.coroutine
def crawl(start_url, max_depth, word_length):
    seen_urls = set()
    to_fetch = [(0, canonicalize(start_url))]
    results = {}
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
                url, top_word, found_urls = yield from future
            except Exception:
                continue

            results[url] = top_word
            for url in found_urls:
                to_fetch.append((depth+1, url))

    return results



def main():
    # Bridge the gap between sync and async
    future = asyncio.Task(crawl(argv[1], int(argv[2]), int(argv[3])))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()

    result = future.result()
    print_popular_word(result)


if __name__ == '__main__':
    main()
