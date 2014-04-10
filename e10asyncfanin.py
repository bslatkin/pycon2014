#!/usr/bin/env python3

"""
./e10asyncfanin.py http://camlistore.org 1 6
#0 word,  107 occurrences: camlistore
#1 word,   39 occurrences: content
...


First integer arg is depth, second is minimum word count.
"""

from sys import argv

import asyncio
from e06asynctwostage import crawl_async


@asyncio.coroutine
def wordcount_global_async(start_url, max_depth, word_length):
    result = yield from crawl_async(start_url, max_depth, word_length)



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
