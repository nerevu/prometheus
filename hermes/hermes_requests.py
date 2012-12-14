# new event w embedded type
import json
import requests
newevent = {'symbol': 'ISIS', 'type': {'name': 'Dividend', 'unit': 'USD'}, 'value': 100}
r = requests.post('http://127.0.0.1:5000/api/event', data=json.dumps(newevent), headers={'content-type': 'application/json'})
r.status_code, r.headers['content-type'], r.json
# new event
newevent = {'symbol': 'ISIS', 'date': '1/22/12', 'type_id': 1, 'value': 100}
r = requests.post('http://127.0.0.1:5000/api/event', data=json.dumps(newevent), headers={'content-type': 'application/json'})
r.status_code, r.headers['content-type'], r.json
# new event type
neweventtype = {'name': 'Split', 'unit': 'Multiplier'}
r = requests.post('http://127.0.0.1:5000/api/type', data=json.dumps(neweventtype), headers={'content-type': 'application/json'})
r.status_code, r.headers['content-type'], r.json
# delete event
r = requests.delete('http://127.0.0.1:5000/api/event/1', headers={'content-type': 'application/json'})
r.status_code, r.headers['content-type'], r.json
# get event
r = requests.get('http://127.0.0.1:5000/api/type/1', headers={'content-type': 'application/json'})
newid = r.json['id']
r = requests.get('http://127.0.0.1:5000/api/type/%s' % newid, headers={'content-type': 'application/json'})
r.status_code, r.headers['content-type']
r.json
