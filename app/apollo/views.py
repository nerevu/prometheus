# from __future__ import print_function
import numpy as np
import pandas as pd
import app.apollo as ap

from pprint import pprint
from flask import Blueprint, render_template

apollo = Blueprint('apollo', __name__)


@apollo.route('/worth/')
@apollo.route('/worth/<table>/')
def worth(table='USD'):
# 	currency_id = id_from_value(table, commodity)
	currency_id = 1
	id = 'worth'
	title = 'Net Worth'
	chart_caption = 'Net Worth per Commodity in %s' % table
	list = ['prices', 'dividends', 'rates', 'commodities']

	results = [ap.get_table_info(item)[0] for item in list]
	keys = [ap.get_table_info(item)[1] for item in list]
	values = [ap.get_values(z[0], z[1]) for z in zip(results, keys)]
	dfs = [ap.DataFrame(z[0], keys=z[1]) for z in zip(values, keys)]
	d = dict(zip(list, dfs))

	result, keys = ap.get_table_info('transactions')
	data = ap.get_values(result, keys)
	mp = ap.Portfolio(
		data, currency_id=currency_id, commodities=d['commodities'])

	reinvestments = mp.calc_reinvestments(d['dividends'], d['prices'])
	values = mp.calc_value(d['prices'], d['rates'], reinvestments)
	data = mp.convert_values(values)

	# fix if missing
	missing = False

	if missing:
		chart_caption = '%s (some price data is missing)' % chart_caption
	elif mp.empty:
		chart_caption = 'No transactions found. Please enter some events or prices.'

	heading = 'View your net worth'
	subheading = (
		'View the net worth of all ETF, Mutual Fund, and Stock '
		'holdings. Prices are taken from the Prices tab and a purchase of 100'
		' shares is assumed for each date a price is given.')

	category = 'Commodity'
	data_label = 'Value in %s' % table

	kwargs = {
		'id': id, 'title': title, 'heading': heading,
		'subheading': subheading, 'columns': data,
		'chart_caption': chart_caption, 'category': category,
		'data_label': data_label}

	return render_template('barchart.html', **kwargs)
