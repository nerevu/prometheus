# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2012 Audrius Kažukauskas
#
# This file is part of BeanCounter and is released under
# the ISC license, see LICENSE for more details.

from datetime import date

from flask import json

from tests import TestCase

ENTRY = {
    'amount': '42.00',
    'date': str(date.today()),
    'note': 'foobar',
}

URL = '/api/charts'


class ChartsTestCase(TestCase):
    def test_chart_bar(self):
        entry2 = ENTRY.copy()
        entry2['amount'] = '13.37'
        self.add_entry(ENTRY)
        self.add_entry(entry2)
        resp = self.client.get(URL, query_string={'type': 'bar'})
        data_point = json.loads(resp.data)['series'][0]
        assert data_point[0] == '(no tag)'
        assert data_point[1] == '55.37'

    def test_chart_date(self):
        entry2 = ENTRY.copy()
        self.add_entry(ENTRY)
        self.add_entry(entry2)
        resp = self.client.get(URL, query_string={'type': 'date'})
        data_point = json.loads(resp.data)['series'][0]
        assert data_point[0] == ENTRY['date']
        assert data_point[1] == '84.00'

    def test_chart_invalid_month(self):
        resp = self.client.get(URL, query_string={
            'month': '2011',
            'type': 'date',
        })
        assert resp.status_code == 400

    def test_chart_invalid_type(self):
        resp = self.client.get(URL, query_string={'type': 'foo'})
        assert resp.status_code == 400

    def test_chart_missing_type(self):
        resp = self.client.get(URL)
        assert resp.status_code == 400
