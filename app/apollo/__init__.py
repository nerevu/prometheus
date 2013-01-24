# -*- coding: utf-8 -*-
"""
	app.apollo
	~~~~~~~~~~~~~~

	Provides application manipulation functions for input into visualization
	libraries
"""

import numpy as np
import pandas as pd
import itertools as it

from pprint import pprint
from datetime import datetime as dt, date
from sqlalchemy.orm import aliased

from app import db
from app.hermes.models import Commodity


def char_range(number, letter='a'):
	"""Generates the characters from letter to letter + number, inclusive."""
	for c in xrange(ord(letter), ord(letter) + number):
		yield chr(c)


class DataFrame(pd.DataFrame):
	def __init__(
			self, data=None, dtype=None, index=None, keys=None):
		"""Creates a DataFrame

		Parameters
		----------
		data : sequence of values, Pandas DataFrame, Pandas Series,
			or dict of Pandas Series, optional

		dtype : sequence of ('column name', data type) pairs, optional
		index : subset of column names to use for category names, optional
		keys : sequence of column names, optional

		Examples
		--------
# 		>>> make_df().to_dict()
# 		{}
# 		>>> import numpy as np
# 		>>> make_df([(6, u'APL')], [('id', np.int), ('symbol', 'a5')], ['id']) \
# 		.to_dict()
# 		{'symbol': {6: 'APL'}}
		"""
		sequence = False
		switch = {'frame': data, 'dict': pd.DataFrame(data)}

		try:
			empty = True if data.empty else False
			type = 'frame'
		except AttributeError:
			try:
				empty = False if data.any() else True
				type = 'series'
				switch = {'series': pd.DataFrame({data.name: data})}
			except AttributeError:
				try:
					empty = False if data.values() else True
					type = 'dict'
				except AttributeError:
					empty = False if data else True
					sequence = True
					type = 'sequence'

		if empty:
			df = pd.DataFrame({})
		elif not sequence:
			df = switch.get(type)
		elif dtype:
			ndarray = np.array(data, dtype)
			df = pd.DataFrame.from_records(ndarray)
		else:
			if not keys:
				mod_keys = [c for c in char_range(len(data))]

			try:
				# test for case like [(0, 'commodity_id')
				keys[0][0] / 1
				mod_keys = [k[1] for k in keys]
			except TypeError:
				mod_keys = keys

			zip_data = zip(*data)
			series = [pd.Series(z) for z in zip_data]
			combo = dict(zip(mod_keys, series))
			df = pd.DataFrame(combo)
# 	 		types = [d for d in df.dtypes]
# 	 		dtype = zip(df.dtypes.index, types)
			types = [df.ix[0][p] for p in mod_keys]
			dtype = zip(mod_keys, types)

		if not (empty or index) and sequence:
