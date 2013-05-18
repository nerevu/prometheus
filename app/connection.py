# -*- coding: utf-8 -*-
"""
	app.connection
	~~~~~~~~~~~~~~

	Provides functions for querying the database
"""

from pprint import pprint
from json import dumps as dmp, loads, JSONEncoder
from requests import get as g, post as p, delete as d
from flask import current_app as app


class CustomEncoder(JSONEncoder):
	def default(self, obj):
		if set(['quantize', 'year']).intersection(dir(obj)):
			return str(obj)
		elif hasattr(obj, 'next'):
			return list(obj)
		return JSONEncoder.default(self, obj)


class Connection(object):
	"""
	DB connection.

	Attributes
	----------
	event : tuple
	event_type : tuple
	price : tuple
	commodity : tuple
	transaction : tuple
	stock : tuple
	dividend : tuple
	rate : tuple
	"""
	HDR = {'content-type': 'application/json'}

	def __init__(self, site, native=1):
		"""Creates a connection to the database

		Parameters
		----------
		site : a string
			api endpoint

		native : a number, default 1
			id of the native currency

		display : boolean, default False

		Examples
		--------
		>>> Connection('http://prometheus-api.herokuapp.com/')  #doctest: +ELLIPSIS
		<app.connection.Connection object at 0x...>
		"""
		self.site = site
		self.native = native
		self.limit = 1000

	@property
	def table_headers(self):
		return {
			'event': ['Symbol', 'Name', 'Unit', 'Value', 'Date'],
			'event_type': ['Type Name'],
			'price': ['Stock', 'Currency', 'Date', 'Price'],
			'commodity': ['Symbol', 'Name', 'Type'],
			'transaction': [
				'Holding', 'Type', 'Shares', 'Share Price', 'Date',
				'Commission']}

	@property
	def table_keys(self):
		return {
			'event': ['com_symbol', 'name', 'cur_symbol', 'value', 'date'],
			'event_type': ['name'],
			'price': ['com_symbol', 'cur_symbol', 'date', 'close'],
			'commodity': ['symbol', 'name', 'type'],
			'transaction': [
				'symbol', 'type_id', 'shares', 'price', 'date',
				'trade_commission']}

	@property
	def event(self):
		res = []

		for o in self.get('event'):
			res.append({
				'com_symbol': o['commodity']['symbol'],
				'name': o['type']['name'],
				'cur_symbol': o['currency']['symbol'],
				'value': o['value'],
				'date': o['date']})

		return res

	@property
	def event_type(self):
		symbols = []
		objects = self.get('event_type')
		return [symbols.append(o['name']) for o in objects]

	@property
	def price(self):
		res = []

		for o in self.get('price'):
			res.append({
				'com_symbol': o['commodity']['symbol'],
				'cur_symbol': o['currency']['symbol'],
				'date': o['date'],
				'close': o['close'],
				'currency_id': o['currency_id'],
				'commodity_id': o['commodity_id']})

		return res

	@property
	def rates(self):
		res = []
		[res.extend(p) for p in self.list_prices([5])]
		return res

	@property
	def security_prices(self):
		res = []
		[res.extend(p) for p in self.list_prices([1, 3, 4])]
		return res

	@property
	def commodity(self):
		res = []

		for o in self.get('commodity_type'):
			for c in o['commodities']:
				c.update({'type': o['name']})

			res.extend(o['commodities'])

		return res

	@property
	def security_data(self):
		res = []
		[res.extend(o['commodities']) for o in self.list_commodities()]
		return res

	@property
	def transaction(self):
		res = []

		for o in self.get('holding'):
			for trxn in o['transactions']:
				trxn.update({'symbol': o['commodity']['symbol']})
				trxn.update({'owner_id': o['account']['owner_id']})
				trxn.update({'account_id': o['account_id']})
				trxn.update({'commodity_id': o['commodity_id']})
				trxn.update({'trade_commission': o['account']['trade_commission']})
				res.append(trxn)

		return res

	@property
	def dividend(self):
		query = {'filters': [{'name': 'id', 'op': 'eq', 'val': 1}]}
		return self.get('event_type', query)[0]['events']

	def list_commodities(self, group=1):
		query = {'filters': [{'name': 'group_id', 'op': 'eq', 'val': group}]}
		return self.get('commodity_type', query)

	def list_prices(self, type_ids):
		query = {
			'filters': [
				{'name': 'type_id', 'op': 'in', 'val': type_ids},
				{
					'name': 'commodity_prices__currency_id', 'op': 'any',
					'val': self.native}]}

		objects = self.get('commodity', query)
		return [o['commodity_prices'] for o in objects]

	def get_commodity_info(self, symbols):
		query = {'filters': [{'name': 'symbol', 'op': 'in', 'val': symbols}]}
		return self.get('commodity', query)

	def commodity_ids(self, symbols):
		# TODO: return 'N/A' if symbol doesn't exist
		multi = True

		if hasattr(symbols, 'isalnum'):
			symbols = [symbols]
			multi = False

		objects = self.get_commodity_info(symbols)
		list = [(o['symbol'], o['id']) for o in objects]
		ids = [dict(list).get(s) for s in symbols]
		ids = ids if multi else ids[0]
		return ids

	def process(self, post_values, keys):
		tables = post_values.keys()
		value_list = post_values.values()
		tables = [tables] if hasattr(tables, 'isalnum') else tables

		# wrap keys in tuple() to prevent ["name"] from iterating over each letter
		key_list = [tuple(keys[t]) for t in tables]
		combo = zip(key_list, value_list)

		table_data = [
			[dict(zip(c[0], values)) for values in c[1]] for c in combo]

		content_keys = ('table', 'data')
		content_values = zip(tables, table_data)
		return [dict(zip(content_keys, values)) for values in content_values]

	def get(self, table, query=None):
		url = '%s%s?results_per_page=%s' % (self.site, table, self.limit)

		if query:
			url = '%s&q=%s' % (url, dmp(query, cls=CustomEncoder))

		r = g(url, headers=self.HDR)
		return loads(r.text)['objects']

	def post(self, content):
		for piece in content:
			table = piece['table']
			r = None

			for d in piece['data']:
				r = p(
					'%s%s' % (self.site, table),
					data=dmp(d, cls=CustomEncoder), headers=self.HDR)

				if r.status_code != 201:
					print (
						'Response: %s. Request %s with content %s sent to %s'
						% (r.status_code, r.request.data, r._content, r.url))

		return r
