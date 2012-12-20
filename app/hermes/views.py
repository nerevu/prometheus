from __future__ import print_function
from pprint import pprint
from app import db
from flask import Blueprint, render_template, flash, redirect, url_for
from flask.ext.wtf import AnyOf
from .forms import *
from .models import *

hermes = Blueprint('hermes', __name__, url_prefix='/hermes')

def _get_form_data():
# 	with app.test_request_context():
	result = Type.query.order_by('name').all()
	choices = [(x.id, '%s (%s)' % (x.name, x.unit)) for x in result]
	values = [x.id for x in result]
	validators = [Required(), AnyOf(choices, message=u'Invalid value, must be one of: %(values)s')]
	return choices, validators

@hermes.route('/', methods=['GET', 'POST'])
def events():
	events = db.session.query(Event, Type).join(Type).all()
	choices, validators = _get_form_data()
	form = EventForm()
	form.type_id.choices = choices
	form.type_id.validators = validators
	return render_template('hermes/events.html', events=events, form=form)

@hermes.route('/add/', methods=['GET', 'POST'])
def add_event():
	choices, validators = _get_form_data()
	form = EventForm()
	form.type_id.choices = choices
	form.type_id.validators = validators
	if form.validate_on_submit():
		event = Event()
		form.populate_obj(event)
		print(form.type_id.data)
 		db.session.add(event)
		db.session.commit()
		flash('Success! A new event was posted.', 'alert alert-success')
	else: [flash('%s: %s' % (k.title(), v[0]), 'alert alert-error')
		for k, v in form.errors.iteritems()]
	return redirect(url_for('hermes.events'))
