import requests
import json

api_url = 'http://api-duels-test.galapagosgames.com/{}'

headers = {
    'Expect': '100-continue',
    'Content-Type': 'application/json',
    'X-Unity-Version': '2018.2.14f1',
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.0; BV6000 Build/NRD90M)',
    'Host': 'api-duels-test.galapagosgames.com',
}

def getKey(obj):
    return obj.get_stats()

def load_users(file = 'users.json'):
    l = []
    try:
        with open(file, 'r', encoding = 'utf8') as f:
            l = json.loads(f.read())
    except FileNotFoundError:
        pass

    return l

def make_request(path, data, api_url = api_url):
    r = requests.post(api_url.format(path), headers=headers, data=data)
    j = json.loads(r.text)
    if j.get('error', True) is True:
        return j
    else:
        return None
