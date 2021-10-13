import requests
import datetime
import time
import json
from sql_db import Users, Variants, Photos

class Vk:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, user_id):
        self.user_id = user_id
        self.params = {'access_token': token,  'v': '5.131'}

    def get_city_msg(self, city_t):
        user_url = self.url + 'database.getCities'
        user_params = {'country_id': 1, 'q': city_t}
        city_id_msg = (requests.get(user_url, params={**self.params, **user_params}).json())['response']['items'][0]['id']
        return city_id_msg

    def update_user(self, city_i, city_t):
        with open('user_file.json', encoding='utf-8') as f:
            data = json.load(f)
            data[0]['user_city_id'] = city_i
            data[0]['user_city'] = city_t
            with open('user_file.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        return

    def update_user_a(self, age_):
        with open('user_file.json', encoding='utf-8') as f:
            data = json.load(f)
            data[0]['user_age'] = age_
            with open('user_file.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        return

    def get_user(self):
        user_data = []
        user_url = self.url + 'users.get'
        user_params = {'user_ids': self.user_id, 'fields': 'bdate, sex, city, relation'}
        user = requests.get(user_url, params={**self.params, **user_params}).json()
        user = user['response']
        
        user_id = user[0]['id']
        user_first_name = user[0]['first_name']
        user_last_name = user[0]['last_name']
        user_age = int(datetime.datetime.now().strftime('%Y')) - int(user[0]['bdate'].split('.')[-1] if 'bdate' in user[0] else 0)
        user_city_id = (user[0]['city']['id'] if 'city' in user[0] else 0)
        user_city = (user[0]['city']['title'] if 'city' in user[0] else "-")
        user_sex = user[0]['sex']
        user_data.append({'user_id': user_id, 'user_first_name': user_first_name,
                          'user_last_name': user_last_name, 'user_age': user_age,
                          'user_city_id': user_city_id, 'user_city': user_city, 'user_sex': user_sex})
        with open("user_file.json", "a", encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False)
        return user_data

    def get_candidates(self):
        candidate = []
        with open('user_file.json', encoding='utf-8') as f:
            user_data = json.load(f)
        c_url = self.url + 'users.search'
        # 'city': (user_data[0]['user_city_id']
        c_params = {'sex': (1 if user_data[0]['user_sex'] == 2 else 2), 'hometown': (user_data[0]['user_city']),
                       'status': '6', 'count': 200, 'has_photo': '1', 'fields': 'sex, city, relation, bdate'}
        candidates = requests.get(c_url, params={**self.params, **c_params}).json()['response']['items']
        time.sleep(0.3)

        for c in candidates:
            c_id = c['id']
            c_link = f'vk.com/id{c_id}'
            c_first_name = c['first_name']
            c_last_name = c['last_name']
            c_age = int(datetime.datetime.now().strftime('%Y')) - int((c['bdate'].split('.')[-1] if 'bdate' in c else 0))
            c_city_id = (c['city']['id'] if 'city' in c else '')
            c_city = (c['city']['title'] if 'city' in c else '')
            c_sex = c['sex']
            c_relation = (c['relation'] if 'relation' in c else '')
            c_user_id = user_data[0]['user_id']

            if c_city == user_data[0]['user_city'] and (c_relation == 6 or c_relation == 1) and \
                         (abs(c_age - user_data[0]['user_age']) <= 3):
                candidate.append({'c_id': c_id, 'c_link': c_link, 'c_first_name': c_first_name,
                                  'c_last_name': c_last_name, 'c_age': c_age, 'c_city_id': c_city_id,
                                  'c_city': c_city,  'c_relation': c_relation, 'c_sex': c_sex, 'user_id': c_user_id})
        return candidate

    def get_photos(self):
        candidate_photo = {}
        candidate = self.get_candidates()
        for c_ in candidate:
            photos_dict = {}
            c_id = c_['c_id']
            get_photo_url = self.url + 'photos.get'
            get_photo_params = {'owner_id': c_id, 'album_id': 'profile', 'count': 200, 'extended': '1'}
            photos = requests.get(get_photo_url, params={**self.params, **get_photo_params}).json()['response']['items']
            time.sleep(0.3)

            for photo in photos:
                photo_owner_id = photo['owner_id']
                photo_likes = int(photo['likes']['count'])
                photo_url = photo['sizes'][len(photo['sizes'])-1]['url']
                photos_dict.setdefault(photo_likes, photo_url)

            best_photos_dict = {}
            sorted_photos = sorted(photos_dict.keys())
            if len(sorted_photos) > 3:
                for i in range(1, 4):
                    best_photos_dict.setdefault(sorted_photos[-i], photos_dict[sorted_photos[-i]])
            else:
                best_photos_dict = photos_dict
            candidate_photo.setdefault(photo_owner_id, list(best_photos_dict.values()))
        return candidate_photo


    def itog_msg(self, session_maker):
        candidate = self.get_candidates()
        candidate_photo = self.get_photos()
        with open('user_file.json', encoding='utf-8') as f:
            user_data = json.load(f)
        user = Users(user_data[0]['user_id'], user_data[0]['user_last_name'], user_data[0]['user_first_name'],
                     user_data[0]['user_age'], user_data[0]['user_city'])
        mes = ''
        count_v = len(candidate)
        for i in range(1, (count_v + 1 if count_v <= 3 else 4)):
            v = candidate[i - 1]
            var = Variants(v['c_id'], v['c_last_name'], v['c_first_name'], v['c_link'], v['c_age'],
                           v['c_city'], v['user_id'])
            if session_maker:
                # если есть доступ к базе - запрос, чтобы избежать повтор
                already_in_db = session_maker().query(Users).filter(Users.Id_user == v['c_id']).first()
            else:
                already_in_db = False

            if not already_in_db:
                ph = candidate_photo[candidate[i - 1]['c_id']]
                m = f'{v["c_first_name"]} {v["c_last_name"]}  {v["c_link"]}\n' \
                    f'Возраст: {v["c_age"]}\n' \
                    f'Cамые попумярные фото {ph} \n '
                mes = mes + f'{m}\n'

                for p in ph:
                    p_ = Photos(p, candidate[i - 1]['c_id'])
                    Vk.dump_file(self, session_maker, user, var, p_)  #  запись в базу, если доступно

            if not session_maker:  # если база недоступна - дамп в файл
                with open("candidate_file.json", "a", encoding='utf-8') as f:
                    json.dump(v, f, ensure_ascii=False)
        return mes

    def dump_file(self, session_maker, user, var, p_):
        res = False
        if session_maker:
            session = session_maker()
            session.add(p_)
            session.add(var)
            session.add(user)
            session.commit()
            res = True
        return res



