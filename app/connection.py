# -*- coding: utf-8 -*-
"""
	app.connection
	~~~~~~~~~~~~~~

	Provides functions for querying the database
"""

from pprint import pprint
from json import dumps as dmp, loads, JSONEncoder
from requests import get as g, post as p
from sqlalchemy.orm import aliased

from app import db
from app.hermes.models import Event, EventType, Price, Commodity, CommodityType
from app.cronus.models import Transaction, Holding, Account, TrxnType


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
	raw_commodity : tuple
	raw_price : tuple
	raw_transaction : tuple
	"""
	HDR = {'content-type': 'application/json'}
	TABLES = [
		'exchange', 'data_source', 'commodity_group', 'commodity_type',
		'commodity', 'event_type', 'event', 'price', 'person', 'company',
		'account_type', 'account', 'holding', 'trxn_type', 'transaction']

	KEYS = [
		# '[(' is needed so dict doesn't iterate over each character
		('symbol', 'name'),  # exchange
		[('name')],  # data_source
		[('name')],  # commodity_group
		('name', 'group_id'),  # commodity_type
		('symbol', 'name', 'type_id', 'data_source_id', 'exchange_id'),  # commodity
		[('name')],  # event_type
		('type_id', 'commodity_id', 'currency_id', 'value', 'date'),  # event
		('commodity_id', 'currency_id', 'close', 'date'),  # price
		('currency_id', 'first_name', 'last_name', 'email'),  # person
		('name', 'website'),  # company
		[('name')],  # account_type
		('type_id', 'company_id', 'currency_id', 'owner_id', 'name'),  # account
		('commodity_id', 'account_id'),  # holding
		[('name')],  # trxn_type
		(
			'holding_id', 'type_id', 'shares', 'price', 'date',
			'commissionable')] 	# transaction

	def __init__(
			self, site='http://localhost:5000/api/', native=1, display=False):
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
		>>> Connection('http://localhost:5000/api/')  #doctest: +ELLIPSIS
		<app.connection.Connection object at 0x...>
		"""
		self.site = site
		self.native = native
		self.display = display

	@property
	def event(self):
		form_fields = [
			'commodity_id', 'type_id', 'currency_id', 'value', 'date']

		table_headers = ['Symbol', 'Name', 'Unit', 'Value', 'Date']
		Currency = aliased(Commodity)

		query = (
			db.session.query(Event, EventType, Commodity, Currency)
			.join(EventType).join(Event.commodity)
			.join(Currency, Event.currency).order_by(Event.date))

		keys = [
			(2, 'symbol'), (1, 'name'), (3, 'symbol'), (0, 'value'),
			(0, 'date')]

		if self.display:
			returned = form_fields, table_headers, query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def event_type(self):
		form_fields = ['name']
		table_headers = ['Type Name']
		query = db.session.query(EventType).order_by(EventType.name)
		keys = ['name']

		if self.display:
			returned = form_fields, table_headers, query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def price(self):
		form_fields = ['commodity_id', 'currency_id', 'close', 'date']
		table_headers = ['Stock', 'Currency', 'Date', 'Price']
		Currency = aliased(Commodity)
		query = (
			db.session.query(Price, Commodity, Currency)
			.join(Price.commodity).join(Currency, Price.currency)
			.order_by(Price.date))
		keys = [(1, 'symbol'), (2, 'symbol'), (0, 'date'), (0, 'close')]

		if self.display:
			returned = form_fields, table_headers, query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def commodity(self):
		form_fields = [
			'symbol', 'name', 'type_id', 'data_source_id', 'exchange_id']
		table_headers = ['Symbol', 'Name', 'Type']
		query = (
			db.session.query(Commodity, CommodityType).join(CommodityType)
			.order_by(Commodity.name))
		keys = [(0, 'symbol'), (0, 'name'), (1, 'name')]

		if self.display:
			returned = form_fields, table_headers, query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def transaction(self):
		form_fields = [
			'holding_id', 'type_id', 'shares', 'price', 'date', 'commissionable']

		table_headers = [
			'Holding', 'Type', 'Shares', 'Share Price', 'Date', 'Commission']

		query = (
			db.session.query(Transaction, Holding, Account, TrxnType, Commodity)
			.join(Transaction.holding).join(Account, Holding.account)
			.join(TrxnType, Transaction.type).join(Commodity, Holding.commodity))

		keys = [
			(4, 'symbol'), (3, 'name'), (0, 'shares'), (0, 'price'),
			(0, 'date'), (2, 'trade_commission')]

		if self.display:
			returned = form_fields, table_headers, query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def stock(self):
		query = (
			db.session.query(Commodity).filter(
				Commodity.type_id.in_([1, 3, 4])))

		keys = ['id', 'symbol']

		if self.display:
			returned = [], [], query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def dividend(self):
		query = (
			db.session.query(Event).order_by(Event.commodity_id)
			.filter(Event.type_id.in_([1])))

		keys = ['currency_id', 'commodity_id', 'date', 'value']

		if self.display:
			returned = [], [], query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def rate(self):
		Currency = aliased(Commodity)
		query = (
			db.session.query(Price, Commodity, Currency).join(Price.commodity)
			.join(Currency, Price.currency).order_by(Price.commodity)
			.filter(Commodity.type_id.in_([5])).filter(
				Currency.id.in_([self.native])))

		keys = [(0, 'commodity_id'), (0, 'date'), (0, 'close')]

		if self.display:
			returned = [], [], query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def raw_commodity(self):
		query = db.session.query(Commodity)
		keys = ['id', 'symbol']

		if self.display:
			returned = [], [], query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def raw_price(self):
		query = (
			db.session.query(Price, Commodity).join(Price.commodity)
			.order_by(Price.commodity)
			.filter(Commodity.type_id.in_([1, 3, 4])))

		keys = [
			(0, 'currency_id'), (0, 'commodity_id'), (0, 'date'), (0, 'close')]

		if self.display:
			returned = [], [], query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def raw_transaction(self):
		query = (
			db.session.query(Transaction, Holding, Account)
			.join(Transaction.holding).join(Account, Holding.account))

		keys = [
			(2, 'owner_id'), (1, 'account_id'), (1, 'commodity_id'),
			(0, 'type_id'), (0, 'date'), (0, 'shares'), (0, 'price'),
			(2, 'trade_commission')]

		if self.display:
			returned = [], [], query.all(), keys
		else:
			returned = query.all(), keys

		return returned

	@property
	def securities(self):
		filter = {'filters': [{'name': 'group_id', 'op': 'eq', 'val': 1}]}
		return 'commodity_type', filter

	def commodities(self, symbols):
		filter = {'filters': [{'name': 'symbol', 'op': 'in', 'val': symbols}]}
		return 'commodity', filter

	def values(self, result, keys):
		"""Extracts desired values from a query result

		Parameters
		----------
		result : sequence of classes or sequence of sequences of classes
			e.g. sqlalchemy.query.all()

		keys : sequence of attributes or sequence of (int, attribute)
			attributes should be contained in the classes from `result`

		Returns
		-------
		df : list of tuples of values

		Examples
		--------
		# >>> conn = Connection('http://localhost:5000/api/')
		# >>> conn.values(conn.raw_commodity)
		# [(6, u'APL')]
		"""

		try:
			values = [[getattr(r[k[0]], k[1]) for k in keys] for r in result]
		except TypeError:
			values = [[getattr(r, k) for k in keys] for r in result]

		return [tuple(value) for value in values]

	def ids_from_symbols(self, symbols):
		values = self.values(*self.raw_commodity)
		ids = dict(zip([v[1] for v in values], [v[0] for v in values]))

		if hasattr(symbols, 'isalnum'):
			ids = ids.get(symbols, None)
		else:
			ids = [ids.get(s, None) for s in symbols]

		return ids

	def process(self, post_values, tables=None, keys=None):
		tables = (tables or self.TABLES)
		keys = (keys or self.KEYS or [])
		tables = [tables] if hasattr(tables, 'isalnum') else tables
		combo = zip(keys, post_values)

		table_data = [
			[dict(zip(list[0], values)) for values in list[1]]
			for list in combo]

		content_keys = ('table', 'data')
		content_values = zip(tables, table_data)
		return [dict(zip(content_keys, values)) for values in content_values]

	def get(self, table, query=None):
		base = '%s%s' % (self.site, table)
		url = '%s?q=%s' % (base, dmp(query, cls=CustomEncoder)) if query else base
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
