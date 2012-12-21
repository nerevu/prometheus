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
    'amount':  '42.00',
    'date':    str(date.today()),
    'note':    'foobar',
}

URL = '/api/entries'


class EntriesTestCase(TestCase):
    # GET tests.
    # ----------

    def test_empty_db(self):
        resp = self.client.get(URL)
        data = json.loads(resp.data)
        assert len(data['entries']) == 0

    def test_get_entries_by_date(self):
        self.add_entry(ENTRY)
        # Cut day part from the date.
        resp = self.client.get(URL, query_string={'month': ENTRY['date'][:-3]})
        data = json.loads(resp.data)
        assert len(data['entries']) == 1

    def test_get_entries_by_date_invalid_month(self):
        resp = self.client.get(URL, query_string={'month': '2011'})
        assert resp.status_code == 400

    def test_get_entries_and_total_amount(self):
        self.add_entry(ENTRY)
        resp = self.client.get(URL, query_string={'total': 1})
        data = json.loads(resp.data)
        assert data['totalAmount'] == '42.00'

    def test_get_nonexistent_entry(self):
        resp = self.client.get('%s/1337' % URL)
        assert resp.status_code == 404

    # POST tests.
    # -----------

    def test_add_entry(self):
        entry_id = self.add_entry(ENTRY)
        resp = self.client.get('%s/%s' % (URL, entry_id))
        data = json.loads(resp.data)
        assert data['id'] == entry_id
        assert data['amount'] == ENTRY['amount']
        assert data['date'] == ENTRY['date']
        assert data['note'] == ENTRY['note']

    def test_add_entry_invalid_data(self):
        entry = ENTRY.copy()
        entry['amount'] = 'foobar'
        del entry['date']
        self.add_entry(entry, status_code=400)

    def test_add_entry_with_tag(self):
        tag_id = self.add_tag({'name': 'foobar'})
        entry = ENTRY.copy()
        entry['tags'] = [tag_id]
        entry_id = self.add_entry(entry)
        resp = self.client.get('%s/%s' % (URL, entry_id))
        data = json.loads(resp.data)
        assert data['tags'] == entry['tags']

    def test_add_entry_with_nonexistent_tag(self):
        entry = ENTRY.copy()
        entry['tags'] = [1337]
        entry_id = self.add_entry(entry)
        resp = self.client.get('%s/%s' % (URL, entry_id))
        data = json.loads(resp.data)
        assert data['tags'] == []

    def test_add_entry_with_tag_invalid_data(self):
        entry = ENTRY.copy()
        entry['tags'] = 42
        self.add_entry(entry, status_code=400)

    def test_add_entry_get_total_amount(self):
        entry = ENTRY.copy()
        entry['totalForMonth'] = ENTRY['date']
        resp = self.client.post(URL, data=json.dumps(entry),
                                content_type='application/json')
        data = json.loads(resp.data)
        assert data['totalAmount'] == '42.00'

    # PUT tests.
    # ----------

    def test_update_entry_one_field(self):
        entry_id = self.add_entry(ENTRY)
        entry = {'amount': '13.37'}
        resp = self.client.put('%s/%s' % (URL, entry_id),
                               data=json.dumps(entry),
                               content_type='application/json')
        assert resp.status_code == 204
        resp = self.client.get('%s/%s' % (URL, entry_id))
        data = json.loads(resp.data)
        assert data['amount'] == entry['amount']
        assert data['date'] == ENTRY['date']
        assert data['note'] == ENTRY['note']

    def test_update_entry_all_fields(self):
        entry_id = self.add_entry(ENTRY)
        entry = {
            'amount': '13.37',
            'date': '2011-01-01',
            'note': 'baz',
        }
        resp = self.client.put('%s/%s' % (URL, entry_id),
                               data=json.dumps(entry),
                               content_type='application/json')
        assert resp.status_code == 204
        resp = self.client.get('%s/%s' % (URL, entry_id))
        data = json.loads(resp.data)
        assert data['amount'] == entry['amount']
        assert data['date'] == entry['date']
        assert data['note'] == entry['note']

    def test_update_entry_invalid_data(self):
        entry_id = self.add_entry(ENTRY)
        entry = {'amount': 'foobar'}
        resp = self.client.put('%s/%s' % (URL, entry_id),
                               data=json.dumps(entry),
                               content_type='application/json')
        assert resp.status_code == 400

    def test_update_entry_with_tag(self):
        tag_id = self.add_tag({'name': 'foobar'})
        entry_id = self.add_entry(ENTRY)
        entry = {'tags': [tag_id]}
        resp = self.client.put('%s/%s' % (URL, entry_id),
                               data=json.dumps(entry),
                               content_type='application/json')
        assert resp.status_code == 204
        resp = self.client.get('%s/%s' % (URL, entry_id))
        data = json.loads(resp.data)
        assert data['tags'] == entry['tags']

    def test_update_entry_remove_tag(self):
        tag_id = self.add_tag({'name': 'foobar'})
        entry = ENTRY.copy()
        entry['tags'] = [tag_id]
        entry_id = self.add_entry(entry)
        entry['tags'] = []
        resp = self.client.put('%s/%s' % (URL, entry_id),
                               data=json.dumps(entry),
                               content_type='application/json')
        assert resp.status_code == 204
        resp = self.client.get('%s/%s' % (URL, entry_id))
        data = json.loads(resp.data)
        assert data['tags'] == []

    def test_update_entry_with_nonexistent_tag(self):
        entry_id = self.add_entry(ENTRY)
        entry = {'tags': [1337]}
        resp = self.client.put('%s/%s' % (URL, entry_id),
                               data=json.dumps(entry),
                               content_type='application/json')
        assert resp.status_code == 204
        resp = self.client.get('%s/%s' % (URL, entry_id))
        data = json.loads(resp.data)
        assert data['tags'] == []

    def test_update_entry_with_tag_invalid_data(self):
        entry_id = self.add_entry(ENTRY)
        entry = {'tags': 42}
        resp = self.client.put('%s/%s' % (URL, entry_id),
                               data=json.dumps(entry),
                               content_type='application/json')
        assert resp.status_code == 400

    def test_update_nonexistent_entry(self):
        entry = {'amount': '13.37'}
        resp = self.client.put('%s/1337' % URL, data=json.dumps(entry),
                               content_type='application/json')
        assert resp.status_code == 404

    def test_update_entry_get_total_amount(self):
        entry_id = self.add_entry(ENTRY)
        # Don't change anything, just request for totalAmount.
        entry = {'totalForMonth': ENTRY['date']}
        resp = self.client.put('%s/%s' % (URL, entry_id),
                               data=json.dumps(entry),
                               content_type='application/json')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['totalAmount'] == '42.00'

    # DELETE tests.
    # -------------

    def test_delete_entry(self):
        entry_id = self.add_entry(ENTRY)
        resp = self.client.delete('%s/%s' % (URL, entry_id))
        assert resp.status_code == 204
        resp = self.client.get('%s/%s' % (URL, entry_id))
        assert resp.status_code == 404

    def test_delete_nonexistent_entry(self):
        resp = self.client.delete('%s/1337' % URL)
        assert resp.status_code == 404

    def test_delete_entry_get_total_amount(self):
        entry_id = self.add_entry(ENTRY)
        data = {'totalForMonth': ENTRY['date']}
        resp = self.client.delete('%s/%s' % (URL, entry_id),
                                  data=json.dumps(data),
                                  content_type='application/json')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['totalAmount'] == '0.00'

    def test_delete_entry_batch_mode(self):
        entry_id = self.add_entry(ENTRY)
        resp = self.client.delete(URL, data=json.dumps({'ids': [entry_id]}),
                                  content_type='application/json')
        assert resp.status_code == 204
        resp = self.client.get('%s/%s' % (URL, entry_id))
        assert resp.status_code == 404

    def test_delete_nonexistent_entry_batch_mode(self):
        resp = self.client.delete(URL, data=json.dumps({'ids': [1337]}),
                                  content_type='application/json')
        assert resp.status_code == 404

    def test_delete_entry_batch_mode_invalid_data(self):
        resp = self.client.delete(URL, data='[]',
                                  content_type='application/json')
        assert resp.status_code == 400

    def test_delete_entry_batch_mode_get_total_amount(self):
        entry_id = self.add_entry(ENTRY)
        data = {
            'ids': [entry_id],
            'totalForMonth': ENTRY['date'],
        }
        resp = self.client.delete(URL, data=json.dumps(data),
                                  content_type='application/json')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['totalAmount'] == '0.00'
