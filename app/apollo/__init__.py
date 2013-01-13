# -*- coding: utf-8 -*-
"""
	app.apollo
	~~~~~~~~~~~~~~

	Provides application manipulation functions for input into visualization
	libraries
"""

import numpy as np
import pandas as pd

from pprint import pprint
from datetime import datetime as dt
from sqlalchemy.orm import aliased

from app import db
from app.hermes.models import Event, EventType, Price, Commodity


def get_prices():
	query = (
		db.session.query(Price, Commodity).join(Price.commodity)
		.order_by(Price.commodity).filter(Commodity.type_id.in_([1, 3, 4])))

	keys = [(0, 'commodity_id'), (0, 'date'), (0, 'close'), (0, 'currency_id')]
	dtype = [
		('comm_id', np.int), ('date', np.datetime64), ('price', np.float32),
		('curr_id', np.int)]

	index = ['comm_id', 'curr_id', 'date']
	return query.all(), keys, dtype, index


def get_commodities():
	query = (
		db.session.query(Commodity).filter(Commodity.type_id.in_([1, 3, 4])))
	keys = ['id', 'symbol']
	dtype = [('id', np.int), ('symbol', 'a5')]
	index = ['id']
	return query.all(), keys, dtype, index


def get_dividends():
	query = (
		db.session.query(Event).order_by(Event.commodity_id)
		.filter(Event.type_id.in_([1])))

	keys = ['commodity_id', 'date', 'value', 'currency_id']
	dtype = [
		('comm_id', np.int), ('date', np.datetime64), ('dividend', np.float32),
		('curr_id', np.int)]

	index = ['comm_id', 'curr_id', 'date']
	return query.all(), keys, dtype, index


def get_rates():
	Currency = aliased(Commodity)
	query = (
		db.session.query(Price, Commodity, Currency).join(Price.commodity)
		.join(Currency, Price.currency).order_by(Price.commodity)
		.filter(Commodity.type_id.in_([5])).filter(Currency.id.in_([1])))

	keys = [(0, 'commodity_id'), (0, 'date'), (0, 'close')]
	dtype = [('curr_id', np.int), ('date', np.datetime64), ('rate', np.float32)]
	index = ['curr_id', 'date']
	return query.all(), keys, dtype, index


