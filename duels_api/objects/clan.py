import json
import random
import logging

import duels_api
from duels_api.settings import make_request


class Clan():
    def __init__(self, clan_id: str, user_id: str, log = None):
        self.id = clan_id
        self.name = ''
        self.description = ''
        self.clan_info = {}
        self.owner_id = user_id
        if log is None:
            self.log = logging.getLogger("Clan")
            self.log.setLevel(logging.DEBUG)
        else:
            self.log = log

        self._get_owner()


    def get_me(self):
        data = '{"clanId":"'+str(self.id)+'","id":"'+str(self.owner_id)+'"}'
        j = make_request('clan/info', data)

        if j:
            return j
        else:
            return None

    def get_more_info(self):
        data = '{"chat":false,"id":"'+self.owner_id+'"}'
        j = make_request('clan', data)

        if j:
            return j['clan']
        else:
            return None

    def _get_owner(self):
        self.clan_info = self.get_me()
        if self.clan_info is not None:
            self.name = self.clan_info['name']

            for i in self.clan_info['members']:
                if i['role']=='Leader':
                    self.owner_id = i['id']
        else:
            return None

    def get_opponent_clan(self):
        self.clan_info = self.get_more_info()
        war = self.clan_info['war'].get('warDescription')

        if war is not None:
            return Clan(war['opponentClan']['_id'], self.owner_id, self.log)

    def get_members(self) -> list:
        self.clan_info = self.get_me()

        for player in self.clan_info.get('members', []):
            yield duels_api.User(player['id'], self.log)

    def edit_description(self, clan_name: str = '', description: str = '') -> bool:
        data = '{"name":"'+(clan_name.encode('utf-8').decode('latin-1') if clan_name!='' else self.name.encode('utf-8').decode('latin-1'))+'","countryInfo":"UA","description":"'+(description.encode('utf-8').decode('latin-1') if description!='' else self.description.encode('utf-8').decode('latin-1'))+'","badge":{"backInfo":"ClanBadgeBackground001","backColor":"F04E0D","iconInfo":"ClanBadgeIcon009","iconColor":"FFFFFF"},"id":"'+str(self.owner_id)+'"}'
        j = make_request('clan/edit', data)

        return True if j.get('error', True) is True else False

    def get_leader(self):
        return duels_api.User(self.owner_id, clan = self)

    def __eq__(self, other) -> bool:
        if isinstance(other, Clan):
            if other.id == self.id:
                return True
            else:
                return False
        elif isinstance(other, str):
            if other == self.id:
                return True
            else:
                return False
        else:
            return False

    def __str__(self) -> str:
        return 'Clan ID: {} Name: {}'.format(self.id, self.name)