# 	 		index = [d[0] for d in dtype if d[1].kind in ['i', 'O']]
			index = [
				d[0] for d in dtype if (
					isinstance(d[1], np.int64) or
					isinstance(d[1], date) or
					isinstance(d[1], dt))]

		if not empty and sequence:
			df.set_index(index, inplace=True)

		super(DataFrame, self).__init__(df)

	@property
	def non_date_index(self):
		return [i for i in self.index.names if i != 'date']

	@property
	def sorted(self):
		"""Sorts a pandas DataFrame

		Parameters
		----------
		df : pandas DataFrame

		Returns
		-------
		df : pandas DataFrame or Series sorted by each index

		Examples
		--------
		>>> import numpy as np
		>>> df = DataFrame([(6, u'APL')], [('id', np.int), ('symbol', 'a5')], ['id'])
		>>> df.to_dict()
		{'symbol': {6: 'APL'}}
		"""
		index = self.index.names

		if len(index) > 1:
			for level in reversed(index):
				df = self.sortlevel(level=level)
		else:
			df = self.sort_index()

		return DataFrame(df)

	def merge_index(self, dfs):
		"""
		Merge index with another dataframe

		Parameters
		----------
		Returns
		-------
		df : pandas DataFrame
		"""
		# TODO: switch order of 'currency_id' and 'commodity_id'
		merged_index = self.index.names
		[merged_index.extend(x.index.names) for x in dfs]
		index = [i for i in set(merged_index)]
		index = [i for i in reversed(index)]
		return index

	def split_frame(self, index):
		"""
		Split data frame in two

		Parameters
		----------
		Returns
		-------
		df : pandas DataFrame
		"""
		df = self.reset_index().set_index(index)
		g = [DataFrame(g[1]) for g in df.groupby(level=0)]
		return tuple(g)

	def merge_frames(self, y, on, toffill=[]):
		"""
		Merge with another dataframe

		Parameters
		----------
		Returns
		-------
		df : pandas DataFrame
		"""
		# reset index so I can merge
		#
		# this will auto fill in values for all combinations of
		# 'owner_id', 'account_id' into into merge DataFrame
		# and 'currency_id' into shares DataFrame
		# returns two sets of date fields (x and y)
		x = self.reset_index()
		y.reset_index(inplace=True)
		merged = x.merge(y, on=on, how='outer')
		[merged[f].fillna(method='ffill', inplace=True) for f in toffill]
		return DataFrame(merged)

	def concat_frames(self, df_y, index, delete_x=None, delete_y=None):
		"""
		Concatenate onto another dataframe

		Parameters
		----------
		Returns
		-------
		df : pandas DataFrame
		"""
		df_x = self.copy()

		# rename columns
		to = [word[:-2] for word in delete_x]
		fix_x = dict(zip(delete_y, to))
		fix_y = dict(zip(delete_x, to))
		df_x.rename(columns=fix_x, inplace=True)
		df_y.rename(columns=fix_y, inplace=True)

		# delete remaining columns
		for f in delete_x:
			del df_x[f]

		for f in delete_y:
			del df_y[f]

		# Concatenate and set index
		df = pd.concat([df_x, df_y]).reset_index().set_index(index)
		return DataFrame(df)

	def join_merged(self, index, delete_x=None, delete_y=None):
		"""
		Join a merged dataframe to itself

		Parameters
		----------
		Returns
		-------
		df : pandas DataFrame
		"""
		# remove the common fields between the 2 data frames
		df_x = self.copy()
		df_y = self.copy()

		for f in delete_x:
			del df_x[f]

		for f in delete_y:
			del df_y[f]

		# set index so I can now join the data frames since they have
		# different fields
		df_x = df_x.rename(columns={'date_x': 'date'}).set_index(index)
		df_y = df_y.rename(columns={'date_y': 'date'}).set_index(index)
		return DataFrame(df_x.join(df_y, how='outer'))

	def fill_missing(
			self, toffill=[], tobfill=[], tointerpolate=[], dedupe=False):
		"""
		Merge with shares

		Parameters
		----------
		Returns
		-------
		df : pandas DataFrame
		"""
		df = self.copy()
		index = self.non_date_index
		missing = False

		if 'date' in df.index.names:
			real_index = index + ['date']
			df.reset_index(inplace=True)
			df.set_index(real_index, inplace=True)

		if not (toffill or tobfill or tointerpolate):
			toffill = [f for f in df]

		# fill in missing values
		for g in df.groupby(level=index).groups:
			for ff in toffill:
				df.ix[g][ff] = df.ix[g][ff].fillna(method='ffill')

			for bf in tobfill:
				df.ix[g][bf] = df.ix[g][bf].fillna(method='bfill')

			for int in tointerpolate:
				# fill in blanks with time interpolated values
				if df.ix[g][int].abs().sum() >= 0:
					df.ix[g][int] = df.ix[g][int].interpolate(method='time')
				else:
					missing = True

		df = df.drop_duplicates() if dedupe else df
		return DataFrame(df), missing


