# from __future__ import print_function
from pprint import pprint
from flask import Blueprint, render_template, flash, redirect, url_for

from app.connection import Connection
from app.helper import get_kwargs, portify
from .forms import TransactionForm
from .models import Transaction

cronus = Blueprint('cronus', __name__)
table = 'transaction'


@cronus.route('/transaction/', methods=['GET', 'POST'])
def transaction():
	site = portify(url_for('api', _external=True))
	conn = Connection(site, display=True)
	kwargs = get_kwargs(str(table), 'cronus', conn, TransactionForm, False)
	return render_template('entry.html', **kwargs)


@cronus.route('/add_trxn/', methods=['GET', 'POST'])
def add():
	table_as_class = table.title().replace('_', '')

	try:
		form = eval('%sForm.new()' % table_as_class)
	except AttributeError:
		form = eval('%sForm()' % table_as_class)

	if form.validate_on_submit():
		site = portify(url_for('api', _external=True))
		conn = Connection(site, display=True)
		entry = eval('%s()' % table_as_class)
		form.populate_obj(entry)
		keys = [f for f in form._fields.keys() if f != 'csrf_token']
		values = [getattr(form, k).data for k in keys]
		content = conn.process(values, table, keys)
		conn.post(content)
		flash(
			'Awesome! You just posted a new %s.' % table.replace('_', ' '),
			'alert alert-success')

	else:
		[flash('%s: %s.' % (k.title(), v[0]), 'alert alert-error')
			for k, v in form.errors.iteritems()]

	return redirect(url_for('.transaction'))


@cronus.errorhandler(409)
def duplicate_values(e):
	flash('Error: %s' % e.orig[0], 'alert alert-error')
	return redirect(url_for('.transaction'))
