#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib.request


def get_npm_version():
    with urllib.request.urlopen('https://registry.npmjs.org/simple-icons') as response:
        data = json.load(response)

    return data['dist-tags']['latest']


def get_crate_version():
    with urllib.request.urlopen('https://crates.io/api/v1/crates/simple-icons') as response:
        data = json.load(response)

    lateste_version_id = sorted(data['crate']['versions'])[-1]

    return [x for x in data['versions'] if x['id'] == lateste_version_id][0]['num']
