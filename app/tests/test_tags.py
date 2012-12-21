# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2012 Audrius Kažukauskas
#
# This file is part of BeanCounter and is released under
# the ISC license, see LICENSE for more details.

from flask import json

from tests import TestCase

URL = '/api/tags'


class TagsTestCase(TestCase):
    def test_empty_db(self):
        resp = self.client.get(URL)
        data = json.loads(resp.data)
        assert len(data['tags']) == 0

    # POST tests.
    # -----------

    def test_add_tag(self):
        self.add_tag({'name': 'foobar'})
        resp = self.client.get(URL)
        data = json.loads(resp.data)['tags'][0]
        assert data['name'] == 'foobar'

    def test_add_tag_invalid_data(self):
        resp = self.client.post(URL, data={})
        assert resp.status_code == 400

    def test_add_tag_already_exists(self):
        tag = {'name': 'foobar'}
        self.add_tag(tag)
        resp = self.client.post(URL, data=json.dumps(tag),
                                content_type='application/json')
        assert resp.status_code == 409

    # PUT tests.
    # ----------

    def test_update_tag(self):
        tag_id = self.add_tag({'name': 'foo'})
        tag = {'name': 'bar'}
        resp = self.client.put('%s/%s' % (URL, tag_id), data=json.dumps(tag),
                               content_type='application/json')
        assert resp.status_code == 204
        resp = self.client.get(URL)
        data = json.loads(resp.data)['tags'][0]
        assert data['id'] == tag_id
        assert data['name'] == tag['name']

    def test_update_tag_invalid_data(self):
        tag_id = self.add_tag({'name': 'foo'})
        tag = {'name': ''}
        resp = self.client.put('%s/%s' % (URL, tag_id), data=json.dumps(tag),
                               content_type='application/json')
        assert resp.status_code == 400

    def test_update_nonexistent_tag(self):
        tag = {'name': 'foobar'}
        resp = self.client.put('%s/42' % URL, data=json.dumps(tag),
                               content_type='application/json')
        assert resp.status_code == 404

    def test_update_tag_name_already_exists(self):
        tag1 = {'name': 'foo'}
        tag2 = {'name': 'bar'}
        tag_id = self.add_tag(tag1)
        self.add_tag(tag2)
        resp = self.client.put('%s/%s' % (URL, tag_id), data=json.dumps(tag2),
                               content_type='application/json')
        assert resp.status_code == 409

    def test_delete_tag(self):
        tag_id = self.add_tag({'name': 'foobar'})
        resp = self.client.delete('%s/%s' % (URL, tag_id))
        assert resp.status_code == 204
        resp = self.client.get(URL)
        data = json.loads(resp.data)
        assert len(data['tags']) == 0

    # DELETE tests.
    # -------------

    def test_delete_nonexistent_tag(self):
        resp = self.client.delete('%s/42' % URL)
        assert resp.status_code == 404

    def test_delete_tag_batch_mode(self):
        tag_id = self.add_tag({'name': 'foobar'})
        resp = self.client.delete(URL, data=json.dumps({'ids': [tag_id]}),
                                  content_type='application/json')
        assert resp.status_code == 204
        resp = self.client.get(URL)
        data = json.loads(resp.data)
        assert len(data['tags']) == 0

    def test_delete_nonexistent_tag_batch_mode(self):
        resp = self.client.delete(URL, data=json.dumps({'ids': [42]}),
                                  content_type='application/json')
        assert resp.status_code == 404

    def test_delete_tag_batch_mode_invalid_data(self):
        resp = self.client.delete(URL, data='[]',
                                  content_type='application/json')
        assert resp.status_code == 400
