import numpy as np
import pandas as pd

from pprint import pprint
from datetime import datetime as dt
from itertools import imap
from app import db
from app.hermes.models import Event, EventType, Price, Commodity
from sqlalchemy.orm import aliased


def calculate_shares(prices, dividends):
	return 'shares'


def get_prices():
	query = (db.session.query(Price, Commodity).join(Price.commodity)
		.order_by(Price.commodity).filter(Commodity.type_id.in_([1, 3, 4])))

	data = [(0, 'commodity_id'), (0, 'date'), (0, 'close'), (0, 'currency_id')]
	dtype = [('comm_id', np.int), ('date', np.datetime64),
		('price', np.float32), ('curr_id', np.int)]
	index = ['curr_id', 'comm_id', 'date']
	return query.all(), data, dtype, index


def get_dividends():
	query = (db.session.query(Event).order_by(Event.commodity_id)
		.filter(Event.type_id.in_([1])))
	keys = ['commodity_id', 'date', 'value', 'currency_id']
	dtype = [('comm_id', np.int), ('date', np.datetime64), ('dividend',
		np.float32), ('curr_id', np.int)]
	index = ['curr_id', 'comm_id', 'date']
	return query.all(), keys, dtype, index


def get_rates():
	Currency = aliased(Commodity)
	query = (db.session.query(Price, Commodity, Currency).join(Price.commodity)
		.join(Currency, Price.currency).order_by(Price.commodity)
		.filter(Commodity.type_id.in_([5])).filter(Currency.id.in_([1])))

	keys = [(0, 'commodity_id'), (0, 'date'), (0, 'close')]
	dtype = [('comm_id', np.int), ('date', np.datetime64), ('rate', np.float32)]
	index = ['comm_id', 'date']
	return query.all(), keys, dtype, index


def get_values(result, keys):
	try:
		values = [[eval('r[k[0]].%s' % k[1]) for k in keys] for r in result]
	except TypeError:
		values = [[eval('r.%s' % k) for k in keys] for r in result]

	return [tuple(value) for value in values]


def make_df(values, dtype, index):
	ndarray = np.array(values, dtype)
	df = pd.DataFrame.from_records(ndarray)
	df.set_index(index, inplace=True)
	return df
