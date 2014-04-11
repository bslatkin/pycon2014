#!/usr/bin/env python3

"""
./e10asyncfanin.py http://camlistore.org 1 6
#1 word,  107 occurrences: camlistore
...


First integer arg is depth, second is minimum word count.
"""

from sys import argv

import asyncio
from e05threadfanin import print_top_words
from e09asynctwostage import crawl_async


def main():
    # Bridge the gap between sync and async
    future = asyncio.Task(crawl_async(argv[1], int(argv[2]), int(argv[3])))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    loop.close()

    result = future.result()
    print_top_words(result)


if __name__ == '__main__':
    main()
