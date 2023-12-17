import atexit
import kb
import log
import os
import asyncio
import user
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import CallbackQuery, InputFile, InputMediaPhoto, ContentType, MediaGroup
from dotenv import load_dotenv
from user import init_user, save, IsInit, init
from aiogram.dispatcher import filters

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, loop=asyncio.get_event_loop())
logger = log.create_logger(os.getenv('ADMIN'), bot, dp)
admin = os.getenv('ADMIN')


@dp.message_handler(commands=['start'])
async def on_command_start(message: types.Message):
    uid = str(message.chat.id)
    if not IsInit[uid]:
        init_user(uid, message.from_user.first_name)
    await bot.send_message(uid, "Слева внизу находится кнопка меню."
                                " Там ты сможешь зарегистрироваться, а также найти список достижений для выполнения."
                                "\n\nВ списке ты можешь посмотреть сами задания и сдать их организатору школы. "
                                "\n\nБудет интересно, обещаем!")


@dp.message_handler(commands=['register'])
async def register_new_user(message: types.message):
    uid = str(message.chat.id)
    if not IsInit[uid]:
        init_user(uid, message.from_user.first_name)
    if users[uid]['IsRegistered']:
        return
    users[uid]['awaiting name'] = True
    await bot.send_message(uid, "Пожалуйста, укажи свою фамилию и имя в следующем сообщении")


@dp.message_handler(commands=['getList'])
async def get_achvlist_msg(message: types.message):
    uid = str(message.chat.id)

    if not IsInit[uid]:
        init_user(uid, message.from_user.first_name)

    users[uid]["resend_next_message"] = 'None'
    users[uid]["awaiting name"] = False

    if message.chat.id == admin:
        return
    if not users[uid]['IsRegistered']:
        await bot.send_message(uid, "Пожалуйста, пройдите регистрацию через меню бота")
        return
    if users[uid]['IsBanned']:
        return
    if users[uid]['last kb'] != 0:
        try:
            await bot.delete_message(uid, users[uid]['last kb'])
        except:
            users[uid]['last kb'] = 0
        if users[uid]['last image'] != 0:
            try:
                await bot.delete_message(uid, users[uid]['last image'])
            except:
                users[uid]['last image'] = 0
            users[uid]['last image'] = 0
    users[uid]['last kb'] = (await bot.send_message(uid, "Список достижений:",
                                                    reply_markup=kb.get_achv_list(1, uid,
                                                                                  logger, users))).message_id
    users[uid]['page num'] = 1


@dp.callback_query_handler(text_startswith="achv|")
async def btn(call: types.CallbackQuery):
    message: types.Message = call.message
    uid = str(message.chat.id)
    num = int(call.data.split("|")[1])

    users[uid]["resend_next_message"] = 'None'
    users[uid]["awaiting name"] = False

    txt = kb.achv_text[kb.achv_label[num]]["text"]
    form = kb.achv_text[kb.achv_label[num]]["form"]
    txt += "\n\n"
    txt += "Статус выполнения: " +\
    ("Сдано" if kb.achv_label[num] in users[str(call.from_user.id)]["cachv"] else "Не сдано")
    if form != "None":
        txt += f"\n\nФорма отчета: {form}"
    await message.edit_text(txt)
    await message.edit_reply_markup(kb.get_kb_back(uid, num, users))
    if kb.achv_text[kb.achv_label[num]]['image'] != "None":
        users[uid]['last image'] = (await bot.send_photo(uid,
                                                         InputFile(path_or_bytesio=kb.achv_text[kb.achv_label[num]]['image']),
                                                         reply_to_message_id=message.message_id))\
            .message_id


@dp.callback_query_handler(filters.Text(startswith="admin|"))
async def btn(call: types.CallbackQuery):
    message: types.Message = call.message
    a, b, uid = call.data.split("|")
    b = int(b)
    user.reg_achv(uid, kb.achv_label[b])
    await bot.send_message(uid, "Достижение \"" + kb.achv_label[b] + "\" получено. Поздравляем!")
    await call.message.edit_reply_markup()
    await bot.delete_message(message.chat.id, users[admin]['last kb'])


