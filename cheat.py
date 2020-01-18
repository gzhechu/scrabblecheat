#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Jan 13 16:09:50 2020

@author: hechu
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
from tornado.options import define, options
import time
from itertools import permutations

from trie import Trie


def load(words, filepath, src=None):
    n = 1
    with open(filepath) as fp:
        line = fp.readline().strip()
        while line:
            wl = line.split("\t")
            word = abbr = desc = ""
            try:
                word = wl[0].lower()
            except IndexError:
                pass
            try:
                abbr = wl[1]
            except IndexError:
                pass
            try:
                desc = wl[2]
            except IndexError:
                pass
            wd = {}
            wd["word"] = word
            wd["abbr"] = abbr
            wd["desc"] = desc
            wd["source"] = set()
            if src is not None:
                wd["source"].add(src)

            if word in words:
                words[word]["source"].add(src)
            else:
                words[word] = wd
            # print("{} {}".format(n, wd))
            line = fp.readline().strip()
            n += 1
    return words


def segment(lstr):
    base = lstr.lower()
    seg = []
    for i in range(2, len(base) + 1):
        s = set(map("".join, permutations(base, r=i)))
        for w in s:
            seg.append(w)
    return seg


# Trie object
trie_obj = Trie()
vocabularys = {}


def init(t, v):
    load(v, "dict/pet2020.txt", "pet")
    load(v, "dict/TWL06.txt", "twl")
    # load(v, "dict/hello.txt", "hello")
    print(len(v))
    print(v["hello"])

    words = []
    for key in vocabularys.keys():
        words.append(key)

    for word in words:
        # print(word)
        try:
            t.insert(word)
        except IndexError:
            pass


def search(trie, base, vocabulary):
    # start = time.process_time()
    segs = segment(base)
    print(len(segs))
    # print(segs)
    words = []
    for seg in segs:
        if (trie.search(seg)):
            w = vocabulary[seg]
            words.append(w)
    # print("time consuming: {}s".format(time.process_time() - start))
    return words


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler), (r"/cheatsocket", CheatSocketHandler)]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # self.render("index.html", messages=CheatSocketHandler.cache)
        self.render("index.html", messages=[])


class CheatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    # cache = []
    # cache_size = 200

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        CheatSocketHandler.waiters.add(self)

    def on_close(self):
        CheatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def send_words(self, chat):
        self.write_message(chat)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        base = parsed["body"]
        if base == "":
            return

        logging.info("got message: {}".format(base))
        chat = {"id": "clear", "word": base, "abbr": "", "desc": "", "src": ""}
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat)
        )
        # logging.info("chat['html']: {}".format(chat["html"]))
        self.send_words(chat)
        wl = search(trie_obj, base, vocabularys)
        for w in wl:
            # logging.info("word: {}".format(w))
            chat = {"id": str(uuid.uuid4()),
                    "word": w['word'], "abbr": w["abbr"], "desc": w["desc"], "src": repr(w['source'])}
            chat["html"] = tornado.escape.to_basestring(
                self.render_string("message.html", message=chat)
            )
            # logging.info("send message: {}".format(chat))
            self.send_words(chat)


define("port", default=8888, help="run on the given port", type=int)


def test2():
    init(trie_obj, vocabularys)
    wl = search(trie_obj, "ABCDEFG", vocabulary)
    for w in wl:
        print(w)
    pass


def test1():
    base = 'absiifg'
    print(len(segment(base)))


def main():
    init(trie_obj, vocabularys)
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
    # test1()
    # test2()
