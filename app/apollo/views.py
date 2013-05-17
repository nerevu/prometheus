# from __future__ import print_function
import time
import numpy as np
import pandas as pd

from pprint import pprint
from json import loads
from collections import deque
from flask import Blueprint, render_template, url_for, jsonify, request

from app.connection import Connection
from . import Worth

apollo = Blueprint('apollo', __name__)


@apollo.route('/get_ids/')
def get_ids():
	conn = Connection()
	tables = [
		'transaction', 'dividend', 'security_prices', 'price', 'security_data']
	jobs = [q.enqueue_call(func=getattr, args=(conn, item)) for item in tables]
	table = request.args.get('table', 'USD')
	jobs.append(q.enqueue_call(func=conn.commodity_ids, args=(table,)))
	result = [job.id for job in jobs]
	return jsonify(result=','.join(result))


@apollo.route('/worth_data/')
def worth_data():
	mp = Worth(*loads(request.args.get('args')))
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
