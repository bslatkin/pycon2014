#!/usr/bin/env python3

import re
from sys import argv
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import urlunparse


URL_EXPR = re.compile('http(s?)://[^"\'\s\\\\]+')


def canonicalize(url):
    parts = list(urlparse(url))
    if parts[2] == '':
        parts[2] = '/'
    return urlunparse(parts)


def crawl(url):
    domain = urlparse(url).netloc
    response = urlopen(url)
    assert response.status == 200
    data = response.read().decode('utf-8')
    found_urls = set()
    for match in URL_EXPR.finditer(data):
        found = canonicalize(match.group(0))
        if domain in found and found != url:
            found_urls.add(found)
    return data, found_urls



data, urls = crawl(canonicalize(argv[1]))

print('%d bytes, %d urls:\n%s' % (len(data), len(urls), '\n'.join(urls)))