class Portfolio(DataFrame):
	"""
	Collection of commodity transactions.

	Attributes
	----------
	transactions : pandas DataFrame
			transactions.dtypes =
				shares        float64
				price         float64
				commission    float64

			transactions.index.names = [
					'owner_id',
					'account_id',
					'commodity_id',
					'trxn_type_id',
					'date']

			[type(i) for i in transactions.index[0]] = [
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<class 'pandas.tslib.Timestamp'>]

	shares : pandas Series
			shares.dtype = dtype('float64')
			shares.name = 'shares'

			shares.index.names = [
				'owner_id',
				'account_id',
				'commodity_id',
				'date']

			[type(i) for i in shares.index[0]] = [
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<class 'pandas.tslib.Timestamp'>]

	currency_id : INT
		default currency, must be a valid id in the Commodities table

	Examples
	--------
# 	>>> from app import db
# 	>>> from app.cronus.models import Transaction
# 	>>> result = db.session.query(Transaction, Holding, Account). \
# 	join(Transaction.holding).join(Account, Holding.account).all()
# 	>>> keys = [(1, 'commodity_id'), (1, 'account_id'), (2, 'owner_id'), \
# 	(0, 'type_id'), (0, 'shares'), (0, 'price'), (0, 'date'), \
# 	(2, 'trade_commission')]
# 	>>> data = [[eval('r[k[0]].%s' % k[1]) for k in keys] for r in result]
# 	>>> myportfolio = Portfolio(data)

	"""

	EMPTY_DF = pd.DataFrame({})
	EMPTY_S = pd.Series({})

	def __init__(
			self, data=None, keys=None, index=None, dtypes=None,
			currency_id=1, commodities={}):
		"""
		Class constructor.

		Parameters
		----------
		data : sequence of values or Pandas DataFrame, optional
		keys : sequence of column names, optional
		index : sequence of the subset of column names, optional
			to use for category names

		dtypes : sequence of data types, optional
		currency_id : INT, optional
			id of the default currency
		commodities : dict, or Pandas Series, or Pandas DataFrame, optional
			commodity_id to commodity mapping

		See also
		--------
		from_prices : make constructor from prices
		"""

		INT = np.int
		FLT = np.float32
		DTIME = np.datetime64

		try:
			empty = True if data.empty else False
			sequence = False
		except AttributeError:
			empty = False if data else True
			sequence = True

		if empty:
			super(Portfolio, self).__init__()
		elif not sequence:
			super(Portfolio, self).__init__(df)
		else:
			keys = (
				keys or [
					'owner_id', 'account_id', 'commodity_id', 'trxn_type_id',
					'shares', 'price', 'date', 'commission'])

			index = (
				index or [
					'owner_id', 'account_id', 'commodity_id', 'trxn_type_id',
					'date'])

			dtypes = (dtypes or [INT, INT, INT, INT, FLT, FLT, DTIME, FLT])
			dtype = zip(keys, dtypes)

			super(Portfolio, self).__init__(data, dtype, index)

		try:
			empty = True if commodities.empty else False
			dict = False
		except AttributeError:
			empty = False if commodities.values() else True
			dict = True

		if empty:
			commodities = {}
		elif not dict:
			commodities = commodities.symbol.to_dict()

		self.commodities = commodities
		self.currency_id = currency_id

	@property
	def transactions(self):
		"""Portfolio transactions
		"""

		pass

	@property
	def shares(self):
		"""Sum of shares grouped by commodity
		"""
		df = self.reset_index(level='trxn_type_id')
		del df['price'], df['trxn_type_id'], df['commission']
		index = df.index.names
		df = df.groupby(level=index).cumsum()
# 		for g in df.groupby(level=index).groups:
# 			df.ix[g] = df.ix[g].cumsum()

		return df

	@classmethod
	def from_prices(cls):
		"""
		Construct Portfolio from prices

		Parameters
		----------

		Returns
		-------
		Portfolio

		Examples
		--------
		"""

		pass
