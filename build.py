#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import sys
import shutil
import os
import urllib.request


SVG_PATH_PATTERN = re.compile(r'path d="([\s\w\-\.,]*)"')

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


def generate_icon_dataset():
    with open('./node_modules/simple-icons/_data/simple-icons.json') as f:
        data = json.load(f)['icons']


    for icon in data:
        slug = slugify(icon['title'])

        with open(f'./node_modules/simple-icons/icons/{slug}.svg') as f:
            svg_data = f.read()

        icon['slug'] = slug
        icon['svg'] = svg_data

        match = SVG_PATH_PATTERN.search(svg_data)

        if match is None:
            raise Exception(f'failed to parse SVG path for {slug}')

        icon['path'] = match.group(1)

    return data


def generate_crate():
    shutil.rmtree('./crate', ignore_errors=True)
    os.makedirs('./crate/src')

    expand_icon = lambda i: f"\"{i['slug']}\" => Icon{{title: \"{i['title']}\", slug: \"{i['slug']}\", hex: \"{i['hex']}\", source: \"{i['source']}\", svg: \"{i['svg']}\", path: \"{i['path']}\"}},"
    expand_all_icons = lambda ds: '\n        '.join([expand_icon(icon) for icon in ds])

    with open('./crate/Cargo.toml', 'w') as f:
        f.write(f'''[package]
name = "simple-icons"
version = "{get_npm_version()}"
authors = ["Mihir Singh <git.service@mihirsingh.com>"]
edition = "2018"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
''')

    with open('./crate/src/lib.rs', 'w') as f:
        f.write(f'''pub struct Icon {{
    title: String,
    slug: String,
    hex: String,
    source: String,
    svg: String,
    path: String,
}}

pub fn get(name: &str) -> Option<Icon> {{
    match name {{
        {expand_all_icons(generate_icon_dataset())}
        _ => None
    }}
}}
''')


if __name__ == '__main__':
    if get_npm_version() == get_crate_version():
        print('crate in-sync with npm; exiting')
        sys.exit(0)

    generate_crate()