from pprint import pprint
from json import dumps as dmp
from requests import post

# pep8: disable=E121
# pep8 --ignore E121

__HDR__ = {'content-type': 'application/json'}

__TABLES__ = (
	'exchange',
	'data_source',
	'commodity_group',
	'commodity_type',
	'commodity',
	'event_type',
	'price',
	'person',
	'company',
	'account_type',
	'account',
	'holding',
	'trxn_type',
	'transaction',
)

__KEYS__ = [
	('symbol', 'name'),
	# extra list is needed so dict doesn't iterate over each character
	[('name')],
	[('name')],
	('name', 'group_id'),
	('symbol', 'name', 'type_id', 'data_source_id', 'exchange_id'),
	[('name')],
	('commodity_id', 'currency_id', 'close'),
	('currency_id', 'first_name', 'last_name', 'email'),
	('name', 'website'),
	[('name')],
	('type_id', 'company_id', 'currency_id', 'person_id', 'name'),
	('commodity_id', 'account_id'),
	[('name')],
	('holding_id', 'type_id', 'shares', 'price', 'date', 'commissionable')]


def init_db(site):
	init_values = [
		[('NYSE', 'New York Stock Exchange'), ('NASDAQ', 'NASDAQ'),
			('OTC', 'Over the counter'), ('N/A', 'Currency')],
		[[('Yahoo')], [('Google')], [('XE')]],
		[[('Security')], [('Currency')], [('Other')]],
		[('Stock', 1), ('Bond', 1), ('Mutual Fund', 1), ('ETF', 1),
			('Currency', 2), ('Descriptor', 3)],
		[('USD', 'US Dollar', 5, 3, 4),
			('EUR', 'Euro', 5, 3, 4),
			('GBP', 'Pound Sterling', 5, 3, 4),
			('TZS', 'Tanzanian Shilling', 5, 3, 4),
			('Multiple', 'Multiple', 6, 3, 4),
			('APL', 'Apple', 1, 1, 1),
			('Text', 'Text', 6, 3, 4)],
		[[('Dividend')], [('Special Dividend')], [('Stock Split')],
			[('Name Change')], [('Ticker Change')]],
		[(2, 1, 1.2), (3, 1, 1.8), (4, 1, 1.0 / 1580.0)],
		[(1, 'Reuben', 'Cummings', 'reubano@gmail.com')],
		[('Scottrade', 'https://trading.scottrade.com/'),
			('Vanguard', 'http://vanguard.com/')],
		[[('Brokerage')], [('Roth IRA')]],
		[(1, 1, 1, 1, 'Scottrade'), (2, 2, 1, 1, 'Vanguard IRA')],
		[(6, 1)],
		[[('buy')], [('sell')]],
		[(1, 1, 10, 100, '1/1/12', True)]]

	combo = zip(__KEYS__, init_values)

	# content
	table_data = [
		[dict(zip(list[0], values)) for values in list[1]] for list in combo]

	content_keys = ('table', 'data')
	content_values = zip(__TABLES__, table_data)
	content = [dict(zip(content_keys, values)) for values in content_values]

	for piece in content:
		table = piece['table']
		data = piece['data']

		for d in data:
			r = post('%s%s' % (site, table), data=dmp(d), headers=__HDR__)

			if r.status_code != 201:
				raise AttributeError(
					'Response: %s. Request %s with content '
					'%s sent to %s' % (
						r.status_code, r.request.data, r._content, r.url))

	return r


def pop_db(site):
	pass
