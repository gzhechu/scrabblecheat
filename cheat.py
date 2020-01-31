#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Jan 13 16:09:50 2020
@author: hechu

# some word list:
# https://github.com/mahavivo/english-wordlists

# score table from:
# https://zh.wikipedia.org/wiki/Scrabble

"""

import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado.options import define, options

import zipfile
import logging
import os.path
import uuid
import time
import re
from itertools import permutations

from trie import Trie


class Word():
    score_table = {'e': 1, 's': 1, 'a': 1, 'i': 1, 'r': 1, 'o': 1,
                   'n': 1, 't': 1, 'l': 1, 'd': 2, 'u': 1, 'c': 3,
                   'g': 2, 'p': 3, 'm': 3, 'h': 4, 'b': 3, 'y': 4,
                   'k': 5, 'f': 4, 'w': 4, 'v': 4, 'z': 10, 'x': 8,
                   'j': 8, 'q': 10}

    def __init__(self, word, src=None):
        self.word = word
        self.score = 0
        self._score()
        self.source = set()
        if src is not None:
            self.source.add(src)
        self.abbr = ""
        self.desc = ""
        pass

    def _score(self):
        self.score = 0
        if self.word is None:
            return
        for c in self.word:
            try:
                self.score += self.score_table[c]
                # print(c, self.score_table[c])
            except KeyError:
                pass


class ScabblerCheat():
    def __init__(self):
        self.wordlist = {}
        # Trie object
        self.trie = Trie()
        pass

    def load(self, filepath, src=None):
        if not os.path.exists(filepath):
            zipedfile = filepath + ".zip"
            zipfolder = "./dict/" # fix it later.
            print("unzip file: {}".format(zipedfile))
            with zipfile.ZipFile(zipedfile, 'r') as zip_ref:
                zip_ref.extractall(zipfolder)

        new_words = []
        with open(filepath) as fp:
            line = fp.readline().strip()
            while line:
                wl = line.split("\t")
                word = abbr = desc = ""
                try:
                    word = wl[0].lower()
                except IndexError:
                    pass

                # try:
                #     abbr = wl[1]
                # except IndexError:
                #     pass
                # try:
                #     desc = wl[2]
                # except IndexError:
                #     pass

                wd = Word(word, src)
                if word in self.wordlist:
                    self.wordlist[word].source.add(src)
                else:
                    self.wordlist[word] = wd
                    new_words.append(word)

                # print("{} {}".format(n, wd))
                line = fp.readline().strip()

        for word in new_words:
            # print(word)
            try:
                self.trie.insert(word)
            except IndexError:
                pass
        print("load {} new {} words from file".format(len(new_words), src))

    def combinations(self, lstr, prefix="", contains="", postfix=""):
        base = lstr.lower()
        seg = []
        for i in range(2, len(base) + 1):
            # use Set to ensure uniq word in the possible solve.
            slist = set(map("".join, permutations(base, r=i)))

            # print("len of posible 1 is {}".format(len(slist)))
            # regex = re.compile(r"a{3}")
            # slist = list(filter(regex.search, slist))
            # print("len of posible 2 is {}".format(len(slist)))
            # print(slist)

            # regex = re.compile(r"{0}".format(contains))
            # slist = list(filter(regex.search, slist))
            # seg.extend(slist)

            for word in slist:
                # print(len(word))
                # print(word)
                if not contains in word:
                    continue
                if not word.startswith(prefix):
                    continue
                if not word.endswith(postfix):
                    continue
                seg.append(word)
        return seg

    def search(self, lstr, prefix="", contains="", postfix=""):
        if (len(lstr) > 8):
            return []

        # print("[{}], [{}], [{}], [{}]".format(lstr, prefix, contains, postfix))
        lstr += prefix
        lstr += contains
        lstr += postfix
        # print("{} letters: {}".format(len(lstr), list(lstr)))

        if len(lstr) > 10:
            return []

        combines = self.combinations(lstr, prefix.lower(),
                                     contains.lower(), postfix.lower())
        # print("search from {} possible solve.".format(len(combines)))
        words = []
        for word in combines:
            if (self.trie.search(word)):
                w = self.wordlist[word]
                words.append(w)
        # print("time consuming: {}s".format(time.process_time() - start))
        return sorted(words, key=lambda w: w.score, reverse=True)
        # return words


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
        # self.render("index.html", messages=[])
        # logging.info("request from: {}".format(self.request.remote_ip))


class CheatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        CheatSocketHandler.waiters.add(self)

    def on_close(self):
        CheatSocketHandler.waiters.remove(self)

    def on_message(self, message):
        base = ""
        prefix = ""
        contains = ""
        postfix = ""

        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        base = parsed["body"].strip().replace(" ", "")
        prefix = parsed["prefix"].strip().replace(" ", "")
        contains = parsed["contains"].strip().replace(" ", "")
        postfix = parsed["postfix"].strip().replace(" ", "")

        if base == "":
            return

        lstr = base + prefix
        lstr += contains
        lstr += postfix

        resp = {"id": "clear", "word": base, "abbr": "", "desc": "", "src": ""}
        resp["html"] = ""
        self.write_message(resp)

        if len(base) > 8 or len(lstr) > 10:
            resp = {"id": str(uuid.uuid4()), "word": "字母太多啦，算不过来啦！",
                    "abbr": "", "desc": "", "src": "", "score": "负分!"}
            resp["html"] = tornado.escape.to_basestring(
                self.render_string("message.html", message=resp)
            )
            self.write_message(resp)
            return

        wl = sc.search(base, prefix, contains, postfix)
        for w in wl:
            # logging.info("word: {}".format(w))
            resp = {"id": str(uuid.uuid4()), "word": w.word, "score": str(w.score),
                    "abbr": w.abbr, "desc": w.desc, "src": repr(w.source).replace("'", "")}
            resp["html"] = tornado.escape.to_basestring(
                self.render_string("message.html", message=resp)
            )
            self.write_message(resp)


define("port", default=8123, help="run on the given port", type=int)

sc = ScabblerCheat()


def init():
    tstart = time.process_time()
    sc.load("dict/high_school.txt", "高中")
    sc.load("dict/pet2020.txt", "pet")
    sc.load("dict/cet4.txt", "cet4")
    sc.load("dict/cet6.txt", "cet6")
    tend = time.process_time()
    print("time consuming: {}s".format(tend - tstart))


def test1():
    init()

    # lstr = "abceeftd"
    lstr = "abceeft"

    # tstart = time.process_time()
    # wl = sc.search(lstr)
    # tend = time.process_time()
    # for w in wl:
    #     # print(w.word, w.source, w.score)
    #     pass
    # print("time consuming: {}s".format(tend - tstart))

    tstart = time.process_time()
    wl = sc.search(lstr, "", "e", "st")
    tend = time.process_time()
    for w in wl:
        print(w.word, w.source, w.score)
        pass
    logging.info("time consuming: {}s".format(tend - tstart))


def main():
    init()
    tornado.options.parse_command_line()
    logging.info("listening on port: {}".format(options.port))
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
    # test1()
