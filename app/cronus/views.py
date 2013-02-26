# from __future__ import print_function
from pprint import pprint
from flask import Blueprint, render_template, flash, redirect, url_for

from app import Add, q
from app.connection import Connection
from app.helper import get_kwargs, portify, init_form
from . import CSV
from .forms import TransactionForm, TrxnUploadForm
from .models import Transaction

cronus = Blueprint('cronus', __name__)
table = 'transaction'
table_as_class = table.title().replace('_', '')


@cronus.route('/transaction/', methods=['GET', 'POST'])
def transaction():
	site = portify(url_for('api', _external=True))
	conn = Connection(site, display=True)
	form = init_form(TransactionForm)
	kwargs = get_kwargs(str(table), 'cronus', conn, form, False)
	return render_template('entry.html', **kwargs)


@cronus.route('/upload_trxn/', methods=['GET', 'POST'])
def upload():
	form = init_form(TrxnUploadForm)
	name = table.replace('_', ' ')

	if form.validate_on_submit():
		site = portify(url_for('api', _external=True))
		csv = CSV(form['name'], site, display=True)
		job = q.enqueue(csv.post, csv.content)

		flash(
			'Awesome! Your %s upload has just been %s.' % (name, job.status),
			'alert alert-success')

	else:
		[flash('%s: %s.' % (k.title(), v[0]), 'alert alert-error')
			for k, v in form.errors.iteritems()]

	return redirect(url_for('.transaction'))


class AddCronus(Add):
	def get_vars(self):
		form = init_form(eval('%sForm' % table_as_class))
		entry = eval('%s()' % table_as_class)
		redir = '.transaction'
		return form, entry, redir

	def get_table(self):
		return table

	def bookmark_table(self, table):
		pass


@cronus.errorhandler(409)
def duplicate_values(e):
	flash('Error: %s' % e.orig[0], 'alert alert-error')
	return redirect(url_for('.transaction'))

cronus.add_url_rule(
	'/add_trxn/', view_func=AddCronus.as_view('add'), methods=['GET', 'POST'])
