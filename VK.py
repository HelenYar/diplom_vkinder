import requests
import datetime
from pprint import pprint
from sql_db import sql



class Vk:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, user_id):
        self.user_id = user_id
        self.params = {'access_token': token,  'v': '5.131'}



    def get_user(self):

        user_data = []

        user_url = self.url + 'users.get'
        user_params = {'user_ids': self.user_id, 'fields': 'bdate, sex, city, relation'}
        user = requests.get(user_url, params={**self.params, **user_params}).json()
        user = user['response']
        
        user_id = user[0]['id']
        user_first_name = user[0]['first_name']
        user_last_name = user[0]['last_name']
        user_age = int(datetime.datetime.now().strftime('%Y')) - int(user[0]['bdate'].split('.')[-1])
        user_city_id = user[0]['city']['id']
        user_city = user[0]['city']['title']
        user_sex = user[0]['sex']
        user_data.append({'user_id': user_id, 'user_first_name': user_first_name,
                          'user_last_name': user_last_name, 'user_age': user_age,
                          'user_city_id': user_city_id, 'user_city': user_city, 'user_sex': user_sex})
        value_insert = f"{user_id}, '{user_last_name}', '{user_first_name}', {user_age}, {user_sex}, {user_city_id}, '{user_city}'"
        s = sql()
        s.insert_user('user_', value_insert)
        # print(user_data)
        return user_data

    def get_candidates(self):
        candidate = []
        user_data = self.get_user()
        c_url = self.url + 'users.search'
        c_params = {'sex': (1 if user_data[0]['user_sex'] == 2 else 2), 'city': (user_data[0]['user_city_id']),
                       'count': 1000, 'fields': 'sex, city, relation, bdate'}
        candidates = requests.get(c_url, params={**self.params, **c_params}).json()
        candidates = candidates['response']['items']
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
                value_insert = f"{c_id}, '{c_last_name}', '{c_first_name}', '{c_link}', {c_age}, {c_sex}, " \
                               f"{c_city_id}, '{c_city}', {c_relation}, {c_user_id}"
                s = sql()
                s.insert_user('VARIANT', value_insert)
        # pprint(candidate)
        return candidate

    def get_photos(self):
        candidate_photo = {}
        candidate = self.get_candidates()
        for c_ in candidate:
            photos_dict = {}
            c_id = c_['c_id']
            get_photo_url = self.url + 'photos.get'
            get_photo_params = {'owner_id': c_id, 'album_id': 'profile', 'extended': '1' }
            photos = requests.get(get_photo_url, params={**self.params, **get_photo_params}).json()
            photos = photos['response']['items']

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
            candidate_photo.setdefault(photo_owner_id, best_photos_dict)
            photo_owner_id = photo_owner_id

            for like, photo in candidate_photo[photo_owner_id].items():
                value_insert = f"'{photo}', {like}, {photo_owner_id}"
                s = sql()
                s.insert_user('Photos', value_insert)
        return


