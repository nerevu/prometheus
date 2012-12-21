# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2012 Audrius Kažukauskas
#
# This file is part of BeanCounter and is released under
# the ISC license, see LICENSE for more details.

import unittest
from os.path import abspath

from flask import json

from beancounter import create_app
from beancounter.model import init_db, clear_db

ENTRIES_URL = '/api/entries'
TAGS_URL = '/api/tags'


class TestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.app = create_app(abspath('../config_test.py'))
        super(TestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        init_db()

    def tearDown(self):
        clear_db()
        self.ctx.pop()

    def add_tag(self, tag):
        resp = self.client.post(TAGS_URL, data=json.dumps(tag),
                                content_type='application/json')
        assert resp.status_code == 200
        assert 'id' in resp.data
        return json.loads(resp.data)['id']

    def add_entry(self, entry, status_code=200):
        resp = self.client.post(ENTRIES_URL, data=json.dumps(entry),
                                content_type='application/json')
        assert resp.status_code == status_code
        if status_code == 200:
            assert 'id' in resp.data
            return json.loads(resp.data)['id']
