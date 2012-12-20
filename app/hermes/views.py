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
	title = 'Events & Types'
	heading = 'Add events and types to the database'
	text = 'On this page you can add events and event types to the database and see them instantly updated in the lists below.'

	events = db.session.query(Event, Type).join(Type).order_by(Event.date)
	types = db.session.query(Type).order_by(Type.name)
	choices, validators = _get_form_data()
	form1 = EventForm()
	form1.type_id.choices = choices
	form1.type_id.validators = validators
	form2 = TypeForm()
	kwargs = {'id': 'events', 'title': title, 'heading': heading, 'text': text,
		'events': events, 'types': types, 'form1': form1, 'form1_title': 'Events',
		'form2': form2, 'form2_title': 'Types'}

	return render_template('hermes/events.html', **kwargs)

@hermes.route('/add_event/', methods=['GET', 'POST'])
def add_event():
	choices, validators = _get_form_data()
	form = EventForm()
	print('Event form set!')
	form.type_id.choices = choices
	form.type_id.validators = validators
	if form.validate_on_submit():
		event = Event()
		form.populate_obj(event)
 		db.session.add(event)
		db.session.commit()
		flash('Success! A new event was posted.', 'alert alert-success')
	else: [flash('%s: %s' % (k.title(), v[0]), 'alert alert-error')
		for k, v in form.errors.iteritems()]
	return redirect(url_for('hermes.events'))

@hermes.route('/add_type/', methods=['GET', 'POST'])
def add_type():
	form = TypeForm()
	print('Type form set!')
	if form.is_submitted():
		print('Submitted!')
		type = Type()
		form.populate_obj(type)
 		db.session.add(type)
		db.session.commit()
		flash('Success! A new event type was posted.', 'alert alert-success')
	else: [flash('%s: %s' % (k.title(), v[0]), 'alert alert-error')
		for k, v in form.errors.iteritems()]
	return redirect(url_for('hermes.events'))
