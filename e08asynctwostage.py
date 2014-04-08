#!/usr/bin/env python3

"""
./e07asynccrawl.py http://camlistore.org 2
Found 37 urls
Depth  0  http://camlistore.org/                                   3681 bytes
Depth  1  http://camlistore.org/code                               4237 bytes
Depth  1  http://camlistore.org/community                          2180 bytes
...
"""

from sys import argv
from urllib.parse import urljoin

import asyncio
from e01fetch import canonicalize, same_domain, URL_EXPR
from e04twostage import print_popular_word


@asyncio.coroutine
def fetch(url):
    data = yield from get_url(url)
    if data is None:
        return None, None, []  # Error
    found_urls = set()
    for match in URL_EXPR.finditer(data):
        found = canonicalize(match.group('url'))
        if same_domain(url, found):
            found_urls.add(urljoin(url, found))
    return data, sorted(found_urls)


@asyncio.coroutine
def wordcount(data, word_length):
    counts = {}
    for match in re.finditer('\w{%d,100}' % word_length, data):
        word = match.group(0)
        counts[word] = counts.get(word, 0) + 1

    ranked_words = list(counts.items())
    ranked_words.sort(key=lambda x: x[1], reverse=True)
    if not ranked_words:
        top_word = ''
    else:
        top_word = ranked_words[0]

    return top_word


@asyncio.coroutine
def fetch_and_wordcount(url, word_length):
    data, found_urls = yield from fetch(url)
    if data is None:
        raise



@asyncio.coroutine
def crawl(start_url, max_depth):
    seen_urls = set()
    to_fetch = [(0, canonicalize(start_url))]
    results = []
    while to_fetch:
        futures = []
        for depth, url in to_fetch:
            if depth > max_depth: continue
            if url in seen_urls: continue
            seen_urls.add(url)
            futures.append(fetch(url))  # Parallel kickoff

        to_fetch = []
        for future in asyncio.as_completed(futures):  # Prioritized wait
            url, data, found_urls = yield from future
            for url in found_urls:
                to_fetch.append((depth+1, url))

        if data is not None:
            results.append((depth, url, data))

    return results


@asyncio.coroutine
def crawl(start_url, max_depth, word_length, depth=0, seen_urls=None):
    if depth > max_depth: return []
    if seen_urls is None: seen_urls = set()
    if url in seen_urls: return []
    seen_urls.add(url)

    futures = []
    url, data, found_urls = yield from fetch(url)
    if data is not None:
        futures.append(wordcount(depth, url, data, word_length))

    for found in found_urls:
        futures.append(crawl(
            found, max_depth, depth=depth+1, seen_urls=seen_urls))

    for future in asyncio.as_completed(futures):
        results.extend((yield from future))

    return result


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
