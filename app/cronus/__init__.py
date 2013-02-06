# -*- coding: utf-8 -*-
"""
	app.cronus
	~~~~~~~~~~~~~~

	Provides libraries for importing portfolio data from multiple sources
"""

import csv

from app.connection import Connection


class DataSource(Connection):
	"""
	Generic data source.
	"""
	def __init__(self, site, native=1, display=False):
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
	content : list of dicts
		csv contents
	"""
	def __init__(
			self, file, site, native=1, display=False, delimiter=',',
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
	def content(self):
		transactions = []
		table = 'transaction'
		keys = [
			'holding_id', 'type_id', 'shares', 'price', 'date',
			'commissionable']

		with open(file, 'rb') as csvfile:
			spamreader = csv.reader(
				csvfile, delimiter=self.delimiter, quotechar=self.quotechar)

			[transactions.append(row) for row in spamreader]

		return self.process(transactions, table, keys)


class GnuCash(DataSource):
	def __init__(self, file, site, native=1, display=False):
		super(GnuCash, self).__init__(site, native, display)
