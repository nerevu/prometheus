# -*- coding: utf-8 -*-
"""
	app.tests.test_site
	~~~~~~~~~~~~~~

	Provides unit tests for the website.
"""

import nose.tools as nt

from . import get_globals, check_equal, err
from pprint import pprint
from app import create_app


def setup_module():
	"""site initialization"""
	global initialized
	global pages
	global client

	app, client, jsonx = get_globals()
	keys = [k for k in app.blueprints.keys() if k.endswith('api0')]
	pages = [link['id'] for link in app.config['TOPNAV']]
	initialized = True
	print('Site Module Setup\n')



class TestWeb:
	"""Unit tests for the website"""
	def __init__(self):
		self.cls_initialized = False

	def setUp(self):
		"""Initialize"""
		assert not self.cls_initialized
		self.cls_initialized = True

		print('\nTestWeb Class Setup\n')

	def tearDown(self):
		"""Tear down"""
		assert self.cls_initialized
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
