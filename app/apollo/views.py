# from __future__ import print_function
import numpy as np
import app.apollo as ap
import pandas as pd

from pprint import pprint
from flask import Blueprint, render_template, flash, redirect, url_for

apollo = Blueprint('apollo', __name__)


@apollo.route('/worth/<table>/')
def worth(table):
#	table = 'USD'
	list = ['prices', 'dividends', 'rates', 'commodities']
	dfs = []

	for item in list:
		result, keys, dtype, index = eval('ap.get_%s()' % item)
		values = ap.get_values(result, keys)

		if values:
			df = ap.make_df(values, dtype, index)
			df = ap.sort_df(df)
		else:
			df = ap.empty_df()

		dfs.append(df)

	prices, dividends, rates, commodities = dfs[0], dfs[1], dfs[2], dfs[3]

	if not dividends.empty and not prices.empty:
		reinvestments, missing = ap.get_reinvestments(dividends, prices)
	else:
		reinvestments, missing = ap.empty_df(), None

	if not prices.empty or not reinvestments.empty:
		transactions = ap.get_transactions(prices, reinvestments, 100)
		transactions = ap.sort_df(transactions)
		shares = ap.get_shares(transactions)
		values = ap.calculate_value(shares, prices, rates, 1)
		data = ap.convert_values(values, commodities)
	else:
		transactions = []
		data = [('N/A', 0)]

	id = 'worth'
	title = 'Net Worth'
	chart_caption = 'Net Worth per Commodity in %s' % table

	if missing:
		chart_caption = '%s (some price data is missing)' % chart_caption
	elif transactions.empty:
		chart_caption = 'No transactions found. Please enter some events or prices.'

	heading = 'View your net worth'
	subheading = ('View the net worth of all ETF, Mutual Fund, '
		'and Stock holdings. Prices are taken from the Prices tab and a '
		'purchase of 100 shares is assumed for each date a price is given.')
	category = 'Commodity'
	data_label = 'Value in %s' % table

	kwargs = {'id': id, 'title': title, 'heading': heading,
		'subheading': subheading, 'columns': data,
		'chart_caption': chart_caption, 'category': category,
		'data_label': data_label}

	return render_template('barchart.html', **kwargs)
