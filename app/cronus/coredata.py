# -*- coding: utf-8 -*-
"""
	app.cronus.coredata
	~~~~~~~~~~~~~~

	Provides methods for creating and manipulating DataObject and Portfolio
	data
"""

import pandas as pd
import numpy as np
import itertools as it

from pprint import pprint
from dateutil.parser import parse
from datetime import datetime as dt, date as d


def char_range(x, letter='a'):
	"""Generates the characters from letter to (letter + x letters),
	inclusive."""
	for c in xrange(ord(letter), ord(letter) + x):
		yield chr(c)


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
		data : a sequence of sets or dicts, a Pandas DataFrame,
			a Series, or a dict of Series, optional

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
		>>> data = [(6, 'APL')]
		>>> DataObject(data).to_dict()
		{0: {0: 6}, 1: {0: 'APL'}}
		>>> keys=['id', 'symbol']
		>>> DataObject(data, keys=keys).to_dict()
		{'symbol': {0: 'APL'}, 'id': {0: 6}}
		>>> DataObject([{0: 6, 1: 'APL'}]).to_dict()
		{0: {0: 6}, 1: {0: 'APL'}}
		>>> import numpy as np
		>>> data = [{'id': 6, 'symbol': 'APL'}]
		>>> dtype = [('id', np.int), ('symbol', 'a5')]
		>>> DataObject(data, dtype, index=['id']).to_dict()
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

		# if empty:
		#	default_df = pd.DataFrame()
		if stype.startswith('f'):
			default_df = data
		elif stype.startswith('ser'):
			default_df = pd.DataFrame({data.name: data})
		elif (stype.startswith('d') or stype.startswith('seq')):
			if keys:
				default_df = pd.DataFrame(data, columns=keys)
			else:
				default_df = pd.DataFrame(data)

		keys = (keys or list(default_df))
		has_index = default_df.index.names[0]

		if not (index or has_index):
			index = [
				k for k in keys if (
					str(k).endswith('_id') or str(k).startswith('date'))]

		if index and not keys:
			keys = index
		elif not (index or has_index) and dtype:
			index = [d[0] for d in dtype if hasattr(d[1], 'year')]
		elif not index:
			index = []

		if empty:
			data = self.fill_data(set(keys).difference(index), index)
			df = pd.DataFrame(data, columns=keys)
		else:
			df = default_df

		if not (index or has_index) and keys:
			try:
				values = [df.ix[0][p] for p in keys]
				zipped = zip(keys, values)
				index = [z[0] for z in zipped if hasattr(z[1], 'year')]
			except KeyError:
				pass
			except IndexError:
				pass

		if 'date' in df:
			is_date = hasattr(type(df.date.tolist()[0]), 'year')

			try:
				df.date = df.date if is_date else df.date.apply(parse)
			except AttributeError:
				df.date = df.date

		if index and not has_index:
			index = [i for i in index if i in df]
			df.set_index(index, inplace=True) if index else ''

		super(DataObject, self).__init__(df)

	@property
	def non_date_index(self):
		return list(set(self.index.names).difference(['date']))

	@property
	def sorted(self):
