from datetime import datetime as dt, date as d, timedelta
from flask import current_app as app
from flask.ext.wtf import AnyOf, Required
from app.connection import Connection


def app_site():
	return app.config['API_URL']


def get_plural(word):
	if word[-1] == 'y':
		return word[:-1] + 'ies'
	else:
		return word + 's'


def init_form(form):
	form = form.new()
	return form


class HelpForm(Connection):
	def __init__(self, *args, **kwargs):
		"""
		Class constructor.

		Parameters
		----------
		args : sequence of arguments, optional
		kwargs : dict of keyword arguments, optional
		"""

		super(HelpForm, self).__init__(*args, **kwargs)

	def get_kwargs(self, table, module, form=None, post_table=True):
		plural_table = get_plural(table).replace('_', ' ')
		table_title = table.title().replace('_', ' ')
		plural_table_title = plural_table.title()
		form_fields = self.keys[table]
		headers = self.table_headers[table]
		post_table = table if post_table else None
		form_caption = '%s Entry Form' % table_title
		heading = 'The %s database' % plural_table
		subheading = (
			'Add %s to the database and see them instantly updated in the lists '
			'below.' % plural_table)

		return {
			'id': table, 'title': plural_table_title, 'heading': heading,
			'subheading': subheading, 'form': form, 'form_caption': form_caption,
			'table_caption': '%s List' % table_title, 'headers': headers,
			'form_fields': form_fields, 'post_location': '%s.add' % module,
			'post_table': post_table}

	def get_choices(self, table, field, order=None, name=None, val=None):
		if (name and val):
			query = {'filters': [{'name': name, 'op': 'in', 'val': val}]}
		else:
			query = None

		result = self.get(table, query)
		values = [x[field] for x in result]
		selection = [x[order] for x in result]
		return zip(values, selection)

	def get_x_choices(self, tables, fields):
		result = self.get(tables[0])
		values = [x[fields[0]] for x in result]
		selection = [x[tables[1]][fields[1]] for x in result]
		return zip(values, selection)

	def get_validators(self, table, field):
		result = self.get(table)
		values = [x[field] for x in result]
		values = sorted(values)

		return [
			Required(), AnyOf(
				values, message=u'Invalid value, must be one of:'
				'%(values)s')]
