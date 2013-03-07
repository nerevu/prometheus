# -*- coding: utf-8 -*-
"""
	app.cronus.sources
	~~~~~~~~~~~~~~

	Provides methods for importing portfolio data from multiple sources
"""

import csv

from app.connection import Connection


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
		<app.cronus.sources.DataSource object at 0x...>
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
		<app.cronus.sources.CSV object at 0x...>
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
		<app.cronus.sources.CSV object at 0x...>
		"""
		super(GnuCash, self).__init__(site, native, display)
