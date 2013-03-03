# -*- coding: utf-8 -*-
"""
	app.cronus
	~~~~~~~~~~~~~~

	Provides libraries for importing portfolio data from multiple sources
"""

import csv
import numpy as np
import pandas as pd
import itertools as it

from pprint import pprint
from datetime import datetime as dt, date

from app.connection import Connection


def char_range(number, letter='a'):
	"""Generates the characters from letter to letter + number, inclusive."""
	for c in xrange(ord(letter), ord(letter) + number):
		yield chr(c)


class DataSource(Connection):
	"""
	Generic data source.
	"""
	def __init__(self, site=None, native=1, display=False):
		"""Creates a DataSource

		Parameters
		----------
		site : a string
			api endpoint

		native : a number, default 1
			id of the native currency

		display : boolean, default False

		Examples
		--------
		>>> DataSource('http://localhost:5000/api/')  # doctest: +ELLIPSIS
		<app.cronus.DataSource object at 0x...>
		"""
		super(DataSource, self).__init__(site, native, display)


class CSV(DataSource):
	"""
	CSV data source.

	Attributes
	----------
	value : list of lists
		csv contents
	"""
	def __init__(
			self, file=None, site=None, native=1, display=False, delimiter=',',
			quotechar='"'):
		"""Creates a CSV DataSource

		Parameters
		----------
		file : a string
			the csv location

		site : a string
			api endpoint

		native : a number, default 1
			id of the native currency

		display : boolean, default False
		delimiter : a character, default ','
			the csv field delimiter

		quotechar : a character, default '"'
			the text quote character

		Examples
		--------
		>>> CSV('file.csv', 'http://localhost:5000/api/')  # doctest: +ELLIPSIS
		<app.cronus.CSV object at 0x...>
		"""
		self.file = file
		self.delimiter = delimiter
		self.quotechar = quotechar
		super(CSV, self).__init__(site, native, display)

	@property
	def values(self):
		transactions = []

		if self.file:
			with open(self.file, 'rb') as csvfile:
				reader = csv.reader(
					csvfile, delimiter=self.delimiter, quotechar=self.quotechar)

				[transactions.append(row) for row in reader]

		return transactions

	@property
	def num_trnx(self):
		return len(self.values) - 1

	def load(self):
		values = [[tuple(v) for v in self.values[1:]]]
		tables = ['transaction']
		keys = [tuple(self.values[0])]
		return self.process(values, tables, keys)


class GnuCash(DataSource):
	"""
	GnuCash data source.

	Attributes
	----------
	"""
	def __init__(self, file, site, native=1, display=False):
		"""Creates a GnuCash DataSource

		Parameters
		----------
		file : a string
			the GnuCash file location

		site : a string
			api endpoint

		native : a number, default 1
			id of the native currency

		display : boolean, default False

		Examples
		--------
		>>> CSV('file.gnucash', 'http://localhost:5000/api/') # doctest: +ELLIPSIS
		<app.cronus.CSV object at 0x...>
		"""
		super(GnuCash, self).__init__(site, native, display)


