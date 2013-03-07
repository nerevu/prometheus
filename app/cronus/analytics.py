# -*- coding: utf-8 -*-
"""
	app.cronus.analytics
	~~~~~~~~~~~~~~

	Provides methods for analyzing Portfolio objects
"""

from .coredata import Portfolio, DataObject


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

	def __init__(self, *args, **kwargs):
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
		return self.convert_prices(self.prices, self.rates, self.currency_id)

	@property
	def shares_w_reinv(self):
		df = self.join_shares(self.dividends)

		if not df.empty:
			new_index = ['owner_id', 'account_id', 'commodity_id', 'date']
			df.reset_index(inplace=True)
			df = DataObject(df.set_index(new_index).sort())
			index = df.non_date_index

			# fill blank dividends with 0
			df.value.fillna(0, inplace=True)

			# calculate number of shares purchased
			df['dividend_received'] = df['value'] * df['shares']
			df['purchases'] = df['dividend_received'] / df['close']
			df['div_shares'] = df['purchases'].groupby(level=index).cumsum()
		else:
			df['div_shares'] = 0

		df['tot_shares'] = df['div_shares'] + df['shares']

		return DataObject({'shares': df.tot_shares})

	@property
	def basis(self):
		df = self.transactions
		index = df.non_date_index
		df['basis'] = df['shares'] * df['price'] + df['trade_commission']
		return DataObject({'basis': df.basis.groupby(level=index).sum()})

	@property
	def share_basis(self):
		df = self.transactions
		index = df.non_date_index
		right = DataObject({'shares': df.shares.groupby(level=index).sum()})
		merged = self.basis.merge_frame(right, reindex=True)
		return DataObject({'share_basis': merged.basis / merged.shares})

	@property
	def advancement(self):
		"""
		unrealized gains from lows
		"""
		pass

	@property
	def retracement(self):
		"""
		unrealized losses from highs (drawdowns)
		"""
		pass

	@property
	def irr(self):
		"""
		internal rate of return
		"""
		pass

	@property
	def sharpe(self):
		"""
		sharpe ratio
		"""
		pass

	@property
	def var(self):
		"""
		value at risk
		"""
		pass

	@property
	def sortino(self):
		"""
		sortino ratio
		"""
		pass
