from pprint import pprint
from json import dumps as dmp
from requests import post as p

__HDR__ = {'content-type': 'application/json'}

__TABLES__ = (
	'exchange',
	'data_source',
	'commodity_group',
	'commodity_type',
	'commodity',
	'event_type',
	'event',
	'price',
	'person',
	'company',
	'account_type',
	'account',
	'holding',
	'trxn_type',
	'transaction')

__KEYS__ = [
	# '[(' is needed so dict doesn't iterate over each character
	('symbol', 'name'),  # exchange
	[('name')],  # data_source
	[('name')],  # commodity_group
	('name', 'group_id'),  # commodity_type
	('symbol', 'name', 'type_id', 'data_source_id', 'exchange_id'),  # commodity
	[('name')],  # event_type
	('type_id', 'commodity_id', 'currency_id', 'value', 'date'),  # event
	('commodity_id', 'currency_id', 'close', 'date'),  # price
	('currency_id', 'first_name', 'last_name', 'email'),  # person
	('name', 'website'),  # company
	[('name')],  # account_type
	('type_id', 'company_id', 'currency_id', 'owner_id', 'name'),  # account
	('commodity_id', 'account_id'),  # holding
	[('name')],  # trxn_type
	(
		'holding_id', 'type_id', 'shares', 'price', 'date',
		'commissionable')] 	# transaction


def post(content, site):
	for piece in content:
		table = piece['table']
		data = piece['data']

		for d in data:
			r = p('%s%s' % (site, table), data=dmp(d), headers=__HDR__)

			if r.status_code != 201:
				raise AttributeError(
					'Response: %s. Request %s with content '
					'%s sent to %s' % (
						r.status_code, r.request.data, r._content, r.url))

	return r


def process(post_values):
	combo = zip(__KEYS__, post_values)
	table_data = [
		[dict(zip(list[0], values)) for values in list[1]] for list in combo]

	content_keys = ('table', 'data')
	content_values = zip(__TABLES__, table_data)
	return [dict(zip(content_keys, values)) for values in content_values]


def get_init_values():
	values = [
		[
			('NYSE', 'New York Stock Exchange'), ('NASDAQ', 'NASDAQ'),
			('OTC', 'Over the counter'), ('N/A', 'Currency')],  # exchange
		[[('Yahoo')], [('Google')], [('XE')]],  # data_source
		[[('Security')], [('Currency')], [('Other')]],  # commodity_group
		[
			('Stock', 1), ('Bond', 1), ('Mutual Fund', 1), ('ETF', 1),
			('Currency', 2), ('Descriptor', 3)],  # commodity_type
		[
			('USD', 'US Dollar', 5, 3, 4),
			('EUR', 'Euro', 5, 3, 4),
			('GBP', 'Pound Sterling', 5, 3, 4),
			('TZS', 'Tanzanian Shilling', 5, 3, 4),
			('Multiple', 'Multiple', 6, 3, 4),
			('APL', 'Apple', 1, 1, 1),
			('Text', 'Text', 6, 3, 4)],  # commodity
		[
			[('Dividend')], [('Special Dividend')], [('Stock Split')],
			[('Name Change')], [('Ticker Change')]],  # event_type
		[],  # event
		[
			(2, 1, 1.2, '1/1/12'),
			(3, 1, 1.8, '1/1/12'),
			(4, 1, 1.0 / 1580.0, '1/1/12'),
			(6, 1, 300, '1/1/12')],  # price
		[(1, 'Reuben', 'Cummings', 'reubano@gmail.com')],  # person
		[
			('Scottrade', 'https://trading.scottrade.com/'),
			('Vanguard', 'http://vanguard.com/')],  # company
		[[('Brokerage')], [('Roth IRA')]],  # account_type
		[(1, 1, 1, 1, 'Scottrade'), (2, 2, 1, 1, 'Vanguard IRA')],  # account
		[(6, 1)],  # holding
		[[('buy')], [('sell')]],  # trxn_type
		[(1, 1, 8, 303, '1/1/12', True)]]  # transaction

	return values


def get_pop_values():
	values = [
		[],  # exchange
		[],  # data_source
		[],  # commodity_group
		[],  # commodity_type
		[
			('IBM', 'International Business Machines', 1, 1, 1),
			('WMT', 'Wal-Mart', 1, 1, 1),
			('CAT', 'Caterpillar', 1, 1, 1)],  # commodity
		[],  # event_type
		[(1, 6, 1, 10, '2/1/12'), (1, 8, 1, 12, '2/1/12')],  # event
		[
			(8, 1, 150, '1/1/12'),
			(9, 1, 90, '1/1/12'),
			(10, 1, 120, '1/1/12')],  # price
		[],  # person
		[],  # company
		[],  # account_type
		[],  # account
		[(8, 1), (9, 1), (10, 1)],  # holding
		[],  # trxn_type
		[
			(2, 1, 10, 148, '1/1/12', True),
			(3, 1, 12, 85, '1/1/12', True),
			(1, 1, 8, 320, '2/1/12', True),
			(4, 1, 14, 125, '2/1/12', True)]]  # transaction

	return values
