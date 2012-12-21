# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2012 Audrius Kažukauskas
#
# This file is part of BeanCounter and is released under
# the ISC license, see LICENSE for more details.

from datetime import date

from tests import TestCase


class MainTestCase(TestCase):
    def test_empty_db(self):
        resp = self.client.get('/')
        assert 'entries: []' in resp.data
        assert 'tags: []' in resp.data
        assert 'currDate: "%s"' % date.today().replace(day=1) in resp.data

    def test_month_in_url(self):
        resp = self.client.get('/entries/2011-12')
        assert 'currDate: "%s"' % date(2011, 12, 1) in resp.data

    def test_invalid_month_in_url(self):
        resp = self.client.get('/entries/2011-42')
        assert resp.status_code == 400
