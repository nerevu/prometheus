from hermes.forms import EventForm, EventTypeForm, PriceForm, CommodityForm
from cronus.forms import TransactionForm


def get_plural(word):
	if word[-1] == 'y':
		return word[:-1] + 'ies'
	else:
		return word + 's'


def get_kwargs(table, module, conn, post_table=True):
	plural_table = get_plural(table).replace('_', ' ')
	table_as_class = table.title().replace('_', '')
	table_title = table.title().replace('_', ' ')
	plural_table_title = plural_table.title()
	form_fields, table_headers, results, keys = getattr(conn, table)
	rows = conn.values(results, keys)

	post_table = table if post_table else None
	form_caption = '%s Entry Form' % table_title
	heading = 'The %s database' % plural_table
	subheading = (
		'Add %s to the database and see them instantly updated in the lists '
		'below.' % plural_table)

	try:
		form = eval('%sForm.new()' % table_as_class)
	except AttributeError:
		form = eval('%sForm()' % table_as_class)

	return {
		'id': table, 'title': plural_table_title, 'heading': heading,
		'subheading': subheading, 'rows': rows, 'form': form,
		'form_caption': form_caption, 'table_caption': '%s List' % table_title,
		'table_headers': table_headers, 'form_fields': form_fields,
		'post_location': '%s.add' % module, 'post_table': post_table}
