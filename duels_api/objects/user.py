import requests
import json
import random
import logging

from duels_api.settings import api_url, headers
import duels_api

class User():
    def __init__(self, id, clan = None, log=None):
        if log is None:
            self.log = logging.getLogger("Clan")
            self.log.setLevel(logging.DEBUG)
        else:
            self.log = log
        self.id = id
        self.name = ''
        self.parts = []
        self.division = ''
        self.clan_id = ''

        self.clan = clan

        self.keys_amount = 0
        self.hp = 0
        self.attack = 0

        self.group_id = ''
        self.group_players = []

        self.get_me()

    def get_user(self, user_id: str) -> dict:
        data = '{"playerId":"'+user_id+'","id":"'+self.id+'"}'
        r = requests.post(api_url.format('profiles/details'), headers=headers, data=data)
        j = json.loads(r.text)
        player = j.get('player', None);

        return player

    def get_me(self) -> bool:
        player = self.get_user(self.id)
        if player is not None:
            self.id = player.get('_id', None)
            self.name = player.get('name', None)
            self.division = player.get('division', None)
            self.clan_id = player.get('clanId', None)

            #if self.clan is None:
            #    self.clan = self.get_clan()#Clan(self.clan_id, self.id, self.log)

            self.parts = player.get('character', None).get('parts', None)
            for part in self.parts:
                if part['stat']['info']=='Health':
                    self.hp += int(part['stat']['value'])
                elif part['stat']['info']=='Attack':
                    self.attack += int(part['stat']['value'])

        return True

    def get_clan(self):
        if self.clan_id is not None:
            return duels_api.Clan(self.clan_id, self.id, self.log)
        else:
            return None

    def leave_clan(self):
        data = '{"id":"'+self.id+'"}'

        r = requests.post(api_url.format('clan/leave'), headers=headers, data=data)
        j = json.loads(r.text)
        self.log.debug("{} Leave clan".format(self.name))
        return j.get('error', True)

    def join_clan(self, clan_id: str) -> bool:
        data = '{"clanId":"'+str(clan_id)+'","id":"'+str(self.id)+'"}'

        r = requests.post(api_url.format('clans/join'), headers=headers, data=data)
        j = json.loads(r.text)
        self.log.debug("{} Join clan {}".format(self.name, clan_id))
        return j.get('error', True)

    def get_self_clan_members(self):
        clan = self.get_clan()
        if clan is not None:
            return clan.get_members()
            #for player in clan.get('members', []):
            #    yield User(player['id'], log)

    def claim_reward(self, claim_id: str) -> bool:
        data = '{"containerId":"'+str(claim_id)+'","id":"'+str(self.id)+'"}'

        r = requests.post(api_url.format('queue/claim'), headers=headers, data=data)
        j = json.loads(r.text)
        if j.get('error', True) is True:
            return True
        else:
            return False

    def get_special_crate(self):
        data = '{"info":"SpecialCrate1","id":"'+str(self.id)+'"}'

        r = requests.post(api_url.format('crates/buy'), headers=headers, data=data)
        j = json.loads(r.text)
        if j.get('error', True) is True:
            if self.claim_reward(j['_q'][0]['_id']):
                for i in j['_q'][0]['steps'][0]['crate']['rewards']:
                    item = i['reward']
                    yield Item(item['__id'], self.id, item['__type'], item['rarity'], item['stat']['info'], item['stat']['value'])
            else:
                return []
        else:
            return []

    def write_to_clan_chat(self, text: str) -> bool:
        data = '{"msg":"'+str(text)+'","id":"'+str(self.id)+'"}';

        r = requests.post(api_url.format('clan/write'), headers=headers, data=data)
        r = json.loads(r.text)

        return r.get('success', False)

    def get_self_opponent_clan(self) -> str:
        clan = self.get_clan()
        if clan is not None:
            return clan.get_opponent_clan(self.clan_id, self.id)


    def search_clans(self) -> list:
        data = '{"id":"'+str(self.id)+'"}'

        r = requests.post(api_url.format('clans/search'), headers=headers, data=data)
        j = json.loads(r.text)
        clans = []
        for i in j['clans']:
            yield duels_api.Clan(i['_id'], self.id, self.log)



    def ranked_battle(self, enemy_id: str, group_id: str) -> bool:
        data = '{"enemyId":"'+str(enemy_id)+'","groupId":"'+str(group_id)+'","id":"'+str(self.id)+'"}'

        r = requests.post(api_url.format('battle/ranked'), headers=headers, data=data)
        j = json.loads(r.text)
        return j.get('result', False)


    def set_ranked_group_info(self) -> bool:
        data = '{"id":"'+self.id+'"}'
        r = requests.post(api_url.format('ranking/group'), headers=headers, data=data)
        j = json.loads(r.text)
        try:
            self.group_id = j['group']['_id']
            self.group_players = [i['pid'] for i in j['group']['members'] if i.get("pid") is not None]
            self.group_players.remove(self.id)
        except Exception as e:
            print(self)
            print(j)
            print(e)

        return True

    def get_ranked_claim_id(self):
        data = '{"id":"'+str(self.id)+'"}'

        r = requests.post(api_url.format('ranking/group'), headers=headers, data=data)
        j = json.loads(r.text)
        #print('claim id', j)
        j = j.get('_q')
        if j is not None:
            return j[0]['_id']
        else:
            return None

    def ranked_battle(self, enemy_id: str) -> bool:
        data = '{"enemyId":"'+str(enemy_id)+'","groupId":"'+str(self.group_id)+'","id":"'+str(self.id)+'"}'

        r = requests.post(api_url.format('battle/ranked'), headers=headers, data=data)
        j = json.loads(r.text)
        return j.get('result', False)

    def clan_battle(self) -> int:
        self.log.debug("clan battle {}".format(self.name))
        data = '{"id":"'+str(self.id)+'"}'

        r = requests.post(api_url.format('clan/war/battle'), headers=headers, data=data)
        j = json.loads(r.text)
        #print(j)
        if j.get('error', None) is not None:
            return -1
        else:
            return j['battle']['result']

    def claim_reward_group(self):
        claim_id = self.get_ranked_claim_id()
        #print('claim id', claim_id, self)
        if claim_id is not None:
            data = '{"containerId":"'+str(claim_id)+'","id":"'+str(self.id)+'"}'

            r = requests.post(api_url.format('queue/claim'), headers=headers, data=data)
            j = json.loads(r.text)
            self.log.debug("Claim reward {} - keys: {}".format(self.name, j['_u']['Key@Value']))
            return j['_u']['Key@Value']
        else:
            self.log.debug("Cant get reward for ranked battle {}".format(self.name))
            return -2

    def get_defeated_clan_opponent(self) -> int:
        data = '{"chat":false,"id":"'+self.id+'"}'

        r = requests.post(api_url.format('clan'), headers=headers, data=data)
        j = json.loads(r.text)
        #print(j)
        j = j['clan']['war'].get('war', None)
        if j is not None:
            return j['defeatedOpponents']
        else:
            return 10

    def defeat_ranked_group(self) -> int:
        self.set_ranked_group_info()
        if len(self.group_players)>=15:
            for i in self.group_players:
                count = 0
                result = self.ranked_battle(i)
                while(result!=True and count<=50):
                    result = self.ranked_battle(i)
                    count+=1
                if result!=True:
                    player = User(i, self.log)
                    self.log.debug("Start working as {}".format(player.name))
                    player.defeat_ranked_group()
                else:
                    self.log.debug("{} beated {}".format(self.name, i))
            return self.claim_reward_group()
        else:
            self.log.debug("Not enough player in group {}".format(self.name))
            return -1 #not enough players in ranked group

    def get_stats(self) -> tuple:
        return self.hp, self.attack

    def __eq__(self, other) -> bool:
        if isinstance(other, User):
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

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return 'User ID: {} Name: {} Division: {} Clan ID: {} HP: {} Attack: {}'.format(self.id,
                                                self.name, self.division, self.clan_id,
                                                self.hp, self.attack)
