from flask.ext.wtf import AnyOf, Required
from app.hermes.models import EventType, Commodity, CommodityType, Exchange
from app.hermes.models import DataSource
from app.cronus.models import Transaction


def get_choices(a_class, value_field, *args, **kwargs):
	order = '%s.%s' % (a_class.__table__, args[0])

	try:
		filter = '%s.%s' % (a_class.__name__, kwargs['column'])
		value = kwargs['value']
		result = a_class.query.filter(eval(filter).in_(value)).order_by(order).all()
	except KeyError:
		result = a_class.query.order_by(order).all()

	values = [getattr(x, value_field) for x in result]
	combo = []

	for arg in args:
		try:
			new = [getattr(getattr(x, arg[0]), arg[1]) for x in result]
		except Exception:
			new = [getattr(x, arg) for x in result]

		combo.append(new)

	try:
		attr = [', '.join(x) for x in zip(combo[0], combo[1])]
	except IndexError:
		attr = combo[0]

	return zip(values, attr)


def get_validators(a_class, value_field):
	result = a_class.query.all()
	values = [getattr(x, value_field) for x in result]
	values = sorted(values)
	return [
		Required(), AnyOf(
			values, message=u'Invalid value, must be one of:'
			'%(values)s')]