@dp.callback_query_handler(text="btnback")
async def btnback(call: types.CallbackQuery):
    global users
    message: types.Message = call.message
    uid = str(message.chat.id)
    if users[uid]['last image'] != 0:
        await bot.delete_message(uid, users[uid]['last image'])
        users[uid]['last image'] = 0
    await message.edit_text("Список достижений:")
    await message.edit_reply_markup(kb.get_achv_list(users[uid]['page num'], uid, logger, users))


@dp.callback_query_handler(filters.Text(startswith="complete|"))
async def complete(call: types.CallbackQuery):
    uid = str(call.message.chat.id)
    if users[uid]["IsBanned"]:
        return
    a, b, c = call.data.split("|")
    users[uid]["resend_next_message"] = kb.achv_label[int(b)]
    await call.message.edit_reply_markup()
    await bot.send_message(uid, "Следующее ваше сообщение будет отправлено администратору,"
                                " как доказательство достижения.")


@dp.callback_query_handler(filters.Text(startswith="decachv|"))
async def decline(call: types.CallbackQuery):
    a, b, c = call.data.split("|")
    await bot.send_message(c, f"Достижение \"{kb.achv_label[int(b)]}\" отклонено.")
    await call.message.edit_reply_markup()


@dp.callback_query_handler(filters.Text(startswith="apachv|"))
async def apply(call: types.CallbackQuery):
    a, b, c = call.data.split("|")
    user.reg_achv(c, kb.achv_label[int(b)])
    await bot.send_message(c, f"Достижение \"{kb.achv_label[int(b)]}\" получено.")
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text="back")
async def btn(call: types.callback_query):
    message: types.Message = call.message
    uid = str(message.chat.id)

    try:
        await message.edit_reply_markup(kb.get_achv_list(users[uid]['page num'] - 1, uid, logger, users))
        users[uid]['page num'] -= 1
    except:
        users[uid]['page num'] -= 0


@dp.callback_query_handler(text="next")
async def btn(call: types.callback_query):
    message: types.Message = call.message
    uid = str(message.chat.id)
    await message.edit_reply_markup(kb.get_achv_list(users[uid]['page num'] + 1, uid, logger, users))
    users[uid]['page num'] += 1


@dp.callback_query_handler(text_startswith="adback|")
async def btn(call: types.callback_query):
    message: types.Message = call.message
    uid = call.data.split("|")[1]
    await message.edit_reply_markup(kb.get_admin_achv_kb(users[admin]['page num'] - 1, uid, logger, users))
    users[admin]['page num'] -= 1


@dp.callback_query_handler(text_startswith="adnext|")
async def btn(call: types.callback_query):
    message: types.Message = call.message
    uid = call.data.split("|")[1]
    await message.edit_reply_markup(kb.get_admin_achv_kb(users[admin]['page num'] + 1, uid, logger, users))
    users[admin]['page num'] += 1


@dp.callback_query_handler(text_startswith=["reg", "dec"])
async def regbtn(call: types.CallbackQuery):
    uid = str(call.data.split("|")[1])
    if str(call.data.split("|")[0]) == "dec":
        await bot.send_message(uid, "Заявка на регистрацию отклонена. Попробуйте снова.")
    else:
        user.register_user(uid, False)
        await bot.send_message(uid, "Администратор подтвердил регистрацию")
        await bot.send_message(uid, "Поздравляем, вы получили достижение \"Добро пожаловать\"")
        user.reg_achv(uid, "Добро пожаловать")
    await call.message.edit_reply_markup()


@dp.message_handler(filters.Text(startswith='/change_username'))
async def change_username(message: types.message):
    try:
        if str(message.chat.id) != admin:
            return
        mtext = message.text.split("|")
        uid = mtext[0].split(" ")[1]
        username = mtext[1]
        if not IsInit[uid]:
            await bot.send_message(message.chat.id, "Несуществующий id пользователя")
            return
        users[uid]['achat_username'] = username
        await bot.send_message(message.chat.id, "Успешно")
    except:
        await bot.send_message(message.chat.id, "Не выполнено")