class DataObject(pd.DataFrame):
	"""
	Abstract DataFrame class.

	Attributes
	----------
	non_date_index : list of strings
		the index minus date fields

	sorted : DataObject
		the DataObject sorted by its index

	unindexed : DataObject
		the DataObject with its index reset
	"""
	def __init__(
			self, data=None, dtype=None, keys=None, index=None, series=False):
		"""Creates a DataObject

		Parameters
		----------
		data : a sequence of values, a Pandas DataFrame, a Series,
			or a dict of Series, optional

		dtype : a sequence of ('column name', data type) pairs, optional
		index : a sequence of column names to use for category names, optional
		keys : a sequence of column names, optional
		series : boolean, default False
			Treat a single instance of sequential data as a series
			[('Tom', 'Dick', 'Jane')] as opposed to a set [(1, 'Tom', 34)].
			Does not apply to multiple sequences [(1, 2, 3), ('a', 'b', 'c')].
			These are always treated as sets and should be entered as
			[(1, 'a'), (2, 'b'), (3, 'c')] or zip((1, 2, 3), ('a', 'b', 'c'))

		Examples
		--------
		>>> DataObject().to_dict()
		{}
		>>> DataObject([(6, 'APL')]).to_dict()
		{1: {0: 6}, 2: {0: 'APL'}}
		>>> import numpy as np
		>>> DataObject([(6, u'APL')], [('id', np.int), ('symbol', 'a5')], \
		index=['id']).to_dict()
		{'symbol': {6: 'APL'}}
		>>> import pandas as pd
		>>> series1 = pd.Series((6, 7, 8))
		>>> DataObject(series1).to_dict()
		{None: {0: 6, 1: 7, 2: 8}}
		>>> series2 = pd.Series(('APL', 'IBM', 'CAT'))
		>>> DataObject({'one': series1, 'two': series2}).to_dict()
		{'two': {0: 'APL', 1: 'IBM', 2: 'CAT'}, 'one': {0: 6, 1: 7, 2: 8}}
		"""
		data_values = [
			('empty', True, 'frame', False),
			('any', False, 'series', True),
			('values', False, 'dict', True),
			(None, False, 'sequence', False)]

		data_keys = ('attr', 'empty', 'stype', 'ismeth')
		data_dict = [dict(zip(data_keys, values)) for values in data_values]

		for d in data_dict:
			try:
				attr = data if not d['attr'] else getattr(data, d['attr'])
				test = attr() if d['ismeth'] else attr
			except AttributeError:
				continue
			else:
				empty = d['empty'] if test else not d['empty']
				stype = d['stype']
				sequence = True if stype.startswith('seq') else False
				break

		if stype.startswith('f'):
			default_df = data
		elif stype.startswith('ser'):
			default_df = pd.DataFrame({data.name: data})
		elif stype.startswith('d'):
			default_df = pd.DataFrame(data)

		try:
			if keys and hasattr(keys[0][0], 'denominator'):
				# test for case like [(0, 'commodity_id')]
				keys = [k[1] for k in keys]
		except TypeError:
			pass

		if not keys and not index:
			keys, index = [], []
		elif keys and not index:
			index = [k for k in keys if k.endswith('_id') or k.startswith('date')]
		elif not keys and index:
			keys = index
		elif not index:
			index = []

		if empty:
			data = self.fill_data(set(keys).difference(index), index)
			df = pd.DataFrame(data, columns=keys)
		elif not sequence:
			df = default_df
		elif dtype:
			ndarray = np.array(data, dtype)
			df = pd.DataFrame.from_records(ndarray)
		else:
			transpose = True if len(data) == 1 and not series else False
			fix = None

			if transpose and not keys:
				keys = range(1, len(data[0]) + 1)
			elif not keys:
				keys = [c for c in char_range(len(data))]

			if transpose and keys:
				fix = dict(zip(range(len(keys)), keys))

			if len(data) == 1:
				pdseries = [pd.Series(*data)]
			else:
				zip_data = zip(*data)
				pdseries = [pd.Series(z) for z in zip_data]

			if transpose:
				df = pd.DataFrame(pdseries)
				df = df.rename(columns=fix) if fix else df
			else:
				df = pd.DataFrame(dict(zip(keys, pdseries)))

			types = [df.ix[0][p] for p in keys]
			dtype = zip(keys, types)

		if not index and dtype:
			# add date data to the index
			index = [d[0] for d in dtype if hasattr(d[1], 'year')]

		if index:
			df.set_index(index, inplace=True)

		super(DataObject, self).__init__(df)

	@property
	def non_date_index(self):
		return list(set(self.index.names).difference(['date']))

	@property
	def sorted(self):
		if (len(self) > 1 and len(self.index.names) > 1):
			for level in reversed(self.index.names):
				df = self.sortlevel(level=level)

			df = DataObject(df)

		elif len(self) > 1:
			df = DataObject(self.sort_index())
		else:
			df = self

		return df

	@property
	def unindexed(self):
		df = self.reset_index() if self.index.names[0] else self
		return df

	def merge_index(self, dfs):
		"""
		Merge current index with another

		Parameters
		----------
		dfs : DataFrame/DataObject or sequence of DataFrame/DataObjects

		Returns
		-------
		index : merged index

		Examples
		--------
		>>> df1, df2 = DataObject([(6, 'APL')]), DataObject([(2, 'IBM')])
		>>> df1.merge_index(df2)
		[None]
		"""
		# TODO: switch order of 'currency_id' and 'commodity_id'
		merged = set(self.index.names)

		if hasattr(dfs, 'empty'):
			dfs = [dfs]

		for x in dfs:
			merged = merged.union(x.index.names)

		return list(reversed(list(merged)))

	def split_frame(self, index):
		"""
		Split data frame by an index

		Parameters
		----------
		index : string
			used to sep the DataObject into groups

		Returns
		-------
		tuple of DataObjects

		Examples
		--------
		>>> df = DataObject([(6, 'APL'), (2, 'IBM')])
		>>> df1, df2 = df.split_frame('a')
		>>> df1.to_dict()
		{'b': {2: 'IBM'}}
		>>> df2.to_dict()
		{'b': {6: 'APL'}}
		"""
		df = self.unindexed.set_index(index)
		g = [DataObject(g[1]) for g in df.groupby(level=0)]
		return tuple(g)

	def merge_frame(self, y, on, toffill=None):
		"""
		Merge a DataObject with another a DataFrame/DataObject

		Parameters
		----------
		y : DataObject or DataFrame
		on : string
		toffill : sequence of strings

		Returns
		-------
		DataObject

		Examples
		--------
		>>> df1 = DataObject([(6, 'APL')])
		>>> df2 = DataObject([(2, 'IBM')])
		>>> df1.merge_frame(df2, 2).to_dict()
		{2: {0: 'APL', 1: 'IBM'}, '1_y': {0: nan, 1: 2.0}, '1_x': {0: 6.0, 1: nan}}
		"""
		# reset index so I can merge
		#
		# this will auto fill in values for all combinations of
		# 'owner_id', 'account_id' into into merge DataFrame
		# and 'currency_id' into shares DataFrame
		# returns two sets of date fields (x and y)
		x = self.unindexed
		y = DataObject(y).unindexed
		toffill = (toffill or [])

		merged = x.merge(y, on=on, how='outer')
		[merged[f].fillna(method='ffill', inplace=True) for f in toffill]
		return DataObject(merged)

	def concat_frames(self, y, index=None, delete_x=None, delete_y=None):
		"""
		Concatenate a DataObject onto a DataFrame/DataObject
		Works like pandas.concat but can operate object with indices and
		with overlapping and/or non-overlapping rows

		Parameters
		----------
		y : DataObject or DataFrame
		index : string, optional
		delete_x : sequence of strings, optional
		delete_y : sequence of strings, optional

		Returns
		-------
		DataObject

		Examples
		--------
		>>> df1, df2 = DataObject([(1, 'a')]), DataObject([(2, 'b')])
		>>> df1.concat_frames(df2).to_dict()
		{1: {0: 2}, 2: {0: 'b'}}
		>>> df1.concat_frames(df2, 1).to_dict()
		{2: {1: 'a', 2: 'b'}}
		"""
		x = self.copy()
		delete_x = (delete_x or [])
		delete_y = (delete_y or [])

		# rename columns
		to = [word[:-2] for word in delete_x]
		fix_x = dict(zip(delete_y, to))
		fix_y = dict(zip(delete_x, to))
		x.rename(columns=fix_x, inplace=True)
		y.rename(columns=fix_y, inplace=True)

		# delete remaining columns
		for f in delete_x:
			del x[f]

		for f in delete_y:
			del y[f]

		# Concatenate and set index
		df = DataObject(pd.concat([x, y]))
		df = df.unindexed.set_index(index) if index else df
		return df

	def join_merged(self, index=None, delete_x=None, delete_y=None):
		"""
		Join a merged dataframe to itself

		Parameters
		----------
		index : string, optional
		delete_x : sequence of strings, optional
		delete_y : sequence of strings, optional

		Returns
		-------
		DataObject

		Examples
		--------
		>>> df = DataObject()
		>>> df.join_merged().to_dict()
		{}
		"""
		# remove the common fields between the 2 data frames
		df_x = self.copy()
		df_y = self.copy()
		delete_x = (delete_x or [])
		delete_y = (delete_y or [])

		for f in delete_x:
			del df_x[f]

		for f in delete_y:
			del df_y[f]

		# set index so I can now join the data frames since they have
		# different fields
		df_x = df_x.rename(columns={'date_x': 'date'})
		df_y = df_y.rename(columns={'date_y': 'date'})
		df_x, df_y = (df_x, df_y) if not index else (
			df_x.set_index(index), df_y.set_index(index))
		return DataObject(df_x.join(df_y, how='outer'))

	def fill_data(self, columns=None, index=None):
		"""
		Provide data to fill the columns and index of a DataFrame

		Parameters
		----------
		columns : sequence of strings
			The keys to use for the columns

		index : sequence of strings
			The keys to use for the index

		Returns
		-------
		list of a tuple

		Examples
		--------
		>>> index = ['owner_id', 'account_id', 'date']
		>>> columns = ['shares', 'price']
		>>> DataObject().fill_data(columns, index)
		[(1, 1, datetime.datetime(2013, 1, 1, 0, 0), 0, 0)]
		"""
		i = len(index) if index else 0
		c = len(columns) if columns else 0

		if i and c:
			keys = list(it.chain(index, columns))
		else:
			keys = (index or columns or [])

		data = list(it.chain(it.repeat(1, i), it.repeat(0, c)))

		if 'date' in keys:
			data[dict(zip(keys, range(i + c)))['date']] = dt(2013, 1, 1)

		return [tuple(data)]

	def fill_missing(
			self, toffill=None, tobfill=None, tointerpolate=None, dedupe=False):
		"""
		Fill in missing values of a DataObject

		Parameters
		----------
		toffill : sequence of strings
		tobfill : sequence of strings
		tointerpolate : sequence of strings
		dedupe : sequence of strings

		Returns
		-------
		DataObject
		missing : boolean
			True if interpolate was unable to fill in all values

		Examples
		--------
		>>> df = DataObject()
		>>> df, missing = df.fill_missing(['list'])
		>>> df.to_dict()
		{}
		>>> missing
		False
		"""
		df = self.copy()
		index = self.non_date_index
		index = index if len(index) > 1 else index[0]
		missing = False

		if 'date' in df.index.names:
			real_index = list(it.chain(index, ['date']))
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
		return DataObject(df), missing


