from __future__ import print_function
from pprint import pprint
from app import db
from flask import Blueprint, render_template, flash, redirect, url_for
from flask.ext.wtf import AnyOf
from .forms import *
from .models import *

hermes = Blueprint('hermes', __name__)

def _get_form_data():
	result = EventType.query.order_by('name').all()
	choices = [(x.id, '%s (%s)' % (x.name, x.unit)) for x in result]
	values = [x.id for x in result]
	values = sorted(values)
	validators = [Required(), AnyOf(values, message=u'Invalid value, must be one of: %(values)s')]
	return choices, validators

@hermes.route('/prices/', methods=['GET', 'POST'])
def prices():
	return render_template('hermes/events.html')

@hermes.route('/worth/', methods=['GET', 'POST'])
def worth():
	return render_template('hermes/events.html')

@hermes.route('/api/', methods=['GET', 'POST'])
def api():
	return render_template('hermes/events.html')

@hermes.route('/events/', methods=['GET', 'POST'])
def events():
	id = 'events'
	post_url = 'hermes.add_event'
	title = 'Events'
	form_caption = 'Event Entry Form'
	form_fields = ['symbol', 'event_type_id', 'value', 'date']
	table_caption = 'Event Type List'
	table_headers = ['Symbol', 'Name', 'Unit', 'Value', 'Date']
	data_fields = [(0, 'symbol'), (1, 'name'), (1, 'unit'), (0, 'value'), (0, 'date')]

	heading = 'Add events to the database'
	text = 'On this page you can add events to the database and see them instantly updated in the lists below.'

	events = db.session.query(Event, EventType).join(EventType).order_by(Event.date).all()
	choices, validators = _get_form_data()
	form = EventForm()
	form.event_type_id.choices = choices
	form.event_type_id.validators = validators
	kwargs = {'id': id, 'title': title, 'heading': heading, 'text': text,
		'rows': events, 'form': form, 'form_caption': form_caption,
		'table_caption': table_caption, 'table_headers': table_headers,
		'data_fields': data_fields, 'form_fields': form_fields,
		'post_url': post_url}

	return render_template('entry.html', **kwargs)

@hermes.route('/add_event/', methods=['GET', 'POST'])
def add_event():
	choices, validators = _get_form_data()
	form = EventForm()
	form.event_type_id.choices = choices
	form.event_type_id.validators = validators
	if form.validate_on_submit():
		event = Event()
		form.populate_obj(event)
 		db.session.add(event)
		db.session.commit()
		flash('Success! A new event was posted.', 'alert alert-success')
	else: [flash('%s: %s' % (k.title(), v[0]), 'alert alert-error')
		for k, v in form.errors.iteritems()]
	return redirect(url_for('hermes.events'))

@hermes.route('/event_types/', methods=['GET', 'POST'])
def event_types():
	id = 'event_types'
	post_url = 'hermes.add_event_type'
	title = 'Types'
	form_caption = 'Event Type Entry Form'
	form_fields = ['name', 'unit']
	table_caption = 'Event Type List'
	table_headers = ['Type Name', 'Unit']
	data_fields = ['name', 'unit']
	heading = 'Add event types to the database'
	text = 'On this page you can add event types to the database and see them instantly updated in the lists below.'

	event_types = db.session.query(EventType).order_by(EventType.name).all()
	form = EventTypeForm()
	kwargs = {'id': id, 'title': title, 'heading': heading, 'text': text,
		'rows': event_types, 'form': form, 'form_caption': form_caption,
		'table_caption': table_caption, 'table_headers': table_headers,
		'data_fields': data_fields, 'form_fields': form_fields,
		'post_url': post_url}

	return render_template('entry.html', **kwargs)

@hermes.route('/add_event_type/', methods=['GET', 'POST'])
def add_event_type():
	form = EventTypeForm()
	if form.validate_on_submit():
		type = EventType()
		form.populate_obj(type)
 		db.session.add(type)
		db.session.commit()
		flash('Success! A new event type was posted.', 'alert alert-success')
	else: [flash('%s: %s' % (k.title(), v[0]), 'alert alert-error')
		for k, v in form.errors.iteritems()]
	return redirect(url_for('hermes.event_types'))
