# from __future__ import print_function
from pprint import pprint
from app import db
from flask import Blueprint, render_template, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from app.connection import Connection, portify
from .forms import EventForm, EventTypeForm, PriceForm, CommodityForm
from .models import Event, EventType, Price, Commodity, CommodityType
from . import get_table_info, get_plural

hermes = Blueprint('hermes', __name__)


def _bookmark(table):
	global __TABLE__
	__TABLE__ = table


@hermes.route('/<table>/', methods=['GET', 'POST'])
def get(table):
	site = portify(url_for('api', _external=True))
	conn = Connection(site, display=True)

	plural_table = get_plural(table).replace('_', ' ')
	table_as_class = table.title().replace('_', '')
	table_title = table.title().replace('_', ' ')
	plural_table_title = plural_table.title()
	form_fields, table_headers, results, keys = getattr(conn, table)
	rows = conn.values(results, keys)

	id = table
	post_location = 'hermes.add'
	post_table = table
	title = '%s' % plural_table_title
	table_caption = '%s List' % table_title
	form_caption = '%s Entry Form' % table_title
	heading = 'The %s database' % plural_table
	subheading = (
		'Add %s to the database and see them '
		'instantly updated in the lists below.' % plural_table)
	results = query.all()

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


@hermes.route('/add/<table>/', methods=['GET', 'POST'])
def add(table):
	table_as_class = table.title().replace('_', '')

	try:
		form = eval('%sForm.new()' % table_as_class)
	except AttributeError:
		form = eval('%sForm()' % table_as_class)

	if form.validate_on_submit():
		entry = eval('%s()' % table_as_class)
		form.populate_obj(entry)
		db.session.add(entry)
		_bookmark(table)
		db.session.commit()
		flash(
			'Awesome! You just posted a new %s.' % table.replace('_', ' '),
			'alert alert-success')

	else:
		[flash('%s: %s.' % (k.title(), v[0]), 'alert alert-error')
			for k, v in form.errors.iteritems()]

	return redirect(url_for('.get', table=table))


@hermes.errorhandler(409)
@hermes.errorhandler(IntegrityError)
def duplicate_values(e):
	flash('Error: %s' % e.orig[0], 'alert alert-error')
	return redirect(url_for('.get', table=__TABLE__))