class Portfolio(DataObject):
	"""
	Collection of commodity transactions.

	Attributes
	----------
	transactions : DataObject
		transactions.dtypes =
			shares        float64
			price         float64
			commission    float64

		transactions.index.names = [
			'owner_id',
			'account_id',
			'commodity_id',
			'type_id',
			'date']

		[type(i) for i in transactions.index[0]] = [
			<type 'numpy.int64'>,
			<type 'numpy.int64'>,
			<type 'numpy.int64'>,
			<type 'numpy.int64'>,
			<class 'pandas.tslib.Timestamp'>]

	shares : Series
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
	>>> Portfolio().to_dict()
	{'price': {(1, 1, 1, 1, <Timestamp: 2013-01-01 00:00:00>): 0}, \
'trade_commission': {(1, 1, 1, 1, <Timestamp: 2013-01-01 00:00:00>): 0}, \
'shares': {(1, 1, 1, 1, <Timestamp: 2013-01-01 00:00:00>): 0}}
	>>> from app.connection import Connection
	>>> conn = Connection('http://localhost:5000/api/')
	"""

	EMPTY_DF = pd.DataFrame({})
	EMPTY_S = pd.Series({})

	def __init__(
			self, data=None, keys=None, index=None, dividends=None,
			prices=None, rates=None, dtypes=None, currency_id=1, mapping=None):
		"""
		Class constructor.

		Parameters
		----------
		data : sequence of values or Pandas DataFrame, optional
		keys : sequence of column names, optional
		dividends : tuple of lists ([values], [keys]), optional
		prices : tuple of lists ([values], [keys]), optional
		rates : tuple of lists ([values], [keys]), optional
		index : sequence of the subset of column names, optional
			to use for category names

		dtypes : sequence of data types, optional
		currency_id : INT, optional
			id of the default currency
		mapping : tuple of lists ([values], [keys]), optional, optional
			commodity_id to commodity mapping

		See also
		--------
		from_prices : make constructor from prices
		"""

		INT = np.int
		FLT = np.float32
		DTIME = np.datetime64

		index = (
			index or [
				'owner_id', 'account_id', 'commodity_id', 'type_id', 'date'])

		keys = (keys or it.chain(index, ['shares', 'price', 'trade_commission']))

		try:
			empty = True if data.empty else False
			sequence = False
		except AttributeError:
			empty = False if data else True
			sequence = True

		if empty:
			super(Portfolio, self).__init__(data, None, list(keys), index)
		elif not sequence:
			super(Portfolio, self).__init__(data)
		else:
			dtypes = (dtypes or [INT, INT, INT, INT, DTIME, FLT, FLT, FLT])
			dtype = zip(keys, dtypes)
			super(Portfolio, self).__init__(data, dtype, index=index)

		mapping = (mapping or ([], []))
		dividends = (dividends or ([], []))
		prices = (prices or ([], []))
		rates = (rates or ([], []))

		div_df = DataObject(dividends[0], keys=dividends[1])

		self.transactions = self
		self.mapping = DataObject(mapping[0], keys=mapping[1], index=['id'])
		self.prices = DataObject(prices[0], keys=prices[1])
		self.rates = DataObject(rates[0], keys=rates[1])
		self.dividends = DataObject(div_df.join(self.prices, how='outer'))
		self.currency_id = currency_id
		self.missing = False

	@property
	def shares(self):
		"""Sum of shares for each commodity
		"""
		bad = ['price', 'type_id', 'trade_commission']
		index = set(self.index.names).difference(['type_id'])
		index = list(index) if len(index) > 1 else index[0]
		df = self.sorted.reset_index(level='type_id')
		keys = set([n for n in df]).intersection(bad)
		[df.pop(key) for key in keys]
		return DataObject(df.groupby(level=index).cumsum())

	@classmethod
	def from_prices(cls):
		"""
		Construct Portfolio from prices

		"""
		return Portfolio()

	def join_shares(self, other, common=None, shares=None):
		"""Joins shares to other

		Parameters
		----------
		other : DataObject
		common : sequence of strings, optional
			Columns/indices that are shared by both shares and other
		shares : DataObject, optional
			replacement for self.shares

		Examples
		--------
		>>> from datetime import datetime as dt
		>>> mp = Portfolio(DataObject())
		>>> keys=['date', 'commodity_id', 'price']
		>>> data = [(dt(2013, 1, 1), 1., 34.)]
		>>> df = DataObject(data, keys=keys)
		>>> mp.join_shares(df).to_records()[0]
		((1, 1, 1.0, <Timestamp: 2013-01-01 00:00:00>), 34.0, 0)
		>>> mp.join_shares(df).to_dict()
		{'price': {(1, 1, 1.0, <Timestamp: 2013-01-01 00:00:00>): 34.0}, \
'shares': {(1, 1, 1.0, <Timestamp: 2013-01-01 00:00:00>): 0}}
		"""
		try:
			empty = True if shares.empty else False
		except AttributeError:
			empty = False if shares else True

		shares = self.shares if empty else shares
		common = (common or ['date', 'commodity_id'])
		cols = set([c for c in other]).difference(common)
		y = it.chain(['date_x'], cols) if cols else ['date_x']
		x = ['date_y', 'shares']
		merged = other.merge_frame(shares, 'commodity_id')
		index = other.merge_index([shares])
		df = merged.join_merged(index, x, y)

		if len(df) > 1:
			df, self.missing = df.fill_missing(['shares'], ['shares'], cols, True)

		return df

	def extend_values(self, df):
		"""
		Extend values to obtain the same number of 	observances for each date
		(currently only works for a set of 2 dates)

		Parameters
		----------
		df : DataObject
			df.dtype = dtype('float64')
			df.name = 'close'

			df.index.names = [
				'currency_id',
				'commodity_id',
				'date']

			[type(i) for i in prices.index[0]] = [
				<type 'numpy.int64'>,
				<type 'numpy.int64'>,
				<class 'pandas.tslib.Timestamp'>]

		Returns
		-------
		DataObject

		Examples
		--------
		>>> from app import db
		"""
		new_index = df.non_date_index
		dfs = [df for df in df.sorted.split_frame('date')]

		# merge sep data frames together
		df_x, df_y = tuple(dfs)
		merged = df_x.merge_frame(df_y, new_index, ['date_x', 'date_y'])
		x = ['date_y', 'native_price_y', 'shares_y', 'div_shares_y']
		y = ['date_x', 'native_price_x', 'shares_x', 'div_shares_x']
		df = merged.join_merged(index, x, y)

		# combine *_x and *_y values
		df_x, df_y = df.split_frame('date')
		return df_x.concat_frames(df_y, index, x[1:], y[1:]).sorted

	def convert_prices(self, prices, rates, native=1):
		"""
		Convert prices to native currency

		Parameters
		----------
		prices : Series or DataFrame/DataObject
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

		rates : Series or DataFrame/DataObject
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

		Returns
		-------
		converted : DataObject
		"""

		if prices.any():
			# first rename rates column and index

			if not hasattr(rates, 'empty'):
				rates = pd.DataFrame({'rate': rates})

			if not hasattr(prices, 'empty'):
				prices = pd.DataFrame({'price': prices})

			rates.reset_index(inplace=True)
			rates.rename(
				columns={'commodity_id': 'currency_id', 'close': 'rate'},
				inplace=True)
			rates.set_index(['currency_id', 'date'], inplace=True)

			# now join prices and rates
			new_prices = prices.reset_index(level='commodity_id')
			converted = new_prices.join(rates, how='left')
			converted = converted.groupby(level='currency_id').fillna(
				method='pad')
		else:
			converted = prices.reset_index(level='commodity_id')
			converted['rate'] = 0

		# fill in native currency rates with value of 1
		if native in converted.groupby(level='currency_id').groups.keys():
			converted.rate[native].fillna(1, inplace=True)

		# calculate share closing prices in native currency
		converted = DataObject(converted.reset_index())
		converted.set_index(['commodity_id', 'date'], inplace=True)
		converted['native_price'] = converted.close * converted.rate
		del converted['currency_id'], converted['close'], converted['rate']
		return converted