#		index = self.index.names
#		if (len(self) > 1 and len(index) > 1):
#			for level in reversed(index):
#				df = self.sortlevel(level=level)
#
#			df = DataObject(df)
#
#		elif len(self) > 1:
#			df = DataObject(self.sort_index())
#		else:
#			df = self

		return DataObject(self.sort())
		# return self.sort()

	@property
	def unindexed(self):
		return self.reset_index() if self.index.names[0] else self

	@property
	def reindexed(self):
		"""
		Put date index last
		"""

		real_index = self.index.names
		index = self.non_date_index
		df = self.df_reindex(index) if index[0] else self

		if (index and 'date' in real_index):
			df.set_index(['date'], inplace=True, append=True)

		return DataObject(df).sorted

	def df_reindex(self, index):
		"""
		Set index to index
		"""
		return self.unindexed.set_index(index) if index else self

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
		>>> df1 = DataObject([{'1_id': 6, 'sym': 'APL'}])
		>>> df2 = DataObject([{'2_id': 2, 'sym': 'IBM'}])
		>>> df1.merge_index(df2)
		['1_id', '2_id']
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
		>>> df1, df2 = df.split_frame(0)
		>>> df1.to_dict()
		{0: {0: 6}, 1: {0: 'APL'}}
		>>> df2.to_dict()
		{0: {1: 2}, 1: {1: 'IBM'}}
		"""
		df = self.df_reindex(index)
		g = [DataObject(g[1]) for g in df.groupby(level=0)]
		return tuple(g)

	def merge_frame(self, y, on=None, toffill=None, reindex=False):
		"""
		Merge a DataObject with another a DataFrame/DataObject

		Parameters
		----------
		y : DataObject or DataFrame
		on : sequence of strings, optional
			the columns that appear in both DataObjects
		toffill : sequence of strings, optional
			the merged columns to fill in missing values
		reindex : boolean, default False
			replace index in the merged DataObject
		Returns
		-------
		DataObject

		Examples
		--------
		>>> df1 = DataObject([{'_id': 6, 'sym': 'APL'}])
		>>> df2 = DataObject([{'_id': 2, 'sym': 'IBM'}])
		>>> df1.to_dict()
		{'sym': {6: 'APL'}}
		>>> df2.to_dict()
		{'sym': {2: 'IBM'}}
		>>> df1.merge_frame(df2).to_dict()
		{'sym_y': {2.0: 'IBM', 6.0: nan}, 'sym_x': {2.0: nan, 6.0: 'APL'}}
		"""
		# reset index so I can merge
		#
		# this will auto fill in values for all combinations of
		# 'owner_id' and 'account_id' into merged DataFrame
		# and 'currency_id' into shares DataFrame
		# returns two sets of date fields (x and y)
		if self.empty:
			return y
		elif y.empty:
			return self
		else:
			on = (on or self.non_date_index)
			x = self.unindexed
			y = DataObject(y).unindexed
			toffill = (toffill or [])
			merged = x.merge(y, on=on, how='outer')
			[merged[f].fillna(method='ffill', inplace=True) for f in toffill]
			new = merged.set_index(on) if reindex else merged
			return DataObject(new)

	def concat_frames(
		self, y, index=None, delete_x=None, delete_y=None, ignore_index=False):
		"""
		Concatenate a DataObject onto a DataFrame/DataObject
		Works like pandas.concat but can operate on objects with indices and
		overlapping and/or non-overlapping rows

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
		>>> df1.to_dict()
		{0: {0: 1}, 1: {0: 'a'}}
		>>> df2.to_dict()
		{0: {0: 2}, 1: {0: 'b'}}
		>>> df1.concat_frames(df2, ignore_index=True).to_dict()
		{0: {0: 1, 1: 2}, 1: {0: 'a', 1: 'b'}}
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
		df = DataObject(pd.concat([x, y], ignore_index=ignore_index))
		return df.df_reindex(index) if index else df.sorted

	def join_frame(self, other):
		"""Joins a df to other

		Parameters
		----------
		other : DataObject

		Examples
		--------
		>>> from datetime import datetime as dt
		>>> keys=['date', 'commodity_id', 'price']
		>>> data = [(dt(2013, 1, 1), 1., 34.)]
		>>> df = DataObject(data, keys=keys)
		>>> df.to_dict()
		{'price': {(<Timestamp: 2013-01-01 00:00:00>, 1.0): 34.0}}
		>>> df.join_frame(DataObject()).to_dict()
		{'price': {(<Timestamp: 2013-01-01 00:00:00>, 1.0): 34.0}}
		>>> df.join_frame(df).to_dict()
		{'price_y': {(<Timestamp: 2013-01-01 00:00:00>, 1.0): 34.0}, \
'price_x': {(<Timestamp: 2013-01-01 00:00:00>, 1.0): 34.0}}
		"""
		if self.empty:
			return other
		elif other.empty:
			return self
		else:
			common_index = set(self.index.names).intersection(other.index.names)
			common_nd_index = set(self.non_date_index).intersection(
				other.non_date_index)
			xnames = set(self).union(self.index.names)
			ynames = set(other).union(other.index.names)
			common = xnames.intersection(ynames).difference(common_nd_index)
			xcols = xnames.difference(common_nd_index.union(common))
			ycols = ynames.difference(common_nd_index.union(common))
			x = set('%s_y' % c for c in common).union(ycols)
			y = set('%s_x' % c for c in common).union(xcols)
			merged = self.merge_frame(other, list(common_nd_index))
			return merged.join_merged(list(common_index), x, y)

	def join_merged(self, index=None, delete_x=None, delete_y=None):
		"""
		Join a merged dataframe to itself

		Parameters
		----------
		index : sequence of strings, optional
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
		if self.empty:
			return self
		else:
			delete_x = (delete_x or [])
			delete_y = (delete_y or [])

			if index:
				df = self.reset_index()
			else:
				combo = set(delete_x).union(delete_y).intersection(self.index.names)
				df = self.reset_index(level=list(combo)) if combo else self.copy()

			df_x, df_y = df, df.copy()

			# remove the common fields between the 2 data frames
			for f in delete_x:
				if f in df_x:
					del df_x[f]

			for f in delete_y:
				if f in df_y:
					del df_y[f]

			# set index so I can now join the data frames since they have
			# different fields
			df_x = df_x.rename(columns={'date_x': 'date'})
			df_y = df_y.rename(columns={'date_y': 'date'})

			if not index:
				df_x, df_y = (df_x, df_y)
			else:
				in_x = [x for x in index if x in df_x]
				in_y = [y for y in index if y in df_y]
				df_x = df_x.set_index(in_x) if in_x else df_x
				df_y = df_y.set_index(in_y) if in_y else df_y

			df = DataObject(df_x.join(df_y, how='outer'))

			if len(df) > 1:
				interpolate = ['close'] if 'close' in df else None
				ffill = ['shares'] if 'shares' in df else None
				df, self.missing = df.fill_missing(ffill, None, interpolate, True)

			return df

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
			The index(ices) to forward fill

		tobfill : sequence of strings
			The index(ices) to back-fill

		tointerpolate : sequence of strings
			The index(ices) to interpolate

		dedupe : sequence of strings

		Returns
		-------
		DataObject
		missing : boolean
			True if interpolate was unable to fill in all values

		Examples
		--------
		>>> data = [(1, 2, 3, 4), (1, 2, 3)]
		>>> keys = ['a_id', 'b_id', 'c', 'd']
		>>> df = DataObject(data, keys=keys)
		>>> df.to_dict()
		{'c': {(1, 2): 3}, 'd': {(1, 2): nan}}
		>>> df, missing = df.fill_missing()
		>>> df.to_dict()
		{'c': {(2, 1): 3}, 'd': {(2, 1): 4.0}}
		>>> missing
		False
		"""
		df = self.reindexed
		index = self.non_date_index
