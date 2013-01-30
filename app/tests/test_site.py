# -*- coding: utf-8 -*-
"""
	app.tests.test_site
	~~~~~~~~~~~~~~

	Provides unit tests for the website.
"""

import nose.tools as nt

from . import APIHelper, get_globals, check_equal, loads, dumps, err, conn
from pprint import pprint
from app import create_app, db
from app.helper import get_init_values


def setup_module():
	"""site initialization"""
	global initialized
	global pages
	global tables
	global client
	global content

	app, client, jsonx = get_globals()
	keys = [k for k in app.blueprints.keys() if k.endswith('api0')]
	tables = [k.replace('api0', '') for k in keys]
	pages = [link['id'] for link in app.config['TOPNAV']]
	values = get_init_values()
	content = conn.process(values)
	initialized = True
	print('Site Module Setup\n')


class TestAPI(APIHelper):
	"""Unit tests for the API"""
	def __init__(self):
		self.cls_initialized = False

	def setUp(self):
		"""database initialization"""
		assert not self.cls_initialized
		db.create_all()

		for piece in content:
			table = piece['table']
			data = piece['data']
			result = [self.post_data(d, table) for d in data]
			[nt.assert_equal(r.status_code, 201) for r in result]

		self.cls_initialized = True
		print('\nTestAPI Class Setup\n')

	def tearDown(self):
		"""database removal"""
		assert self.cls_initialized
		db.drop_all()
		self.cls_initialized = False

		print('TestAPI Class Teardown\n')

	def test_api_get(self):
		for table in tables:
			self.setUp()
			n = self.get_num_results(table)
			self.tearDown()
			yield check_equal, table, n >= 0, True

	def test_api_delete(self):
		for table in tables:
			self.setUp()
			old = self.get_num_results(table)

			if old > 0:
				# delete first entry
				r = self.delete_data(table, 1)

				# test that the entry was deleted
				new = self.get_num_results(table)
				self.tearDown()
				yield check_equal, table, new, old - 1
			else:
				self.tearDown()


class TestWeb:
	"""Unit tests for the website"""
	def __init__(self):
		self.cls_initialized = False

	def setUp(self):
		"""Initialize database with data"""
		assert not self.cls_initialized
		db.create_all()
		self.cls_initialized = True

		print('\nTestWeb Class Setup\n')

	def tearDown(self):
		"""Remove data from database"""
		assert self.cls_initialized
		db.drop_all()
		self.cls_initialized = False

		print('TestWeb Class Teardown\n')

	def test_home(self):
		r = client.get('/')
		nt.assert_equal(r.status_code, 200)

	def test_navbar(self):
		for page in pages:
			self.setUp()
			r = client.get('/%s/' % page)
			self.tearDown()
			yield check_equal, page, r.status_code, 200

	def test_api(self):
		for table in tables:
			self.setUp()
			r = client.get('/api/%s' % table)
			self.tearDown()
			yield check_equal, table, r.status_code, 200
