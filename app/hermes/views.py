# from __future__ import print_function
from pprint import pprint
from flask import Blueprint, render_template, flash, redirect, url_for

from app import Add
from app.helper import HelpForm, app_site, init_form
from .forms import EventForm, EventTypeForm, PriceForm, CommodityForm

hermes = Blueprint('hermes', __name__)


def _bookmark(table):
	global __TABLE__
	__TABLE__ = table


@hermes.route('/<table>/', methods=['GET', 'POST'])
def get(table):
	conn = HelpForm(app_site())
	table_as_class = table.title().replace('_', '')
	form = init_form(eval('%sForm' % table_as_class))
	kwargs = conn.get_kwargs(table, 'hermes', conn.get('keys'), form)
	return render_template('entry.html', **kwargs)


class AddHermes(Add):
	def get_vars(self, table):
		table_as_class = table.title().replace('_', '')
		form = init_form(eval('%sForm' % table_as_class))
		conn = HelpForm(app_site())
		redir = '.get'
		return form, conn, redir

	def bookmark_table(self, table):
		_bookmark(table)


@hermes.errorhandler(409)
# @hermes.errorhandler(IntegrityError)
def duplicate_values(e):
	flash('Error: %s' % e.orig[0], 'alert alert-error')
	return redirect(url_for('.get', table=__TABLE__))

hermes.add_url_rule(
	'/add/<table>/', view_func=AddHermes.as_view('add'),
	methods=['GET', 'POST'])