# 		return Portfolio()

	def calc_reinvestments(self, dividends, prices):
		"""Calculates the number of shares purchased assuming dividend reinvestment

		Parameters
		----------
		dividends : pandas Series of commodity dividends
			dividends.dtype = dtype('float64')
			dividends.name = 'value'

			dividends.index.names = [
				'currency_id',
				'commodity_id',
				'date']

			[type(i) for i in dividends.index[0]] = [
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<class 'pandas.tslib.Timestamp'>]

		prices : pandas Series of commodity prices
			prices.dtype = dtype('float64')
			prices.name = 'close'

			prices.index.names = [
				'currency_id',
				'commodity_id',
				'date']

			[type(i) for i in prices.index[0]] = [
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<class 'pandas.tslib.Timestamp'>]

		Returns
		-------
		reinvestments : pandas Series of dividend reinvestments
			reinvestments.name = 'new_shares'
			reinvestments.dtype = dtype('float64')

			reinvestments.index.names = [
				'owner_id',
				'account_id',
				'currency_id',
				'commodity_id',
				'date']

			[type(i) for i in reinvestments.index[0]] = [
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<class 'pandas.tslib.Timestamp'>]

		Examples
		--------
# 		>>> from app import db
# 		>>> from app.cronus.models import Transaction, Holding, Account
# 		>>> result = db.session.query(Transaction, Holding, Account) \
# 		.join(Transaction.holding).join(Account, Holding.account).all()
# 		>>> keys = [(1, 'commodity_id'), (1, 'account_id'), (2, 'owner_id'), \
# 		(0, 'type_id'), (0, 'shares'), (0, 'price'), (0, 'date'), \
# 		(2, 'trade_commission')]
# 		>>> data = [[eval('r[k[0]].%s' % k[1]) for k in keys] for r in result]
# 		>>> myportfolio = Portfolio(data).to_dict()
# 		"""

		if dividends.any() and prices.any():
			# first join dividends and prices
			try:
				df_dict = {'value': dividends, 'close': prices}
				joined = DataFrame(df_dict)
			except ValueError:
				joined = DataFrame(dividends.join(prices, how='outer'))

			y = ['date_x', 'value', 'close']
			x = ['date_y', 'shares']
			merged = joined.merge_frames(self.shares, 'commodity_id')
			index = joined.merge_index([self.shares])
			df = merged.join_merged(index, x, y)
			df, missing = df.fill_missing(
				['shares'], ['shares'], ['close'], True)

			# remove 'currency_id' from index
			df.reset_index(level='currency_id', inplace=True)
			index = df.non_date_index

			# fill blank dividends with 0
			df.value.fillna(0, inplace=True)

			# calculate number of shares purchased
			df['dividend_received'] = df['value'] * df['shares']
			df['purchases'] = df['dividend_received'] / df['close']
			df['div_shares'] = df['purchases'].groupby(level=index).cumsum()
			reinvestments = df['div_shares']
		else:
			reinvestments = DataFrame()

		return reinvestments

	def calc_value(
			self, prices, rates, reinvestments=EMPTY_S, native=1, how='stock',
			mode='latest', convert=False):
		"""
		Calculate the portfolio value grouped by commodity id

		Parameters
		----------
		prices : pandas Series or DataFrame of commodity prices
			prices.dtype = dtype('float64')
			prices.name = 'close'

			prices.index.names = [
				'currency_id',
				'commodity_id',
				'date']

			[type(i) for i in prices.index[0]] = [
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<class 'pandas.tslib.Timestamp'>]

		rates : pandas Series of exchange rates
			rates.dtypes = dtype('float64')
			rates.name = 'close'

			rates.index.names = [
				'currency_id',
				'commodity_id',
				'date']

			[type(i) for i in rates.index[0]] = [
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<class 'pandas.tslib.Timestamp'>]

		reinvestments : pandas Series of dividend reinvestments, optional
			rates.dtypes = dtype('float64')
			rates.name = 'close'

			rates.index.names = [
				'currency_id',
				'commodity_id',
				'date']

			[type(i) for i in rates.index[0]] = [
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<class 'pandas.tslib.Timestamp'>]

		native : int, default 1
			id of the native currency

		convert : boolean, default False
			convert commodity ids to symbols

		Returns
		-------
		df : pandas DataFrame
		"""

		if prices.any():
			# TODO: check for missing prices
			# first rename rates column and index
			try:
				rates = pd.DataFrame({'rate': rates})
			except ValueError:
				pass

			rates.reset_index(inplace=True)
			rates.rename(
				columns={'commodity_id': 'currency_id', 'close': 'rate'},
				inplace=True)
			rates.set_index(['currency_id', 'date'], inplace=True)

			# now join prices and rates
			try:
				prices = pd.DataFrame({'price': prices})
			except ValueError:
				pass

			prices.reset_index(level='commodity_id', inplace=True)
			converted = prices.join(rates, how='left')
			converted = converted.groupby(level='currency_id').fillna(
				method='pad')

			# fill in native currency rates with value of 1
			if native in converted.groupby(level='currency_id').groups.keys():
				converted.rate[native].fillna(1, inplace=True)

			# calculate share closing prices in native currency
			converted = DataFrame(converted.reset_index())
			converted.set_index(['commodity_id', 'date'], inplace=True)
			converted['native_price'] = converted.close * converted.rate
			del converted['currency_id'], converted['close'], converted['rate']

			# join with shares
			y = ['date_x', 'native_price']
			x = ['date_y', 'shares']
			merged = converted.merge_frames(self.shares, 'commodity_id')
			index = converted.merge_index([self.shares])
			df = merged.join_merged(index, x, y)
			df, missing = df.fill_missing(
				['shares'], ['shares'], ['native_price'], True)

			# join with reinvestments
			df = DataFrame(df.join(reinvestments, how='outer'))
