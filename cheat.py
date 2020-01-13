#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 16:09:50 2020

@author: hechu
"""

from trie import Trie
import time
from itertools import product
from itertools import combinations
from itertools import permutations


def loadWordsFromFile(filepath):
    words = {}
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
            words[word] = wd
            # print("{} {}".format(n, word))
            line = fp.readline().strip()
            n += 1
    return words


def searchWord(word, trie, words):
    if (trie.search(word)):
        return words[word]
    return None


def segment(letters):
    base = letters.lower()
    seg = []
    for i in range(2, len(base) + 1):
        s = set(map("".join, permutations(base, r=i)))
        for w in s:
            seg.append(w)
    return seg


def main():
    # twl = loadWordsFromFile("dict/pet2020.txt")
    twl = loadWordsFromFile("dict/TWL06.txt")
    print(len(twl))

    words = []
    for key in twl.keys():
        words.append(key)

    # Trie object
    t = Trie()

    # Construct trie
    for word in words:
        # print(word)
        try:
            t.insert(word)
        except IndexError:
            pass

    words = ["the", "these", "their", "thaw", "about"]
    base = 'atsfefu'
    lst = list(map(" ".join, list(base)))
    print("optional letters are: {}\n".format(lst))

    start = time.process_time()

    words = segment(base)
    # print(len(words))

    for word in words:
        e = searchWord(word, t, twl)
        if e is not None:
            print("word: [{}], abbr: {}".format(
                e["word"], e["abbr"], e["desc"]))
        # else:
        #     print("- '{}' not found.".format(word))

    # your code here
    print("time consuming: {}s".format(time.process_time() - start))


def test1():
    base = 'absiefg'
    print(len(segment(base)))


if __name__ == '__main__':
    main()
    # test1()
