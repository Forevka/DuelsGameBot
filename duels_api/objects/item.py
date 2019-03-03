import requests
import json
import random
import logging

from duels_api.settings import api_url, headers
import duels_api

class Item():
    def __init__(self, id:str, owner_id: str, type: str, rarity: str, info: str, value: int, log = None):
        self.id = id
        self.owner_id = owner_id

        self.type = type
        self.rarity = rarity

        self.hp = 0
        self.attack = 0

        if log is None:
            self.log = logging.getLogger("Item")
            self.log.setLevel(logging.DEBUG)
        else:
            self.log = log

        if info == 'Attack':
            self.attack = value
        elif info == 'Health':
            self.hp = value

    def dissasemble(self):
        data = '{"partId":"'+str(self.id)+'","id":"'+str(self.owner_id)+'"}'

        r = requests.post(api_url.format('inventory/disassemble'), headers=headers, data=data)
        j = json.loads(r.text)

        if j.get('error', True) is True:
            self.log.debug("{} Dissasemble item".format(self.id))
            return True
        else:
            self.log.debug("{} Can`t dissasemble".format(self.id))
            return False

    def equip(self):
        data = '{"partId":"'+str(self.id)+'","id":"'+str(self.owner_id)+'"}'

        r = requests.post(api_url.format('inventory/equip'), headers=headers, data=data)
        j = json.loads(r.text)

        if j.get('error', True) is True:
            self.log.debug("{} Equiped item".format(self.id))
            return True
        else:
            self.log.debug("{} Can`t equip".format(self.id))
            return False

    def __str__(self):
        return 'Item ID: {} Owner: {} Rarity: {} Attack: {} HP: {}'.format(self.id,
                            self.owner_id, self.rarity, self.attack, self.hp)
