# from __future__ import print_function
from pprint import pprint
from json import loads
from collections import deque
from flask import Blueprint, render_template, url_for, jsonify, request
from app.helper import app_site
from app.connection import Connection
from . import Worth

apollo = Blueprint('apollo', __name__)


@apollo.route('/worth_data/')
def worth_data():
	conn = Connection(app_site())
	tables = [
		'transaction', 'dividend', 'security_prices', 'price', 'security_data']
	table = request.args.get('table', 'USD')
	res = [getattr(conn, t) for t in tables]
	res.append(conn.commodity_ids(table))

	# TODO: Fix 'nan' error with init_db
	mp = Worth(*res)
	worth = mp.convert_worth(mp.calc_worth())
	return jsonify(
		result=worth, id=mp.currency_id, missing=mp.missing, empty=mp.empty)


@apollo.route('/worth/')
@apollo.route('/worth/<table>/')
def worth(table='USD'):
	id = 'worth'
	title = 'Net Worth'
	chart_caption = 'Net Worth per Commodity in %s' % table
	heading = 'View your net worth'
	subheading = (
		'View the net worth of all ETF, Mutual Fund, and Stock holdings. '
		'Transactions are summed from the Events and Transactions tabs, and '
		'prices are taken from the Prices tab.')

	category = 'Commodity'
	data_label = 'Value in %s' % table

	kwargs = {
		'id': id, 'title': title, 'heading': heading,
		'subheading': subheading, 'table': table,
		'chart_caption': chart_caption, 'category': category,
		'data_label': data_label}

	return render_template('barchart.html', **kwargs)
