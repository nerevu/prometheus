# -*- coding: utf-8 -*-
"""
	app.tests.test_hermes
	~~~~~~~~~~~~~~~~

	Provides unit tests for the :mod:`app.hermes` module.
"""

import nose.tools as nt

from . import APIHelper, get_globals, check_equal, loads, err, conn
from pprint import pprint
from app import create_app, db
from app.manage_helper import get_init_values


def setup_module():
	"""site initialization"""
	global initialized
	global content

	values = get_init_values()
	content = conn.process(values)
	initialized = True
	print('Hermes Module Setup\n')


class TestHermesAPI(APIHelper):
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

		print('\nTestAPI Class Setup\n')

	def tearDown(self):
		"""database removal"""
		assert self.cls_initialized
		db.drop_all()
		self.cls_initialized = False

		print('TestAPI Class Teardown\n')

	def test_post_event_new_type(self):
		"""Test for posting an event using :http:method:`post`."""
		# check initial number of events and type
		types = self.get_num_results('event_type')
		events = self.get_num_results('event')

		# add event
		data = {
			'commodity_id': 3, 'date': '1/22/12',
			'type': {'name': 'Brand New'}, 'currency_id': 3, 'value': 100}
		r = self.post_data(data, 'event')
		nt.assert_equal(r.status_code, 201)

		# test that the new event and type were added
		nt.assert_equal(self.get_num_results('event'), events + 1)
		nt.assert_equal(self.get_num_results('event_type'), types + 1)

	def test_patch_commodity_exisiting_type(self):
		"""Test for patching a commodity with an existing type using
		:http:method:`patch`.
		"""
		# set table
		table = 'commodity'

		# check initial commodity type
		type = self.get_type(table)

		# check initial number of commodity types
		types = self.get_num_results('commodity_type')

		# patch the first commodity with an existing type
		choices = range(1, types + 1)
		new = [x for x in choices if x != type][0]
		patch = {'type': {'add': {'id': new}}}
		r = self.patch_data(patch, table, 1)
		nt.assert_equal(r.status_code, 200)

		# test that the new commodity type was changed
		nt.assert_equal(self.get_type(table), new)

	def test_patch_commodity_new_type(self):
		"""Test for patching a commodity with a new type using
		:http:method:`patch`.
		"""
		# set table
		table = 'commodity'

		# check initial num of commodity types
		types = self.get_num_results('commodity_type')

		# patch the first commodity with a new type
		patch = {
			'type': {'add': {'name': 'Brand New', 'group_id': 2}}}
		r = self.patch_data(patch, table, 1)
		nt.assert_equal(r.status_code, 200)

		# test that the new commodity type was changed
		nt.assert_equal(self.get_type(table), types + 1)

	def test_post_price(self):
		"""Test for posting a price using :http:method:`post`."""
		# set table
		table = 'price'

		# check number of prices
		num = self.get_num_results(table)

		# add price
		data = {'commodity_id': 1, 'currency_id': 3, 'close': 30}
		r = self.post_data(data, table)
		nt.assert_equal(r.status_code, 201)

		# test that the new price was added
		nt.assert_equal(self.get_num_results(table), num + 1)