class Metrics(Portfolio):
	"""
	Portfolio metrics.

	Attributes
	----------
	basis : DataObject
		cost basis (average)
		transactions.dtypes =
			shares        float64
			price         float64
			commission    float64

		transactions.index.names = [
			'owner_id',
			'account_id',
			'commodity_id',
			'type_id',
			'date']

		[type(i) for i in transactions.index[0]] = [
			<type 'numpy.int64'>,
			<type 'numpy.int64'>,
			<type 'numpy.int64'>,
			<type 'numpy.int64'>,
			<class 'pandas.tslib.Timestamp'>]

	irr : float
		internal rate of return

	sharpe : float
		sharpe ratio

	sortino : float
		sortino ratio

	var : float
		value at risk

	advancement : float
		unrealized gains from lows

	retracement : float
		unrealized losses from highs (drawdowns)

	"""

	def __init__(self, args=None, kwargs=None):
		"""
		Class constructor.

		Parameters
		----------
		args : sequence of arguments, optional
		kwargs : dict of keyword arguments, optional
		"""

		super(Metrics, self).__init__(*args, **kwargs)

	@property
	def native_prices(self):
		return self.convert_prices(self.prices, self.rates)

	@property
	def native_share_prices(self):
		return self.join_shares(self.native_prices)

	@property
	def share_prices(self):
		return self.join_shares(self.dividends)

	@property
	def reinvestments(self):
		df = self.share_prices

		if not df.empty:
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
			reinvestments = DataObject()

		# need to return union of reinvestments with transactions
		return reinvestments

	@property
	def basis(self):
# 		self.transactions
# 		self.reinvestments
		pass
