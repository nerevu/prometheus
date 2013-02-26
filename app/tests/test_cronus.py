# -*- coding: utf-8 -*-
"""
	app.tests.test_cronus
	~~~~~~~~~~~~~~~~

	Provides unit tests for the :mod:`app.cronus` module.
"""

import nose.tools as nt

from os import path as p
from . import APIHelper, get_globals, check_equal, loads, err, conn
from pprint import pprint
from app import create_app, db
from app.helper import get_init_values
from app.cronus import CSV


def setup_module():
	"""site initialization"""
	global initialized
	global content

	values = get_init_values()
	content = conn.process(values)
	initialized = True
	print('Cronus Module Setup\n')


class TestCronusAPI(APIHelper):
	"""Unit tests for the API endpoints"""
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

		print('\TestCronusAPI Class Setup\n')

	def tearDown(self):
		"""database removal"""
		assert self.cls_initialized
		db.drop_all()
		self.cls_initialized = False

		print('TestAPI Class Teardown\n')

	def test_post_csv(self):
		"""Test for posting csv content :http:method:`post`."""
		# check initial number of transactions
		transactions = self.get_num_results('transaction')

		# upload file
		file = p.join(p.dirname(__file__), 'trnx.csv')
		csv = CSV(file, display=True)
		content = csv.load()

		for piece in content:
			table = piece['table']
			data = piece['data']
			result = [self.post_data(d, table) for d in data]
			[nt.assert_equal(r.status_code, 201) for r in result]

		# test that the new transactions were added
		nt.assert_equal(
			self.get_num_results('transaction'), transactions + csv.num_trnx)
