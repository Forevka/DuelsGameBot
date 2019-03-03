import random

from duels_api import User
import cfg

me = User(cfg.my_id)
print(me)

members = me.get_self_clan_members()
for player in members:
    print(player)