@dp.message_handler(filters.Text(startswith='/ban'))
async def ban(message: types.message):
    try:
        if str(message.chat.id) != admin:
            return
        mtext = message.text.split(" ")
        uid = mtext[1]
        if not IsInit[uid]:
            await bot.send_message(message.chat.id, "Несуществующий id пользователя")
            return
        user.register_user(uid, True)
        await bot.send_message(message.chat.id, f"{users[uid]['achat_username']} заблокирован")
    except:
        await bot.send_message(message.chat.id, "Не выполнено")


@dp.message_handler(filters.Text(startswith='/unban'))
async def unban(message: types.message):
    try:
        if str(message.chat.id) != admin:
            return
        mtext = message.text.split(" ")
        uid = mtext[1]
        if not IsInit[uid]:
            await bot.send_message(message.chat.id, "Несуществующий id пользователя")
            return
        user.register_user(uid, False)
        await bot.send_message(message.chat.id, f"{users[uid]['achat_username']} разблокирован")
    except:
        await bot.send_message(message.chat.id, "Не выполнено")


@dp.message_handler(filters.Text(startswith='/give'))
async def give(message: types.message):
    try:
        if str(message.chat.id) != admin:
            return
        mtext = message.text.split(" ")
        uid = admin
        targetid = mtext[1]
        if not IsInit[uid]:
            await bot.send_message(message.chat.id, "Несуществующий id пользователя")
            return
        if users[uid]['last kb'] != 0:
            try:
                await bot.delete_message(uid, users[uid]['last kb'])
            except:
                users[uid]['last kb'] = 0
        users[uid]['last kb'] = (await bot.send_message(message.chat.id, f"Выберите достижение:",
                                                        reply_markup=kb.get_admin_achv_kb(1, targetid, logger, users))).message_id
        users[uid]['page num'] = 1
    except:
        await bot.send_message(message.chat.id, "Не выполнено")


@dp.message_handler(commands='get_user_list')
async def get_user_list(message: types.message):
    if str(message.chat.id) != admin:
        return
    ans = str()
    for key in users.keys():
        username = users[key]['achat_username']
        cachv = users[key]['cachv']
        banned = users[key]['IsBanned']
        ans += f"{username}: id = {key}\nЗабанен: {banned}\nВыполненные достижения:{cachv}\n--------------------\n"
        if len(ans) > 2048:
            await bot.send_message(message.chat.id, ans)
            ans = ""
    if len(ans) > 0:
        await bot.send_message(message.chat.id, ans)


@dp.message_handler(commands='help')
async def get_user_list(message: types.message):
    if str(message.chat.id) != admin:
        return
    helpm = "/top num - вывести топ num пользователей по достижениям\n"\
            "/get_user_list - получить список пользователей(имена, айди, список ачивок)\n" \
            "/help - помощь\n" \
            "/ban id - заблокировать пользователя с указанным id(можете в get_user_list посмотреть)\n" \
            "/unban id - разблокировать по id\n" \
            "/change_username id|*новое имя* - изменить отображаемое имя\n" \
            "/give id - Выдать достижение\n"
    await bot.send_message(message.chat.id, helpm)


@dp.message_handler(content_types=ContentType.PHOTO)
async def resend(message: types.Message):
    uid = str(message.chat.id)
    if not IsInit[uid]:
        return
    if users[uid]["IsBanned"]:
        return
    if users[uid]["resend_next_message"] != "None":
        username = users[uid]["achat_username"]
        achievement = users[uid]["resend_next_message"]
        if user.AlbumSize[uid] >= 10:
            return
        user.Album[uid].attach_photo(photo=message.photo[0].file_id, caption=message.caption)
        user.AlbumSize[uid] += 1
        num = user.AlbumSize[uid]
        await asyncio.sleep(5)
        if num == 1:
            await bot.send_message(admin, f"Пользователь {username} сдает достижение {achievement}",
                               reply_markup=kb.get_achv_admin_kb(uid, kb.achv_label.index(achievement)))
            await bot.send_media_group(admin, media=user.Album[uid])
            await bot.send_message(uid, "Достижение принято на рассмотрение")
            users[uid]["resend_next_message"] = 'None'
            user.Album[uid] = MediaGroup()
            user.AlbumSize[uid] = 0


