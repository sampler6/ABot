from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import json

with open("achvlist.txt", encoding="utf-8") as f:
    achv_label = f.readlines()
    for i in range(len(achv_label)):
        achv_label[i] = achv_label[i].replace("\n", "")
with open("achivlist.json", encoding="utf-8") as f:
    achv_text = json.load(f)


def get_kb_back(uid, lbl, users):
    kbback = InlineKeyboardMarkup(row_width=1)
    kbback.insert(InlineKeyboardButton(text="<--", callback_data="btnback"))
    if not (achv_label[lbl] in users[uid]['cachv']):
        kbback.insert(InlineKeyboardButton(text="Сдать задание", callback_data="complete|" + str(lbl) + "|" + uid))
    return kbback


def get_achv_list(num, uid, logger, users):
    ikb = InlineKeyboardMarkup(row_width=1)
    for i in range((num-1)*8, min(num*8, len(achv_label))):
        btext = achv_label[i]
        try:
            if achv_label[i] in users[uid]['cachv']:
                btext += " ✓"
            else:
                btext += " ☓"
        except:
            logger.warning('cachv error', extra={"username": users[uid]['achat_username'], "messagetext": "None"})
            btext += " ☓"

        ikb.insert(InlineKeyboardButton(text=btext, callback_data="achv|" + str(i)))
    if num*8 >= len(achv_label):
        ikb.insert(InlineKeyboardButton(text="<--", callback_data="back"))
    elif num == 1:
        ikb.insert(InlineKeyboardButton(text="-->", callback_data="next"))
    else:
        ikb.row(InlineKeyboardButton(text="<--", callback_data="back"),
                InlineKeyboardButton(text="-->", callback_data="next"))
    return ikb


def get_admin_achv_kb(num, uid, logger, users):
    ikb = InlineKeyboardMarkup(row_width=1)
    print(num, uid)
    for i in range((num-1)*8, min(num*8, len(achv_label))):
        btext = achv_label[i]
        try:
            if achv_label[i] in users[uid]['cachv']:
                btext += " ✓"
            else:
                btext += " ☓"
        except:
            logger.warning('cachv error', extra={"username": users[uid]['achat_username'], "messagetext": "None"})
            btext += " ☓"
        ikb.insert(InlineKeyboardButton(text=btext, callback_data="admin|" + str(i) + "|" + str(uid)))
    if num*8 >= len(achv_label):
        ikb.insert(InlineKeyboardButton(text="<--", callback_data="adback" + "|" + str(uid)))
    elif num == 1:
        ikb.insert(InlineKeyboardButton(text="-->", callback_data="adnext" + "|" + str(uid)))
    else:
        ikb.row(InlineKeyboardButton(text="<--", callback_data="adback" + "|" + str(uid)),
                InlineKeyboardButton(text="-->", callback_data="adnext" + "|" + str(uid)))
    return ikb


def get_achv_admin_kb(uid, achv):
    achv_admin_kb = InlineKeyboardMarkup()
    achv_admin_kb.row(
        InlineKeyboardButton(text="✓", callback_data="apachv|" + str(achv) + "|" + uid),
        InlineKeyboardButton(text="☓", callback_data="decachv|" + str(achv) + "|" + uid),
    )
    return achv_admin_kb


def reg_admin_kb(uid):
    admin_kb = InlineKeyboardMarkup(row_width=1)
    admin_kb.insert(InlineKeyboardButton(text="Зарегистрировать", callback_data="reg|" + str(uid)))
    admin_kb.insert(InlineKeyboardButton(text="Отклонить", callback_data="dec|" + str(uid)))
    return admin_kb
