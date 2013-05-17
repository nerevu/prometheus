# from __future__ import print_function
from pprint import pprint
from flask import Blueprint, render_template, flash, redirect, url_for

from app import Add
from app.helper import HelpForm, app_site, init_form
from .sources import CSV
from .forms import TransactionForm, TrxnUploadForm

cronus = Blueprint('cronus', __name__)
table = 'transaction'
redir = '.transaction'


@cronus.route('/transaction/', methods=['GET', 'POST'])
def transaction():
	conn = HelpForm(app_site())
	form = init_form(TransactionForm)
	kwargs = conn.get_kwargs(table, 'cronus', form, False)
	return render_template('entry.html', **kwargs)


@cronus.route('/upload/', methods=['GET', 'POST'])
def upload():
	form = init_form(TrxnUploadForm)
	csv = CSV(form['name'])
	func = csv.post
	args = (csv.load(),)
	return form, func, args, table, redir


class AddCronus(Add):
	def get_vars(self, table):
		table_as_class = table.title().replace('_', '')
		form = init_form(eval('%sForm' % table_as_class))
		entry = eval('%s()' % table_as_class)
		return form, entry, redir

	@property
	def table(self):
		return table

	def bookmark_table(self, table):
		pass


@cronus.errorhandler(409)
def duplicate_values(e):
	flash('Error: %s' % e.orig[0], 'alert alert-error')
	return redirect(url_for('.transaction'))

cronus.add_url_rule(
	'/add_trxn/', view_func=AddCronus.as_view('add'), methods=['GET', 'POST'])
