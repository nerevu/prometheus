# from __future__ import print_function
# from pprint import pprint
from app import db
from flask import Blueprint, render_template, flash, redirect, url_for
from .forms import EventForm, EventTypeForm
from .models import Event, EventType

hermes = Blueprint('hermes', __name__)

def _get_table_info(table):
	def get_entry():
		form_fields = ['symbol', 'event_type_id', 'value', 'date']
		table_headers = ['Symbol', 'Name', 'Unit', 'Value', 'Date']
		data_fields = [(0, 'symbol'), (1, 'name'), (1, 'unit'), (0, 'value'), (0, 'date')]
		query = db.session.query(Event, EventType).join(EventType).order_by(Event.date)
		return form_fields, table_headers, data_fields, query

	def get_entry_type():
		form_fields = ['name', 'unit']
		table_headers = ['Type Name', 'Unit']
		data_fields = ['name', 'unit']
		query = db.session.query(EventType).order_by(EventType.name)
		return form_fields, table_headers, data_fields, query

	def get_price():
		pass

	def get_commodity():
		pass

	switch = {
		'event': get_entry(),
		'event_type': get_entry_type(),
		'price': get_price(),
		'commodity': get_commodity()}

	return switch.get(table)

@hermes.route('/<table>/', methods=['GET', 'POST'])
def get(table):
	table_as_class = table.title().replace('_', '')
	table_as_words = table.title().replace('_', ' ')
	form_fields, table_headers, query, data_fields = _get_table_info(table)
	id = table
	post_location = 'hermes.add'
	post_table = table
	title = '%ss' % table.title()
	table_caption = '%s List' % table_as_words
	form_caption = '%s Entry Form' % table_as_words
	heading = 'Add %ss to the database' % table.replace('_', ' ')
	text = 'On this page you can add %ss to the database and see them instantly updated in the lists below.' % table.replace('_', ' ')
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
		flash('Success! A new %s was posted.' % table.replace('_', ' '), 'alert alert-success')

	else: [flash('%s: %s' % (k.title(), v[0]), 'alert alert-error')
		for k, v in form.errors.iteritems()]
	return redirect(url_for('hermes.get', table=table))

@hermes.route('/worth/', methods=['GET', 'POST'])
def worth():
	pass

@hermes.route('/api/', methods=['GET', 'POST'])
def api():
	pass