#		index = index if len(index) > 1 else index[0]
		missing = False
		toffill = (toffill or [])
		tobfill = (tobfill or [])
		tointerpolate = (tointerpolate or [])

		if 'date' in df.index.names:
			real_index = list(it.chain(index, ['date']))
			df = df.df_reindex(real_index)

		if not (toffill or tobfill or tointerpolate):
			toffill = list(df)

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
			shares		  float64
			price		  float64
			commission	  float64

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
	{}
	"""

	EMPTY_DF = pd.DataFrame({})
	EMPTY_S = pd.Series({})

	def __init__(
			self, data=None, dividends=None, prices=None, rates=None,
			mapping=None, currency_id=1):
		"""
		Class constructor.

		Parameters
		----------
		data : list of dicts, optional
		dividends : list of dicts, optional
		prices : list of dicts, optional
		rates : list of dicts, optional
		currency_id : INT, optional
			id of the default currency
		mapping : list of dicts, optional, optional
			commodity_id to commodity mapping
		"""
		index = ['owner_id', 'account_id', 'commodity_id', 'type_id', 'date']
		empty = False if data else True
		div_df = DataObject(dividends).reset_index(level='type_id', drop=True)
		super(Portfolio, self).__init__(data, index=index)

		self.transactions = self.sorted

		if mapping:
			self.mapping = DataObject(mapping, index=['id'])[['symbol', 'name']]
		else:
			self.mapping = DataObject([{'symbol': '', 'name': ''}])

		self.prices = DataObject(prices)
		self.rates = DataObject(rates).reset_index(level='currency_id', drop=True)

		if (div_df.empty and self.prices.empty):
			self.dividends = DataObject()
		else:
			self.dividends = DataObject(div_df).join_frame(self.prices)

		self.currency_id = currency_id
		self.missing = False

	@property
	def shares(self):
		"""Sum of shares for each commodity
		"""
		df = self.transactions.reset_index(level='type_id')
		index = DataObject(df).non_date_index
		return DataObject({'shares': df.shares.groupby(level=index).cumsum()})

	def extend_values(self, df):
		"""
		Extend values to obtain the same number of	observances for each date
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
		return df_x.concat_frames(df_y, index, x[1:], y[1:])

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
		try:
			empty = True if prices.empty else False
		except AttributeError:
			empty = False if prices.any() else True

		if not empty:
			if not hasattr(rates, 'empty'):
				rates = pd.DataFrame({'rate': rates})

			if not hasattr(prices, 'empty'):
				prices = pd.DataFrame({'price': prices})

			# first rename rates column and set index
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
		converted['native'] = False
		if native in converted.groupby(level='currency_id').groups.keys():
			converted.rate[native].fillna(1, inplace=True)
			converted.native[native] = True

		# filling missing rates
		converted = DataObject(converted)
		converted['rated'] = converted.rate.fillna(0).apply(
			lambda x: True if x else False)

		# remove dupes
		index = ['commodity_id', 'date', 'native', 'rated']
		compacted = converted.df_reindex(index).groupby(
			level=['commodity_id', 'date']).last()

		# calculate share closing prices in native currency
		converted = converted.df_reindex(['commodity_id', 'date'])
		return DataObject({'native_price': converted.close * converted.rate})
