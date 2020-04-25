#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import sys
import shutil
import os
import urllib.request

from peche import setup
from peche.logging import Level
from peche.logging.handlers import StdoutColour

_, log = setup('simple-icons-rs-builder')

SVG_PATH_PATTERN = re.compile(r'path d="([\s\w\-\.,]*)"')

SVG_ESCAPE_RULES = [
    (re.compile(r'"'), '\\"')
]

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

    log.debug('retrieved current NPM package version', version=data['dist-tags']['latest'])

    return data['dist-tags']['latest']


def get_crate_version():
    with urllib.request.urlopen('https://crates.io/api/v1/crates/docker') as response:
        data = json.load(response)

    version = [x for x in data['versions'] if x['id'] == sorted(data['crate']['versions'])[-1]][0]['num']

    log.debug('retrieved current crates.io package version', version=version)


    return version


def slugify(title):
    slug = title.lower()

    for rule in SLUGIFY_RULES:
        slug = rule[0].sub(rule[1], slug)


    log.debug('generated slug for title', title=title, slug=slug)

    return slug


def escape_svg(data):
    for rule in SVG_ESCAPE_RULES:
        data = rule[0].sub(rule[1], data)

    return data


def generate_icon_dataset():
    with open('./node_modules/simple-icons/_data/simple-icons.json') as f:
        data = json.load(f)['icons']


    for icon in data:
        log.debug('generating data for icon', icon_title=icon['title'])

        slug = slugify(icon['title'])

        with open(f'./node_modules/simple-icons/icons/{slug}.svg') as f:
            svg_data = f.read()

        icon['slug'] = slug
        icon['svg'] = escape_svg(svg_data)

        match = SVG_PATH_PATTERN.search(svg_data)

        if match is None:
            raise Exception(f'failed to parse SVG path for {slug}')

        icon['path'] = match.group(1)

    return data


def generate_crate(version):
    shutil.rmtree('./crate', ignore_errors=True)
    os.makedirs('./crate/src')

    expand_icon = lambda i: f"\"{i['slug']}\" => Some(Icon{{title: \"{i['title']}\", slug: \"{i['slug']}\", hex: \"{i['hex']}\", source: \"{i['source']}\", svg: \"{i['svg']}\", path: \"{i['path']}\"}}),"
    expand_all_icons = lambda ds: '\n        '.join([expand_icon(icon) for icon in ds])

    log.debug('generating crate file', file='Cargo.toml')

    with open('./crate/Cargo.toml', 'w') as f:
        f.write(f'''[package]
name = "simple-icons"
version = "{version}"
authors = ["Mihir Singh <git.service@mihirsingh.com>"]
edition = "2018"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
''')

    log.debug('generating source file', file='lib.rs')

    with open('./crate/src/lib.rs', 'w') as f:
        f.write(f'''#[derive(Debug)]
pub struct Icon {{
    pub title: &'static str,
    pub slug: &'static str,
    pub hex: &'static str,
    pub source: &'static str,
    pub svg: &'static str,
    pub path: &'static str,
}}

pub fn get(name: &str) -> Option<Icon> {{
    match name {{
        {expand_all_icons(generate_icon_dataset())}
        _ => None
    }}
}}
''')

    log.info('finished generating crate', version=version)


if __name__ == '__main__':
    log.level = Level.Debug
    log.drop_handlers()
    log.add_handler(StdoutColour)

    log.info('starting crate builder')

    npm_version = get_npm_version()
    crate_version = get_crate_version()

    if npm_version == crate_version:
        log.error('crate in-sync with npm; exiting')
        sys.exit(0)

    generate_crate(npm_version)