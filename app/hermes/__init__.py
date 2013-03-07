# -*- coding: utf-8 -*-
"""
	app.hermes
	~~~~~~~~~~~~~~

	Provides methods for collecting and manipulating Portfolio price and event
	data
"""

import itertools as it

from pprint import pprint
from urllib2 import HTTPError
from datetime import datetime as dt, date as d, timedelta
from dateutil.parser import parse
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
	def price_keys(self):
		return [('commodity_id', 'currency_id', 'close', 'date')]

	@property
	def event_keys(self):
		return [('type_id', 'commodity_id', 'currency_id', 'value', 'date')]

	@property
	def currencies(self):
		objects = self.commodity_list(2)
		symbols = []
		[[symbols.append(c['symbol']) for c in o['commodities']] for o in objects]
		return symbols

	@property
	def securities(self):
		objects = self.commodity_list()
		symbols = []
		[[symbols.append(c['symbol']) for c in o['commodities']] for o in objects]
		return symbols

	def latest_price_dates(self, symbols):
		objects = self.commodity_info(symbols)
		list = []

		for o in objects:
			try:
				list.append((
					o['symbol'],
					max(c['date'] for c in o['commodity_prices'])))
			except ValueError:
				list.append((o['symbol'], None))

		return [dict(list).get(s) for s in symbols]

	def group_ids(self, symbols):
		# TODO: return 'N/A' if symbol doesn't exist
		objects = self.commodity_info(symbols)
		list = [(o['symbol'], o['type']['group_id']) for o in objects]
		return [dict(list).get(s) for s in symbols]

	def get_prices(self, symbols=None, start=None, end=None, extra=None):
		getcontext().prec = 6
		symbols = (symbols or self.securities)
		group_ids = self.group_ids(symbols)
		ids = self.ids_from_symbols(symbols)
		switch = {1: 'yahoo', 2: 'fred'}
		sources = [switch.get(id) for id in group_ids]
		dataset, raw, data, res = [], [], [], []
		end = parse(end).date() if end else d.today()
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

		if start:
			num = len(symbols)
			date = parse(start).date()
			starts = it.repeat(date, num) if num > 1 else [date]
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

		for s in zip(dataset, sources, starts):
			if s[0]:
				try:
					data.append(
						DataReader(
							s[0], s[1], s[2], end, dividends=divs,
							splits=splits))
				except HTTPError:
					data.append(None)
			else:
				data.append(None)

		for s in zip(group_ids, data, dataset):
			try:
				empty = True if s[1].empty else False
			except AttributeError:
				empty = False if s[1] else True

			if (s[0] == 1 and not (empty or divs or splits)):
				raw.append(s[1].Close.to_dict().items())
			elif (not empty and s[2] and s[0] == 1 and divs):
				raw.append(s[1].Dividends.to_dict().items())
			elif (not empty and s[0] == 1 and splits):
				raw.append(s[1].SPLIT.to_dict().items())
			elif not empty:
				raw.append(s[1][s[2]].to_dict().items())
			else:
				raw.append(None)

		for s in zip(ids, raw, symbols, starts):
			if (s[1] and not (divs or splits)):
				res.extend([(
					s[0], 1, Decimal(r[1]).quantize(Decimal('.001')), r[0])
					for r in s[1]])
			elif (s[1] and divs):
				res.extend([(
					1, s[0], 1, Decimal(r[1]).quantize(Decimal('.001')), r[0])
					for r in s[1]])
			elif (s[1] and splits):
				ratio = s[1][0][1].split(':')
				value = Decimal(int(ratio[0]) / int(ratio[1]))
				res.extend([(3, s[0], 1, value, r[0]) for r in s[1]])
			else:
				if extra:
					verb = 'splits' if splits else 'dividends'
				else:
					verb = 'prices'

				print(
					'No %s found for %s from %s to %s' % (verb, s[2], s[3], end))

		return [list(res)]
