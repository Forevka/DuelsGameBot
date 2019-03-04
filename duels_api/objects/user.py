import json
import logging
from uuid import uuid4

import duels_api
from duels_api.settings import make_request


class User():
    def __init__(self, id = None, clan = None, log=None):
        if log is None:
            self.log = logging.getLogger("User")
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

        self._get_me()

    def _get_user(self, user_id: str) -> dict:
        data = '{"playerId":"'+user_id+'","id":"'+self.id+'"}'
        j = make_request('profiles/details', data=data)

        if j:
            return j.get('player', None)
        else:
            return None

    def _create_user(self) -> bool:
        data = '{"ids":["'+str(uuid4())+'"],"appBundle":"com.deemedyainc.duels","appVersion":"0.6.6","platform":"Android"}'
        j = make_request('general/login', data=data)

        return j['profile']['_id']

    def _get_me(self) -> bool:
        if self.id is None:
            self.id =  self._create_user()
            self.log.debug("Creating new user with id {}".format(self.id))
        player = self._get_user(self.id)
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

    def leave_clan(self) -> bool:
        data = '{"id":"'+self.id+'"}'
        j = make_request('clan/leave', data=data)

        if j:
            self.log.debug("{} Leave clan".format(self.name))
            return True
        else:
            self.log.debug("{} Cant leave clan".format(self.name))
            return False

    def join_clan(self, clan_id: str) -> bool:
        data = '{"clanId":"'+str(clan_id)+'","id":"'+str(self.id)+'"}'
        j = make_request('clans/join', data=data)

        if j:
            self.log.debug("{} Join clan {}".format(self.name, clan_id))
            return True
        else:
            self.log.debug("{} Cant join clan {}".format(self.name, clan_id))
            return False

    def get_self_clan_members(self) -> list:
        clan = self.get_clan()
        if clan is not None:
            return clan.get_members()

    def claim_reward(self, claim_id: str) -> bool:
        data = '{"containerId":"'+str(claim_id)+'","id":"'+str(self.id)+'"}'
        j = make_request('queue/claim', data=data)

        if j:
            self.log.debug("{} Claimed reward".format(self.id))
            return True
        else:
            self.log.debug("{} Cant claimed reward".format(self.id))
            return False

    def get_special_crate(self) -> list:
        data = '{"info":"SpecialCrate1","id":"'+str(self.id)+'"}'
        j = make_request('crates/buy', data=data)

        if j:
            self.log.debug("{} Special crate".format(self.id))
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
        j = make_request('clan/write', data=data)

        if j:
            return True#r.get('success', False)
        else:
            return False

    def get_self_opponent_clan(self) -> str:
        clan = self.get_clan()

        if clan is not None:
            return clan.get_opponent_clan(self.clan_id, self.id)


    def search_clans(self) -> list:
        data = '{"id":"'+str(self.id)+'"}'
        j = make_request('clans/search', data=data)

        if j:
            for i in j['clans']:
                yield duels_api.Clan(i['_id'], self.id, self.log)
        else:
            return []

    def set_ranked_group_info(self) -> bool:
        data = '{"id":"'+self.id+'"}'
        j = make_request('ranking/group', data=data)

        if j:
            try:
                self.group_id = j['group']['_id']
                self.group_players = [i['pid'] for i in j['group']['members'] if i.get("pid") is not None]
                self.group_players.remove(self.id)
            except Exception as e:
                print(self)
                print(j)
                print(e)

            return True
        else:
            return False

    def get_ranked_claim_id(self) -> str:
        data = '{"id":"'+str(self.id)+'"}'
        j = make_request('ranking/group', data=data)

        if j:
            j = j.get('_q')
            if j is not None:
                return j[0]['_id']
            else:
                return None
        else:
            return None

    def ranked_battle(self, enemy_id: str) -> bool:
        data = '{"enemyId":"'+str(enemy_id)+'","groupId":"'+str(self.group_id)+'","id":"'+str(self.id)+'"}'
        j = make_request('battle/ranked', data=data)

        if j:
            return True
        else:
            return False

    def clan_battle(self) -> int:
        if self.get_defeated_clan_opponent()<10:
            self.log.debug("clan battle {}".format(self.name))
            data = '{"id":"'+str(self.id)+'"}'
            j = make_request('clan/war/battle', data=data)

            if j:
                return j['battle']['result']
            else:
                return -1
        else:
            return -2

    def claim_reward_group(self) -> int:
        claim_id = self.get_ranked_claim_id()
        if claim_id is not None:
            data = '{"containerId":"'+str(claim_id)+'","id":"'+str(self.id)+'"}'
            j = make_request('queue/claim', data=data)

            if j:
                self.log.debug("Claim reward {} - keys: {}".format(self.name, j['_u']['Key@Value']))
                return j['_u']['Key@Value']
            else:
                return -1
        else:
            self.log.debug("Cant get reward for ranked battle {}".format(self.name))
            return -2

    def get_defeated_clan_opponent(self) -> int:
        data = '{"chat":false,"id":"'+self.id+'"}'
        j = make_request('clan', data=data)

        if j:
            j = j['clan']['war'].get('war', None)
            if j is not None:
                return j['defeatedOpponents']
            else:
                return 10
        else:
            return -1

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
                    player = User(i)
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

    def save(self, file = 'users.json') -> bool:
        l = []
        try:
            with open(file, 'r', encoding = 'utf8') as f:
                l = json.loads(f.read())
        except FileNotFoundError:
            pass

        l.append(self.id)


        with open(file, 'w', encoding = 'utf8') as f:
            f.write(json.dumps(l)+'\n')

        return True

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
