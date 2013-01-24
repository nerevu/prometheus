import app.apollo as ap

from pprint import pprint
from flask import Blueprint, render_template, flash, redirect, url_for
from flask import current_app as app

from app import db, get_plural
from app.connection import Connection, portify
from .forms import TransactionForm
from .models import Transaction

cronus = Blueprint('cronus', __name__)
table = 'transaction'


@cronus.route('/transaction/', methods=['GET', 'POST'])
def transaction():
	site = portify(url_for('api', _external=True))
	conn = Connection(site, display=True)

	plural_table = get_plural(table).replace('_', ' ')
	table_as_class = table.title().replace('_', '')
	table_title = table.title().replace('_', ' ')
	plural_table_title = plural_table.title()
	form_fields, table_headers, results, keys = getattr(conn, table)
	rows = conn.values(results, keys)

	id = table
	post_location = 'cronus.add_trxn'
	post_table = None
	title = '%s' % plural_table_title
	table_caption = '%s List' % table_title
	form_caption = '%s Entry Form' % table_title
	heading = 'The %s database' % plural_table
	subheading = (
		'Add %s to the database and see them '
		'instantly updated in the lists below.' % plural_table)

	try:
		form = eval('%sForm.new()' % table_as_class)
	except AttributeError:
		form = eval('%sForm()' % table_as_class)

	kwargs = {
		'id': id, 'title': title, 'heading': heading,
		'subheading': subheading, 'rows': rows, 'form': form,
		'form_caption': form_caption, 'table_caption': table_caption,
		'table_headers': table_headers, 'form_fields': form_fields,
		'post_location': post_location, 'post_table': post_table}

	return render_template('entry.html', **kwargs)


@cronus.route('/add_trxn/', methods=['GET', 'POST'])
def add_trxn():
	pass
