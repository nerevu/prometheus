from datetime import datetime as dt, date as d, timedelta
from flask import current_app as app
from flask.ext.wtf import AnyOf, Required


# For use with Connection
def app_site():
	return app.config['API_URL']


# For flask-script
def get_init_values():
	return [
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
			('CAD', 'Canadian Dollar', 5, 3, 4),
			('Multiple', 'Multiple', 6, 3, 4),
			('AAPL', 'Apple', 1, 1, 1),
			('Text', 'Text', 6, 3, 4)],  # commodity
		[
			[('Dividend')], [('Special Dividend')], [('Stock Split')],
			[('Name Change')], [('Ticker Change')]],  # event_type
		[],  # event
		[],  # price
		[(1, 'Reuben', 'Cummings', 'reubano@gmail.com')],  # person
		[
			('Scottrade', 'https://trading.scottrade.com/'),
			('Vanguard', 'http://vanguard.com/')],  # company
		[[('Brokerage')], [('Roth IRA')]],  # account_type
		[(1, 1, 1, 1, 'Scottrade'), (2, 2, 1, 1, 'Vanguard IRA')],  # account
		[(6, 1)],  # holding
		[[('Buy')], [('Sell')]],  # trxn_type
		[]]  # transaction


def get_pop_values():
	return [
		[
			('IBM', 'International Business Machines', 1, 1, 1),
			('WMT', 'Wal-Mart', 1, 1, 1),
			('CAT', 'Caterpillar', 1, 1, 1)],  # commodity
		[(8, 1), (9, 1), (10, 1)]]  # holding


# For views
def get_plural(word):
	if word[-1] == 'y':
		return word[:-1] + 'ies'
	else:
		return word + 's'


def get_kwargs(table, module, conn, form=None, post_table=True):
	plural_table = get_plural(table).replace('_', ' ')
	table_title = table.title().replace('_', ' ')
	plural_table_title = plural_table.title()
	form_fields, table_headers, results, keys = getattr(conn, table)
	rows = conn.values(results, keys)

	post_table = table if post_table else None
	form_caption = '%s Entry Form' % table_title
	heading = 'The %s database' % plural_table
	subheading = (
		'Add %s to the database and see them instantly updated in the lists '
		'below.' % plural_table)

	return {
		'id': table, 'title': plural_table_title, 'heading': heading,
		'subheading': subheading, 'rows': rows, 'form': form,
		'form_caption': form_caption, 'table_caption': '%s List' % table_title,
		'table_headers': table_headers, 'form_fields': form_fields,
		'post_location': '%s.add' % module, 'post_table': post_table}


def init_form(form):
	try:
		form = form.new()
	except AttributeError:
		pass

	return form


# For forms
def get_choices(table, field, conn, order=None, name=None, val=None):
	if (name and val):
		query = {'filters': [{'name': name, 'op': 'in', 'val': val}]}
	else:
		query = None

	result = conn.get(table, query)
	values = [x.field for x in result]
	selection = [x.order for x in result]
	return zip(values, selection)


def get_x_choices(tables, fields, conn):
	result = conn.get(tables[0])
	values = [x.fields[0] for x in result]
	selection = [x.tables[1].fields[1] for x in result]
	return zip(values, selection)


def get_validators(table, field, conn):
	result = conn.get(table)
	values = [x.field for x in result]
	values = sorted(values)

	return [
		Required(), AnyOf(
			values, message=u'Invalid value, must be one of:'
			'%(values)s')]
