import asyncio
import json
import os
import time
from collections import defaultdict
from aiogram.types import MediaGroup

IsInit = defaultdict(bool)
users = dict()
Album = dict()
AlbumSize = dict()


def init():
    global users
    with open("users.json", "r", encoding="UTF-8") as f:
        users = json.load(f)

    print(users)
'''
    for key in users.keys():
        users[key] = json.loads(users[key])
        IsInit[key] = True
        Album[key] = MediaGroup()
        AlbumSize[key] = 0
'''


async def save_on_time():
    while True:
        await asyncio.sleep(600)
        save()


def save():
    global users
    with open("users.json", "w+", encoding="UTF-8") as f:
        json.dump(users, f, ensure_ascii=False)


def reg_achv(uid, achv):
    if not achv in users[uid]['cachv']:
        users[uid]['cachv'].append(achv)


def init_user(uid, username):
    global users
    if not (uid in users.keys()) or uid==os.getenv("ADMINCHAT"):
        users[uid] = dict()
        users[uid]['last kb'] = 0
        users[uid]['last image'] = 0
        users[uid]['page num'] = 0
        users[uid]['cachv'] = []
        users[uid]['IsBanned'] = False
        users[uid]['IsRegistered'] = False
        users[uid]['achat_username'] = username
        users[uid]['resend_next_message'] = "None"
        users[uid]['awaiting name'] = False
    IsInit[uid] = True
    Album[uid] = MediaGroup()
    AlbumSize[uid] = 0


def register_user(uid, ban):
    users[uid]['IsRegistered'] = True
    users[uid]['IsBanned'] = ban
