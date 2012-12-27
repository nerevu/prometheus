# from __future__ import print_function
# from pprint import pprint
from app import db
from flask import Blueprint, render_template, flash, redirect, url_for
from sqlalchemy.orm import aliased
from .forms import EventForm, EventTypeForm, PriceForm, CommodityForm
from .models import Event, EventType, Price, Commodity, CommodityType

hermes = Blueprint('hermes', __name__)


def _get_table_info(table):
	def get_event():
		form_fields = ['symbol', 'type_id', 'value', 'date']
		table_headers = ['Symbol', 'Name', 'Unit', 'Value', 'Date']
		query = db.session.query(Event, EventType, Commodity).join(EventType) \
			.join(Commodity, EventType.unit).order_by(Event.date)
		data_fields = [(0, 'symbol'), (1, 'name'), (2, 'symbol'), (0, 'value'),
			(0, 'date')]
		return form_fields, table_headers, query, data_fields

	def get_event_type():
		form_fields = ['name', 'commodity_id']
		table_headers = ['Type Name', 'Unit']
		query = db.session.query(EventType, Commodity).join(Commodity) \
			.order_by(EventType.name)
		data_fields = [(0, 'name'), (1, 'symbol')]
		return form_fields, table_headers, query, data_fields

	def get_price():
		form_fields = ['commodity_id', 'currency_id', 'date', 'close']
		table_headers = ['Stock', 'Currency', 'Date', 'Price']
		Currency = aliased(Commodity)
		query = db.session.query(Price, Commodity, Currency) \
			.join(Price.commodity).join(Currency, Price.currency) \
			.order_by(Price.date)
		data_fields = [(1, 'symbol'), (2, 'symbol'), (0, 'date'), (0, 'close')]
		return form_fields, table_headers, query, data_fields

	def get_commodity():
		form_fields = ['symbol', 'name', 'type_id', 'data_source_id',
			'exchange_id']
		table_headers = ['Symbol', 'Name', 'Type']
		query = db.session.query(Commodity, CommodityType).join(CommodityType) \
			.order_by(Commodity.name)
		data_fields = [(0, 'symbol'), (0, 'name'), (1, 'name')]
		return form_fields, table_headers, query, data_fields

	switch = {'event': get_event(),
		'event_type': get_event_type(),
		'price': get_price(),
		'commodity': get_commodity()}

	return switch.get(table)


def _get_plural(word):
	if word[-1] == 'y':
		return word[:-1] + 'ies'
	else:
		return word + 's'


@hermes.route('/<table>/', methods=['GET', 'POST'])
def get(table):
	plural_table = _get_plural(table).replace('_', ' ')
	table_as_class = table.title().replace('_', '')
	table_title = table.title().replace('_', ' ')
	plural_table_title = plural_table.title()
	form_fields, table_headers, query, data_fields = _get_table_info(table)
	id = table
	post_location = 'hermes.add'
	post_table = table
	title = '%s' % plural_table_title
	table_caption = '%s List' % table_title
	form_caption = '%s Entry Form' % table_title
	heading = 'Add %s to the database' % plural_table
	text = 'On this page you can add %s to the database and see them ' \
		'instantly updated in the lists below.' % plural_table
	results = query.all()

	try:
		form = eval('%sForm.new()' % table_as_class)
	except AttributeError:
		form = eval('%sForm()' % table_as_class)

	kwargs = {'id': id, 'title': title, 'heading': heading, 'text': text,
		'rows': results, 'form': form, 'form_caption': form_caption,
		'table_caption': table_caption, 'table_headers': table_headers,
		'data_fields': data_fields, 'form_fields': form_fields,
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
		db.session.commit()
		flash('Success! A new %s was posted.' % table.replace('_', ' '),
			'alert alert-success')

	else:
		[flash('%s: %s' % (k.title(), v[0]), 'alert alert-error')
			for k, v in form.errors.iteritems()]

	return redirect(url_for('hermes.get', table=table))


@hermes.route('/worth/', methods=['GET', 'POST'])
def worth():
	pass


@hermes.route('/api/', methods=['GET', 'POST'])
def api():
	pass
