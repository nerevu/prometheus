import json
import requests
patch = {'type': {'add': {'name': 'Dividend', 'unit': 'USD'}}}
headers={'content-type': 'application/json'}
site='http://127.0.0.1:5000/api'

patch = {'type': {'add': {'id': 2}}}
r = requests.put('%s/hermes_event/2' % site, data=json.dumps(patch), headers=headers)
r.status_code, r.headers['content-type'], r.json

newevent = {'symbol': 'ISIS', 'type': {'name': 'Dividend', 'unit': 'USD'}, 'value': 100}
r = requests.post('%s/event' % site, data=json.dumps(newevent), headers=headers)
r.status_code, r.headers['content-type'], r.json

newevent = {'symbol': 'ISIS', 'date': '1/22/12', 'type': {'id': 2}, 'value': 100}
r = requests.post('%s/event' % site, data=json.dumps(newevent), headers=headers)
r.status_code, r.headers['content-type'], r.json

neweventtype = {'name': 'Split', 'unit': 'Multiplier'}
r = requests.post('%s/type' % site, data=json.dumps(neweventtype), headers=headers)
r.status_code, r.headers['content-type'], r.json

r = requests.delete('%s/type/1' % site, headers=headers)
r.status_code, r.headers['content-type'], r.json

r = requests.get('%s/type/1', headers=headers)
newid = r.json['id']
r = requests.get('%s/type/%s' % (site, newid), headers=headers)
r.status_code, r.headers['content-type']
r.json
