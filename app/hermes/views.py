# from __future__ import print_function
from pprint import pprint
from flask import Blueprint, render_template, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError

from app import db
from app.connection import Connection
from app.helper import get_kwargs, portify
from .forms import EventForm, EventTypeForm, PriceForm, CommodityForm
from .models import Event, EventType, Price, Commodity, CommodityType


hermes = Blueprint('hermes', __name__)


def _bookmark(table):
	global __TABLE__
	__TABLE__ = table


@hermes.route('/<table>/', methods=['GET', 'POST'])
def get(table):
	table_as_class = table.title().replace('_', '')
	form = eval('%sForm.new()' % table_as_class)
	site = portify(url_for('api', _external=True))
	conn = Connection(site, display=True)
	kwargs = get_kwargs(str(table), 'hermes', conn, form)
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
