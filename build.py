#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import sys
import shutil
import os
import urllib.request

from inflect import engine as num_to_word_gen
from peche import setup
from peche.logging.handlers import StdoutColour


_, log = setup('simple-icons-rs-builder')
num_to_word = num_to_word_gen().number_to_words

SVG_PATH_PATTERN = re.compile(r'path d="([\s\w\-\.,]*)"')
NUM_PATTERN = re.compile(r'(\d+)')

SVG_ESCAPE_RULES = [
    (re.compile(r'"'), '\\"')
]

COMMON_RULES = [
    (re.compile(r'[!:’\']'), ''),
    (re.compile(r'À|Á|Â|Ã|Ä'), 'a'),
    (re.compile(r'Ç|Č|Ć'), 'C'),
    (re.compile(r'È|É|Ê|Ë'), 'E'),
    (re.compile(r'Ì|Í|Î|Ï'), 'I'),
    (re.compile(r'Ñ|Ň|Ń'), 'N'),
    (re.compile(r'Ò|Ó|Ô|Õ|Ö'), 'O'),
    (re.compile(r'Š|Ś'), 'S'),
    (re.compile(r'Ù|Ú|Û|Ü'), 'U'),
    (re.compile(r'Ý|Ÿ'), 'Y'),
    (re.compile(r'Ž|Ź'), 'Z'),
    (re.compile(r'à|á|â|ã|ä'), 'a'),
    (re.compile(r'ç|č|ć'), 'c'),
    (re.compile(r'è|é|ê|ë'), 'e'),
    (re.compile(r'ì|í|î|ï'), 'i'),
    (re.compile(r'ñ|ň|ń'), 'n'),
    (re.compile(r'ò|ó|ô|õ|ö'), 'o'),
    (re.compile(r'š|ś'), 's'),
    (re.compile(r'ù|ú|û|ü'), 'u'),
    (re.compile(r'ý|ÿ'), 'y'),
    (re.compile(r'ž|ź'), 'z'),
]

SLUGIFY_RULES = [
    (re.compile(r'\+'), 'plus'),
    (re.compile(r'^\.'), 'dot-'),
    (re.compile(r'\.$'), '-dot'),
    (re.compile(r'\.'), '-dot-'),
    (re.compile(r'^&'), 'and-'),
    (re.compile(r'&$'), '-and'),
    (re.compile(r'&'), '-and-'),
    (re.compile(r'\s'), ''),
]

MODULIFY_RULES = [
    (re.compile(r'\+'), 'plus'),
    (re.compile(r'^\.'), 'dot_'),
    (re.compile(r'\.$'), '_dot'),
    (re.compile(r'\.'), '_dot_'),
    (re.compile(r'^&'), 'and_'),
    (re.compile(r'&$'), '_and'),
    (re.compile(r'&'), '_and_'),
    (re.compile(r'[\-\s]+'), '_'),
    (re.compile(r'_+'), '_'),
    (re.compile(r'^_+'), ''),
    (re.compile(r'_+$'), ''),
    (re.compile(r'^abstract$'), 'r#abstract'),
    (re.compile(r'^box$'), 'r#box'),
    (re.compile(r'^loop$'), 'r#loop'),
]

STRUCTIFY_RULES = [
    (re.compile(r'\+'), 'Plus'),
    (re.compile(r'^\.'), 'Dot_'),
    (re.compile(r'\.$'), '_Dot'),
    (re.compile(r'\.'), '_Dot_'),
    (re.compile(r'^&'), 'And_'),
    (re.compile(r'&$'), '_And'),
    (re.compile(r'&'), '_And_'),
    (re.compile(r'[\-\s_]+'), ''),
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


def sub_numbers(s, sub=' '):
    m = NUM_PATTERN.findall(s)

    if m is None:
        return m

    for g in m:
        human = ''.join([t.capitalize() for t in num_to_word(int(g)).replace('-', sub).split(' ')])
        s = s.replace(g, f' {human} ')

    return s


def slugify(title):
    slug = title.lower()

    rules = COMMON_RULES.copy()
    rules.extend(SLUGIFY_RULES)

    for rule in rules:
        slug = rule[0].sub(rule[1], slug)

    slug = slug.replace(' ', '')

    log.debug('generated slug for title', title=title, slug=slug)

    return slug


def modulify(title):
    module = sub_numbers(title, sub='_').lower()

    rules = COMMON_RULES.copy()
    rules.extend(MODULIFY_RULES)

    for rule in rules:
        module = rule[0].sub(rule[1], module)

    log.debug('generated module for title', title=title, module=module)

    return module


def structify(title):
    struct = ' '.join([t[0].upper() + t[1:] for t in sub_numbers(title).replace('-', ' ').replace('.', ' Dot ').split(' ') if len(t.strip()) > 0])

    rules = COMMON_RULES.copy()
    rules.extend(STRUCTIFY_RULES)

    for rule in rules:
        struct = rule[0].sub(rule[1], struct)

    log.debug('generated struct for title', title=title, struct=struct)

    return struct


def tokens(title):
    slug = slugify(title)
    module = modulify(title)
    struct = structify(title)

    return slug, module, struct


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

        try:
            slug, module, struct = tokens(icon['title'])
        except Exception:
            raise Exception('failed to tokenize icon', icon=icon['title'])

        icon['slug'] = slug
        icon['module'] = module
        icon['struct'] = struct
        icon['svg'] = escape_svg(svg_data)

        match = SVG_PATH_PATTERN.search(svg_data)

        if match is None:
            raise Exception(f'failed to parse SVG path for {slug}')

        icon['path'] = match.group(1)

        log.info('generated data for icon', title=icon['title'], slug=slug, module=module, struct=struct)

    return {i['module']:i for i in data}


def generate_library(dataset):
    def expand_struct(icon):
        return f'''    mod {icon['module']} {{
        use super::super::Icon;

        pub const ICON: Icon = Icon{{title: "{icon['title']}", slug: "{icon['slug']}", hex: "{icon['hex']}", source: "{icon['source']}", svg: "{icon['svg']}", path: "{icon['path']}"}};
    }}'''

    structs = []
    re_exports = []
    matches = []

    for slug in sorted(dataset.keys()):
        icon = dataset[slug]

        structs.append(expand_struct(icon))
        matches.append('        "{}" => Some(icons::{}),'.format(icon['slug'], icon['struct']))

        if icon['struct'] != 'ICON':
            re_exports.append('    pub use {}::ICON as {};'.format(icon['module'], icon['struct']))
        else:
            re_exports.append('    pub use {}::ICON;'.format(icon['module']))

    log.debug('generating source file', file='lib.rs')

    newline = '\n'

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

pub mod icons {{
{newline.join(structs)}
{newline.join(re_exports)}
}}

pub fn get(name: &str) -> Option<Icon> {{
    match name {{
{newline.join(matches)}
        _ => None,
    }}
}}
''')

def generate_crate(version):
    shutil.rmtree('./crate', ignore_errors=True)
    os.makedirs('./crate/src')

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

    generate_library(generate_icon_dataset())


    log.info('finished generating crate', version=version)


if __name__ == '__main__':
    log.drop_handlers()
    log.add_handler(StdoutColour)

    log.info('starting crate builder')

    npm_version = get_npm_version()
    crate_version = get_crate_version()

    if npm_version == crate_version:
        log.error('crate in-sync with npm; exiting')
        sys.exit(0)

    generate_crate(npm_version)