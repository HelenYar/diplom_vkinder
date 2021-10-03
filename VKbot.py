from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import re
from config import token, bot_id
from VK import Vk
from sql_db import sql
import sys

class Vkinder:
    def __init__(self, token):
        self.vk = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk)

    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def greetings_msg(self):
        text = 'Привет, хочешь найти себе пару? \n' \
               'Напиши  OK чтобы начать\n' \
               'Далее следуй по инструкции!'
        return text
    s = sql()
    s.create_table()

    def start_bot(self):
        step_action = 0
        s = sql()
        s.create_table()

        for event in self.longpoll.listen():
            if event.type != VkEventType.MESSAGE_NEW:
                continue
            if not event.to_me:
                continue
            if not event.from_user:
                continue

            user_id = event.user_id
            user_msg = event.message.lower()

            if step_action == 0:
                self.write_msg(user_id, self.greetings_msg())
                step_action += 1

            if step_action == 1:
                if user_msg == "ок":
                    self.write_msg(user_id,
                                    f'Чтобы начать обработу, Вам нужно передай мне токен, для доступа к приложению\n'
                                    'для этого перейдите по ссылке ниже, скопируйте токе из адресной строки и вставь его в ответ полностью\n'
                                    f'https://oauth.vk.com/authorize?client_id={bot_id}&display=page&scope=stats'
                                    '.photos.offline&response_type=token&v=5.130')
                    step_action += 1

            if step_action == 2:
                user_msg = re.findall(r"access_token=(.{85})", user_msg)
                if not user_msg:
                    continue
                if len(user_msg[0]) != 85:
                    continue
                token_user = user_msg[0]
                self.write_msg(user_id, 'Токен принят\n'
                                'Если вы ищете человека примерно своего возраста и из вашего города, то введите "Готово"\n')
                                #'Если хотите уточнить параметры поиска то введите данные в одну строку в формате:\n'
                                #'пол / возраст / семейное положение / город предполагаемого партнера\n ')

                vk = Vk(token_user, user_id)
                step_action += 1
                user_msg = ""

            if step_action == 3:
                if user_msg.lower() == 'готово':
                    vk.get_photos()
                    self.write_msg(user_id, 'Ищем пару ')
                    s = sql()
                    self.write_msg(user_id, f"{s.itog_msg()}")
                    self.write_msg(user_id, 'Для выхода  введите : Выход ')
                    step_action += 1

            if step_action == 4:
                if user_msg == 'выход':
                    self.write_msg(user_id, 'Пока')
                    s = sql()
                    s.clean_table()
                    sys.exit()



if __name__ == '__main__':
    vkbot = Vkinder(token=token)
    vkbot.start_bot()
