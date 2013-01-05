# from __future__ import print_function
import numpy as np
import app.apollo as ap
import pandas as pd
from pprint import pprint
from flask import Blueprint, render_template, flash

apollo = Blueprint('apollo', __name__)


@apollo.route('/worth/')
def worth():
	list = ['prices', 'dividends', 'rates']
	dfs = []

	for item in list:
		result, keys, dtype, index = eval('ap.get_%s()' % item)
		values = ap.get_values(result, keys)
		df = make_df(values, dtype, index)
		dfs.append(df)

	prices, dividends, rates = dfs[0], dfs[1], dfs[2]
	shares = ap.calculate_shares(prices, dividends)
	pprint(prices)
# 	data = ap.calculate_value(shares, prices, rates)
	data = [('APL', 48), ('IBM', 27), ('Total', 75)]
# 	pprint(data)

	id = 'worth'
	title = 'Net Worth'
	chart_caption = 'Net Worth per Commodity in USD'
	heading = 'View your net worth'
	text = ('On this page you can view the net worth of all ETF, Mutual Fund, '
		'and Stock holdings. Prices are taken from the Prices tab and a '
		'purchase of 100 shares is assumed for each date a price is given.')
	category = 'Commodity'
	data_label = 'Value in USD'

	kwargs = {'id': id, 'title': title, 'heading': heading, 'text': text,
		'columns': data, 'chart_caption': chart_caption,
		'category': category, 'data_label': data_label}

	return render_template('barchart.html', **kwargs)
