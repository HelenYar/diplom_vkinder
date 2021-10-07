from random import randrange
import sys
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import token, token_user
from VK import Vk
from sql_db import sql


class Vkinder:
    def __init__(self, token):
        self.vk = vk_api.VkApi(token=token)
        self.longpoll = VkLongPoll(self.vk)


    def write_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

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
                self.write_msg(user_id, 'Привет, хочешь найти себе пару? \n'
                                        'Напиши  OK чтобы начать\n'
                                        'Далее следуй по инструкции!')
                step_action += 1

            if step_action == 1:
                if user_msg == "ок":
                    self.write_msg(user_id, 'Если вы ищете человека примерно своего возраста и из вашего города, то введите "Готово"\n')
                    vk = Vk(token_user, user_id)
                    step_action += 1
                user_msg = ""

            if step_action == 2:
                if user_msg.lower() == 'готово':
                    vk.get_user()
                    s = sql()
                    c = s.get_city_()
                    if c != None:
                        self.write_msg(user_id, 'В вашем профиле не указан город\n'
                                                'Введите название, например Москва\n')
                        user_msg = "нет города"
                        step_action -= 1
                    step_action += 2

            if step_action == 3:
                if user_msg != 'нет города':
                    city_t = user_msg.title()
                    city_i = vk.get_city_msg(city_t)
                    s = sql()
                    s.update_user(city_i, city_t)
                    user_msg = "*"
                    step_action += 1

            if step_action == 4:
                if user_msg.lower() == 'готово' or user_msg.lower() == '*':
                    a = s.get_age_()
                    if a != None:
                        self.write_msg(user_id, 'В вашем профиле не указан возраст\n'
                                                'Введите его, например 18\n')
                        user_msg = "нет возраста"
                        step_action -= 1
                    step_action += 2

            if step_action == 5:
                if user_msg != "нет возраста":
                    age_ = user_msg
                    s = sql()
                    s.update_user_a(age_)
                    step_action += 1


            if step_action == 6:
                vk.get_photos()
                s = sql()
                self.write_msg(user_id, f"{s.itog_msg()}")
                self.write_msg(user_id, 'Для выхода  введите : Выход ')
                step_action += 1

            if step_action == 7:
                if user_msg == 'выход':
                    self.write_msg(user_id, 'Пока')
                    s = sql()
                    s.clean_table()
                    sys.exit()




