# -*- coding: utf-8 -*-
"""
	app.cronus
	~~~~~~~~~~~~~~

	Provides libraries for importing portfolio data from multiple sources
"""

import csv

from app.connection import Connection


class DataSource(Connection):
	def __init__(self, site, native=1, display=False):
		super(DataSource, self).__init__(site, native, display)


class CSV(DataSource):
	def __init__(
			self, file, site, native=1, display=False, delimiter=',',
			quotechar='"'):
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
