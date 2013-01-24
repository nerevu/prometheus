from pprint import pprint


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
