"""
	tests.test_views
	~~~~~~~~~~~~~~~~
Provides unit tests for the :mod:`app.hermes.views` module.

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
		super(APITestCase, self).setUp()
		"""Setup database"""
		# create an event type with new commodity
		data = {'name': 'Dividend', 'unit': {'name': 'US Dollars', 'symbol': 'USD'}}
		r = self.post_data(data, 'event_type')
		self.assertEqual(r.status_code, 201)

		# create another event type with new commodity
		data = {'name': 'Dividend', 'unit': {'name': 'TZ Shillings',
			'symbol': 'TZS'}}
		r = self.post_data(data, 'event_type')
		self.assertEqual(r.status_code, 201)

		# create another commodity
		data = {'name': 'Euro', 'symbol': 'EUR'}
		r = self.post_data(data, 'commodity')
		self.assertEqual(r.status_code, 201)

		# create an event
		data = {'symbol': 'ISIS', 'date': '1/22/12', 'type': {'id': 1},
			'value': 100}
		r = self.post_data(data, 'event')
		self.assertEqual(r.status_code, 201)

	def test_get_event_types(self):
		"""Test for getting event types using :http:method:`get`."""
		r = self.get_data('event_type')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['num_results'], 2)
		self.assertEqual(loaded['objects'][0]['name'], 'Dividend')

	def test_post_event_with_new_type(self):
		"""Test for posting an event using :http:method:`post`."""
		data = {'symbol': 'ISIS', 'date': '1/22/12',
			'type': {'name': 'Dividend', 'commodity_id': 3}, 'value': 100}
		r = self.post_data(data, 'event')
		self.assertEqual(r.status_code, 201)

		# test that the new event was added
		r = self.get_data('event')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['num_results'], 2)

		# test that the new event type was added
		r = self.get_data('event_type')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['num_results'], 3)
		self.assertEqual(loaded['objects'][2]['name'], data['type']['name'])

	def test_patch_event_exisiting_type(self):
		"""Test for patching an event with an existing type using
		:http:method:`patch`.
		"""
		# patch the event with an existing event type
		patch = {'type': {'add': {'id': 2}}}
		r = self.patch_data(patch, 'event', 1)
		self.assertEqual(r.status_code, 200)

		# test that the new event type was changed
		r = self.get_data('event', 1)
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['type']['id'], 2)

	def test_patch_event_new_type(self):
		"""Test for patching an event with a new type using
		:http:method:`patch`.
		"""
		# patch the event with a new event type
		patch = {'type': {'add': {'name': 'Special Dividend',
			'commodity_id': 2}}}
		r = self.patch_data(patch, 'event', 1)
		self.assertEqual(r.status_code, 200)

		# test that the new event type was changed
		r = self.get_data('event', 1)
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['type']['id'], 3)

		# test that this new event type was added to the database as well
		r = self.get_data('event_type')
		self.assertEqual(r.status_code, 200)
		loaded = loads(r.data)
		self.assertEqual(loaded['num_results'], 3)
		self.assertEqual(loaded['objects'][2]['name'],
			patch['type']['add']['name'])


def load_tests(loader, standard_tests, pattern):
	"""Returns the test suite for this module."""
	suite = TestSuite()
	suite.addTest(loader.loadTestsFromTestCase(WebTestCase))
	suite.addTest(loader.loadTestsFromTestCase(APITestCase))
	return suite
