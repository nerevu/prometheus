# -*- coding: utf-8 -*-
"""
	app.apollo
	~~~~~~~~~~~~~~

	Provides application manipulation functions for input into visualization
	libraries
"""

from app.cronus import Metrics, DataObject


class Worth(Metrics):
	"""
	Description.

	Attributes
	----------
	"""

	def __init__(self, args=None, kwargs=None):
		"""
		Class constructor.

		Parameters
		----------
		args : sequence of arguments, optional
		kwargs : dict of keyword arguments, optional
		"""

		super(Worth, self).__init__(args, kwargs)

	@property
	def share_value(self):
		# adds transaction price to prices df if needed
		df = self.join_shares(self.native_prices, shares=self.shares_w_reinv)
		df['value'] = df.native_price * df.shares

		# TODO: sum by dates, not datetimes
		df = df.groupby(level=df.index.names).sum()
		df_dict = {'shares': df.shares, 'value': df.value}
		return DataObject(df_dict)

	def calc_worth(self, how='stock', mode='latest', convert=False):
		"""
		Calculate portfolio worth for a specific date

		Parameters
		----------
		how : {'own', 'act', 'stock', 'own_stock', 'act_stock', 'own_act'}
			How to group the values:
			* own: by owner
			* act: by account
			* stock: by stock
			* own_stock: by owner and stock
			* act_stock: by account and stock
			* own_act: by owner and account

			default 'stock'

		mode : {'latest', 'uniform'}
			How to select the date on which to calculate the value
			* latest: view most recent data irrespective of incomplete entries
			* uniform: view most recent data that contains values for all
				entries

		convert : boolean, default False
			convert commodity ids to symbols

		"""
		# group transactions by date
#		max_date = max([i[3] for i in df.index])

		# make sep data frames for each date
		# TODO: account for multiple owners and/or accounts
		df = self.share_value
		old_index = df.non_date_index
		dfs = [df for df in df.sorted.split_frame('date')]
		date_list = [(df.index[0], len(df)) for df in dfs]
		by_date = dict(date_list)
		max_entries = max(by_date.values())
		items = by_date.items()
		df.reset_index(inplace=True)

		# select grouping
		switch = {
			'own': ['owner_id'],
			'act': ['account_id'],
			'stock': ['commodity_id'],
			'own_stock': ['owner_id', 'commodity_id'],
			'act_stock': ['account_id', 'commodity_id'],
			'own_act': ['owner_id', 'account_id']}

		new_index = ['date'] + switch.get(how.lower())
		to_delete = set(old_index).difference(new_index)
		df.set_index(new_index, inplace=True)
		df = df.sorted

		for f in to_delete:
			del df[f]

		# select mode
		switch = {
			'latest': max(by_date.keys()),
			'uniform': max([d[0] for d in items if d[1] == max_entries])}

		the_date = switch.get(mode.lower())
		selected = df.groupby(level='date').get_group(the_date)
		return selected.reset_index('date').to_dict()['value']

	def convert_worth(self, worth):
		"""
		Converts Portfolio values into a more parseable format

		Parameters
		----------
		worth : dict {id: value}

		Returns
		-------
		data : sequence of ('symbol', value)
		"""

		if worth.values() and not self.mapping.empty:
			symbols = [self.mapping.symbol.get(x, 'N/A') for x in worth.keys()]
			totals = ['%.2f' % x for x in worth.values()]
			data = zip(symbols, totals)
		elif worth:
			data = worth.items()
		else:
			data = [('N/A', 0)]

		return data
