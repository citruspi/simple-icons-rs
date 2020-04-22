#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import urllib.request


SLUGIFY_RULES = [
    (re.compile(r'\+'), 'plus'),
    (re.compile(r'^\.'), 'dot-'),
    (re.compile(r'\.$'), '-dot'),
    (re.compile(r'\.'), '-dot-'),
    (re.compile(r'^&'), 'and-'),
    (re.compile(r'&$'), '-and'),
    (re.compile(r'&'), '-and-'),
    (re.compile(r'[ !:’\']'), ''),
    (re.compile(r'à|á|â|ã|ä', re.IGNORECASE), 'a'),
    (re.compile(r'ç|č|ć', re.IGNORECASE), 'c'),
    (re.compile(r'è|é|ê|ë', re.IGNORECASE), 'e'),
    (re.compile(r'ì|í|î|ï', re.IGNORECASE), 'i'),
    (re.compile(r'ñ|ň|ń', re.IGNORECASE), 'n'),
    (re.compile(r'ò|ó|ô|õ|ö', re.IGNORECASE), 'o'),
    (re.compile(r'š|ś', re.IGNORECASE), 's'),
    (re.compile(r'ù|ú|û|ü', re.IGNORECASE), 'u'),
    (re.compile(r'ý|ÿ', re.IGNORECASE), 'y'),
    (re.compile(r'ž|ź', re.IGNORECASE), 'z'),
]


def get_npm_version():
    with urllib.request.urlopen('https://registry.npmjs.org/simple-icons') as response:
        data = json.load(response)

    return data['dist-tags']['latest']


def get_crate_version():
    with urllib.request.urlopen('https://crates.io/api/v1/crates/docker') as response:
        data = json.load(response)

    lateste_version_id = sorted(data['crate']['versions'])[-1]

    return [x for x in data['versions'] if x['id'] == lateste_version_id][0]['num']


def slugify(title):
    for rule in SLUGIFY_RULES:
        title = rule[0].sub(rule[1], title)

    return title.lower()