@dp.message_handler(content_types=ContentType.VIDEO)
async def resend(message: types.Message):
    uid = str(message.chat.id)
    if not IsInit[uid]:
        return
    if users[uid]["IsBanned"]:
        return
    if users[uid]["resend_next_message"] != "None":
        username = users[uid]["achat_username"]
        achievement = users[uid]["resend_next_message"]
        if user.AlbumSize[uid] >= 10:
            return
        user.Album[uid].attach_video(video=message.video.file_id, caption=message.caption)
        user.AlbumSize[uid] += 1
        num = user.AlbumSize[uid]
        await asyncio.sleep(5)
        if num == 1:
            await bot.send_message(admin, f"Пользователь {username} сдает достижение {achievement}",
                               reply_markup=kb.get_achv_admin_kb(uid, kb.achv_label.index(achievement)))
            await bot.send_media_group(admin, media=user.Album[uid])
            await bot.send_message(uid, "Достижение принято на рассмотрение")
            users[uid]["resend_next_message"] = 'None'
            user.Album[uid] = MediaGroup()
            user.AlbumSize[uid] = 0


@dp.message_handler(commands='top')
async def top(message: types.Message):
    if str(message.chat.id) != admin:
        return
    try:
        num = int(message.text.split()[1])
    except:
        num = 1000000

    u = list()
    for user in users.values():
        u.append(list((len(user['cachv']), user['achat_username'])))
    u = sorted(u, key=lambda x: x[0], reverse=True)
    tmp = ""
    place = 1
    for i in range(len(u)):
        tmp += f"{place}. {u[i][1]}: {u[i][0]} достижение(й)\n"
        place += 1
        if i != len(u) - 1 and u[i][0] == u[i + 1][0]:
            place -= 1
        if place > num:
            break
    await bot.send_message(admin, tmp)


@dp.message_handler(text_startswith='/send_to_all')
async def mes_to_all(message: types.Message):
    if str(message.chat.id) != admin:
        return

    mes = message.text.split('"')[1]
    for key in users.keys():
        if users[key]['IsRegistered']:
            await bot.send_message(key, mes)


@dp.message_handler(content_types=['any'])
async def resend(message: types.Message):
    uid = str(message.chat.id)
    if not IsInit[uid]:
        init_user(uid, message.from_user.first_name)
        return
    if users[uid]["IsBanned"]:
        return
    if users[uid]["resend_next_message"] != "None":
        username = users[uid]["achat_username"]
        achievement = users[uid]["resend_next_message"]
        users[uid]["resend_next_message"] = 'None'
        await bot.send_message(admin, f"Пользователь {username} сдает достижение {achievement}",
                               reply_markup=kb.get_achv_admin_kb(uid, kb.achv_label.index(achievement)))
        await message.send_copy(admin)
        await bot.send_message(uid, "Достижение принято на рассмотрение")
        return
    if users[uid]["awaiting name"]:
        users[uid]['achat_username'] = message.text
        await bot.send_message(admin,
                               f"Пользователь {users[uid]['achat_username']} просит разрешения на регистрацию",
                               reply_markup=kb.reg_admin_kb(message.from_user.id))
        users[uid]["awaiting name"] = False
        return
    if uid == admin:
        return
    await bot.send_message(uid, "Сообщение не распознано")


if __name__ == '__main__':
    atexit.register(save)
    init()
    users = user.users
    init_user(admin, "ADMIN")
    dp.loop.create_task(user.save_on_time())
    executor.start_polling(dp)
