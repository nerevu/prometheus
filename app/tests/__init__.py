# -*- coding: utf-8 -*-
"""
	app.tests
	~~~~~~~~~~~~~~

	Provides application unit tests
"""

import sys
import nose.tools as nt

from flask import json
from app import create_app, db
from requests import get, post, delete, patch

loads = json.loads
dumps = json.dumps
err = sys.stderr
initialized = False


def setup_package():
	"""database context creation"""
	global initialized
	global app
	global client
	global jsonx
	global base

	app = create_app(config_mode='Test')
	base = app.config['API_URL']
	client = app.test_client()
	jsonx = app.test_request_context()
	jsonx.push()
	initialized = True

	print('Test Package Setup\n')


def teardown_package():
	"""database context removal"""
	global initialized
	global jsonx

	jsonx.pop()
	initialized = False

	print('Test Package Teardown\n')


def check_equal(page, x, y):
	nt.assert_equal(x, y)


def get_globals():
	global app
	global client
	global jsonx

	return app, client, jsonx


class APIHelper:
	hdr = {'content-type': 'application/json'}

	def get_data(self, table, id=None, query=None):
		# returns status_code 200
		if id:
			url = base + table + '/' + id
		else:
			url = base + table

		if query:
			url = '%s&q=%s' % (url, dumps(query))

		return get(url, headers=self.HDR)

	def delete_data(self, table, id):
		# returns status_code 204
		url = base + table + '/' + id
		return delete(url, headers=self.hdr)

	def post_data(self, data, table):
		# returns status_code 201
		url = base + table
		r = post(url, data=dumps(data), headers=self.hdr)
		return r

	def patch_data(self, data, table, id=None, query=None):
		# returns status_code 200 or 201
		if id:
			url = base + table + '/' + id
		else:
			url = base + table

		if query:
			url = '%s&q=%s' % (url, dumps(query))

		return patch(url, data=dumps(data), headers=self.hdr)

	def get_num_results(self, table):
		r = self.get_data(table)
		loaded = loads(r.data)
		return loaded['num_results']

	def get_type(self, table, id=1):
		r = self.get_data(table, id)
		loaded = loads(r.data)
		return loaded['type']['id']
