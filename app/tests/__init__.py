"""
	app unit tests
"""
from unittest import TestCase

from os.path import abspath
from flask import json
from app import create_app, db

dumps = json.dumps
loads = json.loads
content_type = 'application/json'


class TestCase(TestCase):
	def __init__(self, *args, **kwargs):
		self.app = create_app(config_mode='Test')
		super(TestCase, self).__init__(*args, **kwargs)

	def setUp(self):
		self.client = self.app.test_client()
		self.ctx = self.app.test_request_context()
		self.ctx.push()
		db.create_all()

	def tearDown(self):
		db.drop_all()
		self.ctx.pop()

	def get_data(self, url, id=None, query=None):
		if id:
			url = '%s/%s)' % (url, id)

		if query:
			resp = self.client.get(url, content_type=content_type, q=query)
		else:
			resp = self.client.get(url, content_type=content_type)

		assert resp.status_code == 200
		return loads(resp.data)

	def delete_data(self, url, id):
		url = '%s/%s)' % (url, id)
		resp = self.client.delete(url, content_type=content_type)
		assert resp.status_code == 204

	def post_data(self, data, url):
		data = dumps(data)
		resp = self.client.post(url, data=data, content_type=content_type)
		assert resp.status_code == 201
		return loads(resp.data)

	def patch_data(self, data, url, id=None, query=None):
		if id:
			url = '%s/%s)' % (url, id)

		if query:
			resp = self.client.patch(url, content_type=content_type, q=query)
		else:
			resp = self.client.patch(url, content_type=content_type)

		assert (resp.status_code == 200 or resp.status_code == 201)
		return loads(resp.data)