# 			max_date = max([i[3] for i in df.index])

			# group transactions by date
			index = df.index.names
			new_index = df.non_date_index
			sorted = df.sorted

			# make sep data frames for each date
			# TODO: account for multiple owners and/or accounts
			dfs = [df for df in sorted.split_frame('date')]
			date_list = [(df.index[0], len(df)) for df in dfs]
			by_date = dict(date_list)
			max_entries = max(by_date.values())
			items = by_date.items()

			##### 					experimental 					#####
			#															#
			# fill in missing values so I have the same number of
			# observances for each date (currently only works for a set
			# of 2 dates
			#
			# merge sep data frames together
			df_x, df_y = tuple(dfs)
			x = ['date_y', 'native_price_y', 'shares_y', 'div_shares_y']
			y = ['date_x', 'native_price_x', 'shares_x', 'div_shares_x']
			merged = df_x.merge_frames(df_y, new_index, ['date_x', 'date_y'])
			df = merged.join_merged(index, x, y)

			# combine *_x and *_y values
			df_x, df_y = df.split_frame('date')
			df = df_x.concat_frames(df_y, index, x[1:], y[1:]).sorted
			#															#
			##### 					experimental 					#####

			# fill in missing values
			df, missing = df.fill_missing(
				['shares', 'div_shares'], ['shares', 'div_shares'],
				['native_price'])

			# calculate value
			df['total_shares'] = df['shares'] + df['div_shares']
			df['value'] = df.native_price * df.total_shares
			old_index = df.non_date_index
			df.reset_index(inplace=True)

			# select report type
			switch = {
				'owner': ['owner_id'],
				'account': ['account_id'],
				'stock': ['commodity_id'],
				'owner_stock': ['owner_id', 'commodity_id'],
				'account_stock': ['account_id', 'commodity_id'],
				'owner_account': ['owner_id', 'account_id']}

			new_index = ['date'] + switch.get(how.lower())
			to_delete = [i for i in old_index if i not in new_index]
			df.set_index(new_index, inplace=True)
			df = df.sorted

			for f in to_delete:
				del df[f]

			df_dict = {'total_shares': df.total_shares, 'value': df.value}
			all_dates = DataFrame(df_dict)

			# view most recent data irrespective of incomplete entries
			# or view most recent data that contains values for all entries
			switch = {
				'latest': max(by_date.keys()),
				'uniform': max([d[0] for d in items if d[1] == max_entries])}

			the_date = switch.get(mode.lower())
			selected = all_dates.groupby(level='date').get_group(the_date)
			selected.reset_index('date', inplace=True)
			values = selected.to_dict()['value']

			if convert:
				pass
		else:
			values = {}

		return values

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

		if values and not self.commodities.values():
			symbols = [self.commodities[x] for x in values.keys()]
			totals = ['%.2f' % x for x in values.values()]
			data = zip(symbols, totals)
		elif values:
			data = values.items()
		else:
			data = [('N/A', 0)]

		return data
