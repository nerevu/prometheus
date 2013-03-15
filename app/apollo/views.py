# from __future__ import print_function
import time
import numpy as np
import pandas as pd

from pprint import pprint
from json import dumps, loads
from redis import Redis
from rq import Queue
from rq.job import Job
from collections import deque
from flask import Blueprint, render_template, url_for, jsonify, request

from app.connection import Connection
from app.helper import portify
from . import Worth

apollo = Blueprint('apollo', __name__)
rconn = Redis()


@apollo.route('/get_ids/')
def get_ids():
	site = portify(url_for('api', _external=True))
	conn = Connection(site)
	q = Queue(connection=rconn)
	tables = [
		'transaction', 'dividend', 'security_prices', 'price', 'security_data']
	jobs = [q.enqueue_call(func=getattr, args=(conn, item)) for item in tables]
	table = request.args.get('table', 'USD')
	jobs.append(q.enqueue_call(func=conn.commodity_ids, args=(table,)))
	result = [job.id for job in jobs]
	return jsonify(result=','.join(result))


# @apollo.route('/poll/')
# def poll():
# 	job_ids = request.args.get('job_ids').split(',')
# 	jobs = [Job.fetch(j, connection=rconn) for j in job_ids]
# 	return jsonify(result=all(job.is_finished for job in jobs))


@apollo.route('/get_res/')
def get_res():
	job_ids = request.args.get('job_ids').split(',')
	jobs = [Job.fetch(j, connection=rconn) for j in job_ids]
	result = [job.result for job in jobs]
	return jsonify(result=dumps(result))


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
# 	return render_template('index.html', **kwargs)
