# -*- coding: utf-8 -*-
"""
	app.hermes
	~~~~~~~~~~~~~~

	Provides methods for collecting and manipulating Portfolio price and event
	data
"""

import itertools as it
import dateutil.parser as parser

from pprint import pprint
from urllib2 import HTTPError
from datetime import datetime as dt, date as d, timedelta
from pandas.io.data import DataReader
from app.connection import Connection
from decimal import Decimal, getcontext


def parse(date):
	return date if hasattr(date, 'year') else parser.parse(date).date()


class Historical(Connection):
	def __init__(self, *args, **kwargs):
		"""
		Class constructor.

		Parameters
		----------
		args : sequence of arguments, optional
		kwargs : dict of keyword arguments, optional
		"""
		getcontext().prec = 6
		super(Historical, self).__init__(*args, **kwargs)

	@property
	def currencies(self):
		objects = self.list_commodities(2)
		symbols = []

		[
			[symbols.append(c['symbol']) for c in o['commodities']]
			for o in objects]

		return symbols

	@property
	def securities(self):
		objects = self.list_commodities()
		symbols = []

		[
			[symbols.append(c['symbol']) for c in o['commodities']]
			for o in objects]

		return symbols

	def earliest_price_dates(self, symbols, extra=None):
		#TODO: Check dividend and split dates
		objects = self.get_commodity_info(symbols)
		list = []

		for o in objects:
			try:
				list.append((
					o['symbol'],
					min(c['date'] for c in o['commodity_prices'])))
			except ValueError:
				list.append((o['symbol'], None))

		return [dict(list).get(s) for s in symbols]

	def latest_price_dates(self, symbols, extra=None):
		#TODO: Check dividend and split dates
		objects = self.get_commodity_info(symbols)
		list = []

		for o in objects:
			try:
				list.append((
					o['symbol'],
					max(c['date'] for c in o['commodity_prices'])))
			except ValueError:
				list.append((o['symbol'], None))

		return [dict(list).get(s) for s in symbols]

	def holding_ids(self, symbols):
		symbols = [symbols] if hasattr(symbols, 'isalnum') else symbols
		# TODO: return 'N/A' if symbol doesn't exist
		objects = self.get_commodity_info(symbols)
		list = [(o['symbol'], o['holdings'][0]['id']) for o in objects]
		return [dict(list).get(s) for s in symbols]

	def group_ids(self, symbols):
		symbols = [symbols] if hasattr(symbols, 'isalnum') else symbols
		# TODO: return 'N/A' if symbol doesn't exist
		objects = self.get_commodity_info(symbols)
		list = [(o['symbol'], o['type']['group_id']) for o in objects]
		return [dict(list).get(s) for s in symbols]

	def get_symbol_data(self, symbols):
		ids = self.commodity_ids(symbols)
		group_ids = self.group_ids(symbols)
		switch = {1: 'yahoo', 2: 'fred'}
		sources = [switch.get(id) for id in group_ids]
		return ids, group_ids, sources

	def get_prices(self, symbols, starts=None, ends=None, extra=None):
		ids, group_ids, sources = self.get_symbol_data(symbols)
		dataset, data, prices = [], [], []
		divs = True if (extra and extra.startswith('d')) else False
		splits = True if (extra and extra.startswith('s')) else False

		for s in zip(group_ids, symbols):
			if s[0] == 1:
				dataset.append(s[1])
			elif s[0] == 2:
				switch = {'EUR': 'DEXUSEU', 'GBP': 'DEXUSUK', 'CAD': 'DEXCAUS'}
				dataset.append(switch.get(s[1]))
			else:
				dataset.append(None)

		for s in zip(dataset, sources, starts, ends):
			if s[0]:
				try:
					data.append(
						DataReader(
							s[0], s[1], s[2], s[3], dividends=divs,
							splits=splits))
				except HTTPError:
					data.append(None)
				except IOError:
					data.append(None)
			else:
				data.append(None)

		for s in zip(group_ids, data, dataset):
			try:
				empty = True if s[1].empty else False
			except AttributeError:
				empty = False if s[1] else True

			if (s[0] == 1 and not (empty or divs or splits)):
				prices.append(s[1].Close.to_dict().items())
			elif (not empty and s[2] and s[0] == 1 and divs):
				prices.append(s[1].Dividends.to_dict().items())
			elif (not empty and s[0] == 1 and splits):
				prices.append(s[1].SPLIT.to_dict().items())
			elif not empty:
				prices.append(s[1][s[2]].to_dict().items())
			else:
				prices.append(None)

		return prices

	def get_first_price(
			self, symbols=None, date=None, extra=None, forward=True,
			limit=7):
		symbols = (symbols or self.securities)
		num = len(symbols)
		ids = self.holding_ids(symbols)
		date = parse(date) if date else d.today() - timedelta(days=limit)
		divs = True if (extra and extra.startswith('d')) else False
		splits = True if (extra and extra.startswith('s')) else False
		table = 'event' if extra else 'price'
		res = []

		if forward:
			start = date
			end = date + timedelta(days=limit)
		else:
			start = date - timedelta(days=limit)
			end = date

		starts = list(it.repeat(start, num)) if num > 1 else [start]
		ends = list(it.repeat(end, num)) if num > 1 else [end]

		prices = self.get_prices(symbols, starts, ends)

		for s in zip(ids, prices):
			id, data = s[0], s[1]

			if not data:
				continue

			if forward:
				data.sort(key=lambda x: x[0])
			else:
				data.sort(key=lambda x: x[0], reverse=True)

			res.extend([(
				True, data[0][0], id,
				Decimal(data[0][1]).quantize(Decimal('.001')), 1, 1)])

		return {'transaction': res}

	def get_price_list(self, symbols=None, start=None, end=None, extra=None):
		symbols = (symbols or self.securities)
		num = len(symbols)
		ids = self.commodity_ids(symbols)
		date = parse(end) if end else d.today()
		ends = list(it.repeat(date, num)) if num > 1 else [date]
		divs = True if (extra and extra.startswith('d')) else False
		splits = True if (extra and extra.startswith('s')) else False
		table = 'event' if extra else 'price'
		res = []

		if start:
			date = parse(start)
			starts = list(it.repeat(date, num)) if num > 1 else [date]
		else:
			last_dates = self.latest_price_dates(symbols)
			starts = []

			for ts in last_dates:
				if ts:
					starts.append(
					dt.strptime(ts, "%Y-%m-%dT%H:%M:%S").date()
					+ timedelta(days=1))
				else:
					starts.append(d.today() - timedelta(days=30))

		prices = self.get_prices(symbols, starts, ends, extra)

		for s in zip(ids, prices, symbols, starts, ends):
			id, price = s[0], s[1]
			if (price and not extra):
				res.extend([(
					Decimal(r[1]).quantize(Decimal('.001')), id, 1, r[0])
					for r in price])
			elif (price and divs):
				res.extend([(
					id, 1, r[0], 1, Decimal(r[1]).quantize(Decimal('.001')))
					for r in price])
			elif (price and splits):
				ratio = price[0][1].split(':')
				value = Decimal(int(ratio[0]) / int(ratio[1]))
				res.extend([(id, 1, r[0], 3, value) for r in price])
			else:
				if extra:
					verb = 'splits' if splits else 'dividends'
				else:
					verb = 'prices'

				print(
					'No %s found for %s from %s to %s' % (
					verb, s[2], s[3], s[4]))

		return {table: res}
