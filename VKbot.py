from random import randrange
import sqlalchemy
import sys
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import token, token_user, sql_name
from VK import Vk
from sql_db import clean_table
import os

class Vkinder:
    i = 1

    def __init__(self, token):
        self.vk = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk)


    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def start_bot(self, session_maker):
        step_action = 0
        user_data = 0
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
                self.write_msg(user_id, 'Привет, хочешь найти себе пару? \n'
                                        'Напиши  OK чтобы начать\n'
                                        'Далее следуй по инструкции!')
                step_action += 1

            if step_action == 1:
                if user_msg == "ок":
                    self.write_msg(user_id, 'Если вы ищете человека примерно своего возраста и из вашего города,'
                                            ' то введите "Готово"\n')
                    vk = Vk(token_user, user_id)
                    step_action += 1
                user_msg = ""

            if step_action == 2:
                if user_msg.lower() == 'готово':
                    user_data = vk.get_user()
                    if user_data[0]['user_city_id'] == 0:
                        self.write_msg(user_id, 'В вашем профиле не указан город\n'
                                                'Введите название, например Москва\n')
                        user_msg = "нет города"
                        step_action -= 1
                    step_action += 2

            if step_action == 3:
                if user_msg != 'нет города':
                    city_t = user_msg.title()
                    city_i = vk.get_city_msg(city_t)
                    v = vk
                    v.update_user(city_i, city_t)
                    user_msg = "*"
                    step_action += 1

            if step_action == 4:
                if user_msg.lower() == 'готово' or user_msg.lower() == '*':

                    if user_data[0]['user_age'] == 0:
                        self.write_msg(user_id, 'В вашем профиле не указан возраст\n'
                                                'Введите его, например 18\n')
                        user_msg = "нет возраста"
                        step_action -= 1
                    step_action += 2

            if step_action == 5:
                if user_msg != "нет возраста":
                    age_ = int(user_msg)
                    vk.update_user_a(age_)
                    step_action += 1

            if step_action == 6:
                i = self.i
                msg = vk.itog_msg(session_maker, i)
                self.write_msg(user_id, f"{msg}")
                self.write_msg(user_id, 'Если хотите продолжить введите: Дальше,\n'
                                        'Для выхода  введите : Выход ')
                step_action += 1

            if step_action == 7:
                if user_msg == 'дальше':
                    self.i += 3
                    i = self.i
                    msg = vk.itog_msg(session_maker, i)
                    self.write_msg(user_id, f"{msg}")
                    self.write_msg(user_id, 'Если хотите продолжить введите: Дальше \n'
                                            'Для выхода  введите : Выход ')
                if user_msg == 'выход':
                    self.write_msg(user_id, 'Пока')
                    os.remove("user_file.json")
                    # os.remove("candidate_file.json")
                    clean_table(sql_name)
                    sys.exit()






