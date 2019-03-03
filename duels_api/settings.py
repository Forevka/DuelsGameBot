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
