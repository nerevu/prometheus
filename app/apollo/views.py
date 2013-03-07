# from __future__ import print_function
import numpy as np
import pandas as pd

from pprint import pprint
from flask import Blueprint, render_template, url_for

from app import db
from app.connection import Connection
from app.helper import portify
from . import Worth

apollo = Blueprint('apollo', __name__)


@apollo.route('/worth/')
@apollo.route('/worth/<table>/')
def worth(table='USD'):
	site = portify(url_for('api', _external=True))
	conn = Connection(site)
	currency_id = conn.ids_from_symbols(table)

	if not currency_id and table != 'USD':
		table = 'USD (%s rates not available)' % table

	currency_id = (currency_id or 1)
	conn.native = currency_id
	id = 'worth'
	title = 'Net Worth'
	chart_caption = 'Net Worth per Commodity in %s' % table
	tables = ['raw_transaction', 'dividend', 'raw_price', 'rate', 'stock']

	results = [getattr(conn, item)[0] for item in tables]
	keys = [getattr(conn, item)[1] for item in tables]
	values = [conn.values(z[0], z[1]) for z in zip(results, keys)]
	data = zip(values, keys)
	d = dict(zip(tables, data))

	arg1, arg2 = tuple(d['raw_transaction'])
	cols = [k[1] for k in arg2]
	args = [arg1, cols, None, d['dividend'], d['raw_price'], d['rate']]
	kwargs = {'currency_id': currency_id, 'mapping': d['stock']}

	mp = Worth(*args, **kwargs)
	worth = mp.calc_worth()
	data = mp.convert_worth(worth)

	if mp.missing:
		chart_caption = '%s (some price data is missing)' % chart_caption
	elif mp.empty:
		chart_caption = 'No transactions found. Please enter some events or prices.'

	heading = 'View your net worth'
	subheading = (
		'View the net worth of all ETF, Mutual Fund, and Stock holdings. '
		'Transactions are summed from the Events and Transactions tabs, and '
		'prices are taken from the Prices tab.')

	category = 'Commodity'
	data_label = 'Value in %s' % table

	kwargs = {
		'id': id, 'title': title, 'heading': heading,
		'subheading': subheading, 'columns': data,
		'chart_caption': chart_caption, 'category': category,
		'data_label': data_label}

	return render_template('barchart.html', **kwargs)
