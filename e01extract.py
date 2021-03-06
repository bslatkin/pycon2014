#!/usr/bin/env python3

"""
./e01extract.py http://camlistore.org
INFO:root:Fetching http://camlistore.org/
http://camlistore.org/ is 3681 bytes, 11 urls:
http://camlistore.org/
...
"""

import logging
logging.getLogger().setLevel(logging.INFO)
import re
from sys import argv
from urllib.request import urlopen
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse


URL_EXPR = re.compile(
    '([a-zA-Z]+\s*=\s*["\'])'   # Tag attribute: href="
    '(?P<url>'
        '((http(s?):)?'         # Optional scheme
        '//[^"\'\s\\\\</]+)?'   # Optional domain
        '/[^"\'\s\\\\<]*'       # Required path
    ')')


def canonicalize(url):
    parts = list(urlparse(url))
    if parts[2] == '':
        parts[2] = '/'  # Empty path equals root path
    parts[5] = ''       # Erase fragment
    return urlunparse(parts)


def fetch(url):
    logging.info('Fetching %s', url)
    response = urlopen(url, timeout=5)
    assert response.status == 200
    data = response.read()
    assert data
    return data.decode('utf-8')


def same_domain(a, b):
    parsed_a = urlparse(a)
    parsed_b = urlparse(b)
    if parsed_a.netloc == parsed_b.netloc:
        return True
    if (parsed_a.netloc == '') ^ (parsed_b.netloc == ''):  # Relative paths
        return True
    return False


def extract(url):
    data = fetch(url)
    found_urls = set()
    for match in URL_EXPR.finditer(data):
        found = canonicalize(match.group('url'))
        if same_domain(url, found):
            found_urls.add(urljoin(url, found))
    return url, data, sorted(found_urls)


def main():
    url = argv[1]
    _, data, found_urls = extract(url)
    print('%s is %d bytes, %d urls:\n%s' %
          (url, len(data), len(found_urls), '\n'.join(found_urls)))


if __name__ == '__main__':
    main()
