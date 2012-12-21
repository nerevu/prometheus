from __future__ import print_function
from pprint import pprint
from app import db
from flask import Blueprint, render_template, flash, redirect, url_for
from flask.ext.wtf import AnyOf
from .forms import *
from .models import *

hermes = Blueprint('hermes', __name__)

def _get_form_data():
	result = Type.query.order_by('name').all()
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
	legend = 'Event entry form'
	heading = 'Add events to the database'
	text = 'On this page you can add events to the database and see them instantly updated in the lists below.'

	events = db.session.query(Event, Type).join(Type).order_by(Event.date)
	choices, validators = _get_form_data()
	form = EventForm()
	form.type_id.choices = choices
	form.type_id.validators = validators
	kwargs = {'id': id, 'title': title, 'heading': heading, 'text': text,
		'events': events, 'types': types, 'form': form, 'legend': legend,
		'post_url': post_url}

	return render_template('hermes/event.html', **kwargs)

@hermes.route('/add_event/', methods=['GET', 'POST'])
def add_event():
	choices, validators = _get_form_data()
	form = EventForm()
	form.type_id.choices = choices
	form.type_id.validators = validators
	if form.validate_on_submit():
		event = Event()
		form.populate_obj(event)
		print('Submitted!')
		print(form.type_id.data)
 		db.session.add(event)
		db.session.commit()
		flash('Success! A new event was posted.', 'alert alert-success')
	else: [flash('%s: %s' % (k.title(), v[0]), 'alert alert-error')
		for k, v in form.errors.iteritems()]
	return redirect(url_for('hermes.events'))

@hermes.route('/types/', methods=['GET', 'POST'])
def types():
	id = 'types'
	post_url = 'hermes.add_event_type'
	title = 'Types'
	legend = 'Type entry form'
	heading = 'Add event types to the database'
	text = 'On this page you can add event types to the database and see them instantly updated in the lists below.'

	types = db.session.query(Type).order_by(Type.name)
	form = TypeForm()
	kwargs = {'id': id, 'title': title, 'heading': heading, 'text': text,
		'events': events, 'types': types, 'form': form, 'legend': legend,
		'post_url': post_url}

	return render_template('hermes/event_type.html', **kwargs)

	form = TypeForm()
@hermes.route('/add_event_type/', methods=['GET', 'POST'])
def add_event_type():
	if form.validate_on_submit():
		type = Type()
		form.populate_obj(type)
 		db.session.add(type)
		db.session.commit()
		flash('Success! A new event type was posted.', 'alert alert-success')
	else: [flash('%s: %s' % (k.title(), v[0]), 'alert alert-error')
		for k, v in form.errors.iteritems()]
	return redirect(url_for('hermes.types'))
