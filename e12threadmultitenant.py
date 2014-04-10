#!/usr/bin/env python3

"""
./e12threadmultitenant.py 9999

Navigate your browser to http://localhost:9999
"""

from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
logging.getLogger().setLevel(logging.INFO)
from queue import Queue
import re
from socketserver import ThreadingMixIn
from sys import argv
from threading import Condition, Thread
from urllib.parse import parse_qsl

from e01extract import extract
from e05threadfanin import get_global_words, get_top_words_message
from e11asyncmultitenant import MY_FORM


class State(object):
    def __init__(self, start_url):
        self.start_url = start_url
        self.seen_urls = set()
        self.pending_fetches = 0
        self.pending_counts = 0
        self.results = []
        self.output = Condition()


class FetchResult(object):
    def __init__(self, state, depth, url, data, found_urls):
        self.state = state
        self.depth = depth
        self.url = url
        self.data = data
        self.found_urls = found_urls


def fetcher(fetch_queue, output_queue):
    logging.info('Starting fetcher thread')
    while True:
        state, depth, url = fetch_queue.get()
        logging.info('%s: Fetching in thread: %s', id(state), url)
        try:
            try:
                _, data, found_urls = extract(url)
            except Exception:
                data, found_urls = None, []

            output_queue.put(FetchResult(state, depth, url, data, found_urls))
        finally:
            fetch_queue.task_done()


class CountResult(object):
    def __init__(self, state, url, counts):
        self.state = state
        self.url = url
        self.counts = counts


def counter(count_queue, word_length, result_queue):
    logging.info('Starting counter thread')
    while True:
        state, url, data = count_queue.get()
        logging.info('%s: Counting in thread: %s', id(state), url)
        try:
            counts = {}
            for match in re.finditer('\w{%d,100}' % word_length, data):
                word = match.group(0).lower()
                counts[word] = counts.get(word, 0) + 1
            result_queue.put(CountResult(state, url, counts))
        finally:
            count_queue.task_done()


class Coordinator(Thread):
    def __init__(self, request_queue, fetch_queue, count_queue, max_depth,
                 **kwargs):
        Thread.__init__(self, **kwargs)
        self.request_queue = request_queue
        self.fetch_queue = fetch_queue
        self.count_queue = count_queue
        self.max_depth = max_depth

    def handle_state(self, state):
        logging.info('%s: Handling kickoff for %s', id(state), state.start_url)
        state.pending_fetches += 1
        self.fetch_queue.put((state, 0, state.start_url))

    def handle_fetch_result(self, fetch_result):
        logging.info('%s: Handling fetch result for %s',
                     id(fetch_result.state), fetch_result.url)
        state = fetch_result.state
        state.pending_fetches -= 1

        state.seen_urls.add(fetch_result.url)
        if fetch_result.data is not None:
            state.pending_counts += 1
            self.count_queue.put((state, fetch_result.url, fetch_result.data))

        next_depth = fetch_result.depth + 1
        if next_depth <= self.max_depth:
            for url in fetch_result.found_urls:
                if url in state.seen_urls: continue
                state.seen_urls.add(url)
                state.pending_fetches += 1
                self.fetch_queue.put((state, next_depth, url))

        self.maybe_notify(state)

    def handle_count_result(self, count_result):
        logging.info('%s: Handling count result for %s',
                     id(count_result.state), count_result.url)
        state = count_result.state
        state.pending_counts -= 1
        state.results.append((count_result.url, count_result.counts))
        self.maybe_notify(state)

    def maybe_notify(self, state):
        logging.info('%s: Pending fetches: %d, pending counts: %d',
                     id(state), state.pending_fetches, state.pending_counts)
        if (state.pending_fetches == 0 and
            state.pending_counts == 0):
            with state.output:
                state.output.notify()

    def run(self):
        logging.info('Coordinator started')
        while True:
            next = self.request_queue.get()
            try:
                if isinstance(next, State):
                    self.handle_state(next)
                elif isinstance(next, FetchResult):
                    self.handle_fetch_result(next)
                elif isinstance(next, CountResult):
                    self.handle_count_result(next)
                else:
                    assert False
            finally:
                self.request_queue.task_done()


def start(max_depth, word_length):
    request_queue = Queue()
    fetch_queue = Queue()
    count_queue = Queue()

    func = lambda: fetcher(fetch_queue, request_queue)
    for _ in range(3):
        Thread(target=func, daemon=True).start()

    func = lambda: counter(count_queue, word_length, request_queue)
    for _ in range(3):
        Thread(target=func, daemon=True).start()

    Coordinator(request_queue, fetch_queue, count_queue, max_depth,
                daemon=True).start()

    return request_queue


class MyHandler(BaseHTTPRequestHandler):
    request_queue = None

    def do_GET(self):
        self.wfile.write(MY_FORM.encode('utf-8'))

    def do_POST(self):
        length = min(100, int(self.headers.get('content-length', 0)))
        data = self.rfile.read(length).decode('utf-8')
        url = dict(parse_qsl(data)).get('url')
        state = State(url)
        self.request_queue.put(state)
        with state.output:
            state.output.wait()
        self.wfile.write(b'<pre>')
        top_words = get_global_words(state.results)
        message = get_top_words_message(top_words)
        self.wfile.write(escape(message).encode('utf-8'))
        self.wfile.write(b'</pre>')



class MyServer(HTTPServer, ThreadingMixIn):
    daemon_threads = True
    def __init__(self, port):
        HTTPServer.__init__(self, ('', port), MyHandler)


def main():
    port = int(argv[1])
    MyHandler.request_queue = start(1, 1)
    server = MyServer(port)
    server.serve_forever()


if __name__ == '__main__':
    main()
