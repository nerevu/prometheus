"""
	tests.test_hermes
	~~~~~~~~~~~~~~~~
Provides unit tests for the :mod:`app.hermes` module.

"""

from unittest2 import TestCase, TestSuite, main
from flask import json
from app import create_app, db

dumps = json.dumps
loads = json.loads


class InitialCase(TestCase):
	def setUp(self):
		"""Before each test, set up a blank database"""
		self.app = create_app(config_mode='Test')
		self.client = self.app.test_client()
		self.jsonx = self.app.test_request_context()
		self.jsonx.push()
		db.create_all()

	def tearDown(self):
		"""Get rid of the database again after each test."""
		db.drop_all()
		self.jsonx.pop()


class APIHelperCase(InitialCase):
	endpoint = '/api'
	json = 'application/json'

	def get_data(self, table, id=None, query=None):
		# returns status_code 200
		if id:
			url = '%s/%s/%s' % (self.endpoint, table, id)
		else:
			url = '%s/%s' % (self.endpoint, table)

		if query:
			r = self.client.get(url, content_type=self.json, q=query)
		else:
			r = self.client.get(url, content_type=self.json)

		return r

	def delete_data(self, table, id):
		# returns status_code 204
		url = '%s/%s/%s' % (self.endpoint, table, id)
		r = self.client.delete(url, content_type=self.json)
		return r

	def post_data(self, data, table):
		# returns status_code 201
		url = '%s/%s' % (self.endpoint, table)
		r = self.client.post(url, data=dumps(data), content_type=self.json)
		return r

	def patch_data(self, data, table, id=None, query=None):
		# returns status_code 200 or 201
		if id:
			url = '%s/%s/%s' % (self.endpoint, table, id)
		else:
			url = '%s/%s' % (self.endpoint, table)

		if query:
			r = self.client.patch(url, data=dumps(data), content_type=self.json,
				q=query)
		else:
			r = self.client.patch(url, data=dumps(data), content_type=self.json)

		return r


class WebTestCase(InitialCase):
	"""Unit tests for the website"""
	def test_home(self):
		r = self.client.get('/')
		self.assertEquals(r.status_code, 200)

	def test_events(self):
		r = self.client.get('/event/')
		self.assertEquals(r.status_code, 200)

	def test_types(self):
		r = self.client.get('/event_type/')
		self.assertEquals(r.status_code, 200)

	def test_prices(self):
		r = self.client.get('/price/')
		self.assertEquals(r.status_code, 200)

	def test_commodities(self):
		r = self.client.get('/commodity/')
		self.assertEquals(r.status_code, 200)


