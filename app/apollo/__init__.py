import numpy as np
import pandas as pd

from pprint import pprint
from datetime import datetime as dt
from app import db
from app.hermes.models import Event, EventType, Price, Commodity
from sqlalchemy.orm import aliased


def calculate_value(shares, prices, rates, native):
	# TODO: check for missing prices
	native = 1
	prices.reset_index(level='comm_id', inplace=True)
	converted = prices.join(rates, how='outer')
	converted = converted.groupby(level='curr_id').fillna(method='pad')

	if native in converted.groupby(level='curr_id').groups.keys():
		converted.rate[native] = converted.rate[native].fillna(1)

	converted.reset_index(inplace=True)
	converted.set_index(['comm_id', 'date'], inplace=True)
	converted['con_price'] = converted.price * converted.rate
	del converted['curr_id'], converted['price'], converted['rate']
	shares['date'] = dt.today()
	shares.set_index('date', inplace=True, append=True)
	df = converted.join(shares, how='outer')
	df = df.groupby(level='comm_id').fillna(method='pad')
	df['value'] = df.con_price * df.shares
	df.reset_index('date', inplace=True)
	del df['con_price'], df['shares'], df['date']
	df = df.dropna(axis=0)
	return df.to_dict()['value']


def convert_values(values, commodities):
	symbols = [commodities.ix[int(x)][0] for x in values.keys()]
	totals = ['%.2f' % x for x in values.values()]
	return zip(symbols, totals)


def get_prices():
	query = (db.session.query(Price, Commodity).join(Price.commodity)
		.order_by(Price.commodity).filter(Commodity.type_id.in_([1, 3, 4])))

	keys = [(0, 'commodity_id'), (0, 'date'), (0, 'close'), (0, 'currency_id')]
	dtype = [('comm_id', np.int), ('date', np.datetime64),
		('price', np.float32), ('curr_id', np.int)]
	index = ['comm_id', 'curr_id', 'date']
	return query.all(), keys, dtype, index


def get_commodities():
	query = (db.session.query(Commodity)
		.filter(Commodity.type_id.in_([1, 3, 4])))
	keys = ['id', 'symbol']
	dtype = [('id', np.int), ('symbol', 'a5')]
	index = ['id']
	return query.all(), keys, dtype, index


def get_dividends():
	query = (db.session.query(Event).order_by(Event.commodity_id)
		.filter(Event.type_id.in_([1])))
	keys = ['commodity_id', 'date', 'value', 'currency_id']
	dtype = [('comm_id', np.int), ('date', np.datetime64), ('dividend',
		np.float32), ('curr_id', np.int)]
	index = ['comm_id', 'curr_id', 'date']
	return query.all(), keys, dtype, index


def get_rates():
	Currency = aliased(Commodity)
	query = (db.session.query(Price, Commodity, Currency).join(Price.commodity)
		.join(Currency, Price.currency).order_by(Price.commodity)
		.filter(Commodity.type_id.in_([5])).filter(Currency.id.in_([1])))

	keys = [(0, 'commodity_id'), (0, 'date'), (0, 'close')]
	dtype = [('curr_id', np.int), ('date', np.datetime64), ('rate', np.float32)]
	index = ['curr_id', 'date']
	return query.all(), keys, dtype, index


def get_values(result, keys):
	try:
		values = [[eval('r[k[0]].%s' % k[1]) for k in keys] for r in result]
	except TypeError:
		values = [[eval('r.%s' % k) for k in keys] for r in result]

	return [tuple(value) for value in values]


def sort_df(df):
	index = df.index.names

	if len(index) > 1:
		for level in reversed(index):
			df = df.sortlevel(level=level)

	return df


def make_df(values, dtype, index):
	"""Return a data frame given a set of components
	more text
	>>> make_df([(6, u'APL')], [('id', np.int), ('symbol', 'a5')], ['id']).columns
	Index([symbol], dtype=object)
	"""

	ndarray = np.array(values, dtype)
	df = pd.DataFrame.from_records(ndarray)
	df.set_index(index, inplace=True)
	return df


def empty_df():
	return pd.DataFrame({})


def get_transactions(prices, reinvestments, shares):
	index = prices.index.names

	if not reinvestments.empty:
		[index.append(x) for x in reinvestments.index.names if x not in index]

	df = prices.reset_index()
	df['shares'] = shares

	if not reinvestments.empty:
		reinvestments = reinvestments.reset_index()
		df = pd.concat([df, reinvestments], ignore_index=True)

	df.set_index(index, inplace=True)
	return df


def get_reinvestments(dividends, prices):
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
	return df, missing


def get_shares(transactions):
	"""Return the sum of shares grouped by commodity
	more text
	"""

	df = transactions.groupby(level='comm_id').sum()
	del df['price']
	return df
