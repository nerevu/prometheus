# -*- coding: utf-8 -*-
"""
	app.hermes
	~~~~~~~~~~~~~~

	Provides methods for collecting and manipulating Portfolio price and event
	data
"""

from datetime import datetime as dt, date as d, timedelta
from pandas.io.data import DataReader
from app.connection import Connection
from decimal import Decimal, getcontext


class Historical(Connection):
	def __init__(self, *args, **kwargs):
		"""
		Class constructor.

		Parameters
		----------
		args : sequence of arguments, optional
		kwargs : dict of keyword arguments, optional
		"""

		super(Historical, self).__init__(*args, **kwargs)

	@property
	def symbols(self):
		table, filter = self.securities
		objects = self.get(table, filter)
		symbols = []
		[[symbols.append(c['symbol']) for c in o['commodities']] for o in objects]
		return symbols

	def latest_price_date(self, symbols=None):
		symbols = (symbols or self.symbols)
		table, filter = self.commodities(symbols)
		objects = self.get(table, filter)
		return [max(c['date'] for c in o['commodity_prices']) for o in objects]

	def get_prices(self, symbol, start=None, end=None):
		getcontext().prec = 6

		start = (start or d.today() - timedelta(days=30))
		end = (end or d.today())
		data = DataReader(symbol, "yahoo", start, end)
		raw = data.Close.to_dict().items()

		return [
			(
				self.id_from_symbol(symbol), 1,
				Decimal(r[1]).quantize(Decimal('.001')), r[0])
			for r in raw]