class APITestCase(APIHelperCase):
	"""Unit tests for the API endpoints"""
	def setUp(self):
		"""Initialize database with data"""
		super(APITestCase, self).setUp()

		content = [{'table': 'exchange',
		'data': [{'symbol': 'NYSE', 'name': 'New York Stock Exchange'},
			{'symbol': 'NASDAQ', 'name': 'NASDAQ'},
			{'symbol': 'OTC', 'name': 'Over the counter'},
			{'symbol': 'N/A', 'name': 'Currency'}]},

		{'table': 'data_source',
		'data': [{'name': 'Yahoo'}, {'name': 'Google'}, {'name': 'XE'}]},

		{'table': 'commodity_group',
		'data': [{'name': 'Security'}, {'name': 'Currency'},
			{'name': 'Other'}]},

		{'table': 'commodity_type',
		'data': [{'name': 'Stock', 'commodity_group_id': 1},
			{'name': 'Bond', 'commodity_group_id': 1},
			{'name': 'Mutual Fund', 'commodity_group_id': 1},
			{'name': 'ETF', 'commodity_group_id': 1},
			{'name': 'Currency', 'commodity_group_id': 2},
			{'name': 'Descriptor', 'commodity_group_id': 3}]},

		{'table': 'commodity',
		'data': [{'symbol': 'USD', 'name': 'US Dollar',
				'commodity_type_id': 5, 'data_source_id': 3, 'exchange_id': 4},
			{'symbol': 'EUR', 'name': 'Euro',
				'commodity_type_id': 5, 'data_source_id': 3, 'exchange_id': 4},
			{'symbol': 'GBP', 'name': 'Pound Sterling',
				'commodity_type_id': 5, 'data_source_id': 3, 'exchange_id': 4},
			{'symbol': 'TZS', 'name': 'Tanzanian Shilling',
				'commodity_type_id': 5, 'data_source_id': 3, 'exchange_id': 4},
			{'symbol': 'Multiple', 'name': 'Multiple',
				'commodity_type_id': 6, 'data_source_id': 3, 'exchange_id': 4},
			{'symbol': 'Text', 'name': 'Text',
				'commodity_type_id': 6, 'data_source_id': 3,
				'exchange_id': 4}]},

		{'table': 'event_type',
		'data': [{'name': 'Dividend', 'commodity_id': '1'},
			{'name': 'Special Dividend', 'commodity_id': '1'},
			{'name': 'Stock Split', 'commodity_id': '5'},
			{'name': 'Name Change', 'commodity_id': '6'},
			{'name': 'Ticker Change', 'commodity_id': '6'}]}]

		for dict in content:
			table = dict['table']
			data = dict['data']
			result = [self.post_data(d, table) for d in data]
			[self.assertEqual(r.status_code, 201) for r in result]

	def test_get_event_types(self):
		"""Test for getting event types using :http:method:`get`."""
		r = self.get_data('event_type')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertGreater(loaded['num_results'], 1)

	def test_post_event_new_type(self):
		"""Test for posting an event using :http:method:`post`."""
		# check initial number of event types
		r = self.get_data('event_type')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		old = loaded['num_results']
		new = old + 1

		# add event
		data = {'symbol': 'ISIS', 'date': '1/22/12',
			'type': {'name': 'Brand New', 'commodity_id': 3}, 'value': 100}
		r = self.post_data(data, 'event')
		self.assertEqual(r.status_code, 201)

		# test that the new event was added
		r = self.get_data('event')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['num_results'], 1)

		# test that the new event type was added
		r = self.get_data('event_type')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['num_results'], new)

	def test_patch_commodity_exisiting_type(self):
		"""Test for patching a commodity with an existing type using
		:http:method:`patch`.
		"""
		# check initial commodity type
		r = self.get_data('commodity', 1)
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		old = loaded['type']['id']
		new = old + 1

		# patch the commodity with an existing type
		patch = {'type': {'add': {'id': new}}}
		r = self.patch_data(patch, 'commodity', 1)
		self.assertEqual(r.status_code, 200)

		# test that the new commodity type was changed
		r = self.get_data('commodity', 1)
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['type']['id'], new)

	def test_patch_commodity_new_type(self):
		"""Test for patching a commodity with a new type using
		:http:method:`patch`.
		"""
		# check initial num of commodity types
		r = self.get_data('commodity_type')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		old = loaded['num_results']
		new = old + 1

		# patch the commodity with a new type
		patch = {'type': {'add': {'name': 'Brand New',
			'commodity_group_id': 2}}}
		r = self.patch_data(patch, 'commodity', 1)
		self.assertEqual(r.status_code, 200)

		# test that the new commodity type was changed
		r = self.get_data('commodity', 1)
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['type']['id'], new)

	def test_post_price(self):
		"""Test for posting a price using :http:method:`post`."""
		# add price
		data = {'commodity_id': 1, 'currency_id': 3, 'close': 30}
		r = self.post_data(data, 'price')
		self.assertEqual(r.status_code, 201)

		# test that the new price was added
		r = self.get_data('price')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['num_results'], 1)

	def test_delete_commodity(self):
		"""Test for deleting a commodity with a query using
		:http:method:`delete`.
		"""
		# check number of commodities
		r = self.get_data('commodity')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		old = loaded['num_results']
		new = old - 1

		# delete commodity
		r = self.delete_data('commodity', 2)
		self.assertEqual(r.status_code, 204)

		# test that the commodity was deleted
		r = self.get_data('commodity')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['num_results'], new)


def load_tests(loader, standard_tests, pattern):
	"""Returns the test suite for this module."""
	suite = TestSuite()
	suite.addTest(loader.loadTestsFromTestCase(WebTestCase))
	suite.addTest(loader.loadTestsFromTestCase(APITestCase))
	return suite