def get_values(result, keys):
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
	# >>> from app import db
	# >>> from app.hermes.models import Commodity
	# >>> get_values(db.session.query(Commodity).all(), ['id', 'symbol'])
	# [(6, u'APL')]
	"""

	try:
		values = [[eval('r[k[0]].%s' % k[1]) for k in keys] for r in result]
	except TypeError:
		values = [[eval('r.%s' % k) for k in keys] for r in result]

	return [tuple(value) for value in values]


def make_df(values, dtype, index):
	"""Creates a DataFrame

	Parameters
	----------
	values : sequence of values
	dtype : sequence of ('column name', data type) pairs
	index : sequence of column names


	Returns
	-------
	df : data
		Explanation

	Examples
	--------
	>>> import numpy as np
	>>> make_df([(6, u'APL')], [('id', np.int), ('symbol', 'a5')], ['id']) \
	.to_dict()
	{'symbol': {6: 'APL'}}
	"""

	ndarray = np.array(values, dtype)
	df = pd.DataFrame.from_records(ndarray)
	df.set_index(index, inplace=True)
	return df


def empty_df():
	"""Creates an empty pandas DataFrame

	Returns
	-------
	df : pandas DataFrame

	Examples
	--------
	>>> empty_df().to_dict()
	{}
	"""
	return pd.DataFrame({})


def sort_df(df):
	"""Sorts a pandas DataFrame

	Parameters
	----------
	df : pandas DataFrame

	Returns
	-------
	df : pandas DataFrame sorted by each index

	Examples
	--------
	>>> import numpy as np
	>>> df = make_df([(6, u'APL')], [('id', np.int), ('symbol', 'a5')], ['id'])
	>>> sort_df(df).to_dict()
	{'symbol': {6: 'APL'}}
	"""
	index = df.index.names

	if len(index) > 1:
		for level in reversed(index):
			df = df.sortlevel(level=level)

	return df


def get_reinvestments(dividends, prices):
	"""Calculates the number of shares

	Parameters
	----------
	dividends : pandas DataFrame
	prices : pandas DataFrame

	Returns
	-------
	df : pandas DataFrame sorted by each index

	Examples
	--------
	>>> import numpy as np
	>>> df = make_df([(6, u'APL')], [('id', np.int), ('symbol', 'a5')], ['id'])
	>>> sort_df(df).to_dict()
	{'symbol': {6: 'APL'}}
	"""
	if not dividends.empty and not prices.empty:
		df = dividends.join(prices, how='outer')
		index = df.index.names[:-1]	 # exclude the date index

		for g in df.groupby(level=index).groups:
			if df.ix[g].price.sum() > 0:
				df.ix[g].price = df.ix[g].price.interpolate(method='time')
				missing = False
			else:
				missing = True

		df['shares'] = df['dividend'] / df['price']
		del df['dividend']
	else:
		df, missing = empty_df(), False

	return df, missing


class Portfolio(object):
	"""
	Collection of commodity transactions.

	Attributes
	----------
	transactions : pandas data-frame
	commodities : pandas data-frame
	shares : pandas data-frame
	"""

	empty_df = pd.DataFrame({})

	def __init__(self, transactions=empty_df, commodities=empty_df):
		"""
		Class constructor.

		Parameters
		----------
		transactions : pandas data-frame, optional
		commodities : pandas data-frame, optional

		See also
		--------
		from_prices : make constructor from prices
		"""

		self.transactions = sort_df(transactions)
		self.commodities = commodities

	@property
	def shares(self):
		"""Sum of shares grouped by commodity
		"""

		df = self.transactions.groupby(level='comm_id').sum()
		del df['price']
		df['date'] = dt.today()
		df.set_index('date', inplace=True, append=True)
		return df

	@classmethod
	def from_prices(cls, prices, commodities=empty_df, shares=100):
		"""
		Construct Portfolio from prices

		Parameters
		----------
		prices : pandas data-frame
		commodities : pandas data-frame, optional
		reinvestments : pandas data-frame, optional
		shares : int, default 100
			number of shares to purchase @each price

		Returns
		-------
		Portfolio
		"""

		if not prices.empty:
			index = prices.index.names
			trnx = prices.reset_index()
			trnx['shares'] = shares
			trnx.set_index(index, inplace=True)
		else:
			trnx = cls.empty_df

		return Portfolio(trnx, commodities)

	def calculate_value(self, prices, rates, native=1, convert=False):
		"""
		Calculate the portfolio value grouped by commodity id

		Parameters
		----------
		prices : pandas data-frame
		rates : pandas data-frame
		native : int, default 1
			id of the native currency
		convert : boolean, default False
			convert to commodity ids to symbols

		Returns
		-------
		df : pandas data-frame
		"""

		if not prices.empty:
			# TODO: check for missing prices
			prices.reset_index(level='comm_id', inplace=True)
			converted = prices.join(rates, how='outer')
			converted = converted.groupby(level='curr_id').fillna(method='pad')

			if native in converted.groupby(level='curr_id').groups.keys():
				converted.rate[native] = converted.rate[native].fillna(1)

			converted.reset_index(inplace=True)
			converted.set_index(['comm_id', 'date'], inplace=True)
			converted['con_price'] = converted.price * converted.rate
			del converted['curr_id'], converted['price'], converted['rate']
			df = converted.join(self.shares, how='outer')
			df = df.groupby(level='comm_id').fillna(method='pad')
			df['value'] = df.con_price * df.shares
			df.reset_index('date', inplace=True)
			del df['con_price'], df['shares'], df['date']
			df = df.dropna(axis=0)
			df = df.to_dict()['value']

			if convert:
				pass
		else:
			df = self.empty_df

		return df

	def convert_values(self, values):
		"""
		Converts Portfolio values into a more parseable format

		Parameters
		----------
		values : dict {id: value}

		Returns
		-------
		data : sequence of ('symbol', value)
		"""

		if values and not self.commodities.empty:
			symbols = [self.commodities.ix[int(x)][0] for x in values.keys()]
			totals = ['%.2f' % x for x in values.values()]
			data = zip(symbols, totals)
		else:
			data = [('N/A', 0)]

		return data
