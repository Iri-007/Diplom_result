from datetime import datetime

from vk_api import vk_api, VkApiError

from engine.checker import Checker

step_size = 10


def set_ages(params, age):
    params['age_from'], params['age_to'] = age - 5, age + 5


def set_city(params, city):
    params['city'] = city


class VKinderEngine:
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)
        self.checker = Checker()

    def get_new_profile(self, params, users):
        for user in users:
            if not self.checker.exist(user['id'], params['user_id']):
                self.checker.put_record(user['id'], params['user_id'])
                return user
        return None

    def search_user(self, params):
        offset = 0
        while True:
            users = self.api.method('users.search',
                                    {'count': step_size, 'offset': offset, 'age_from': params['age_from'],
                                     'age_to': params['age_to'], 'sex': params['sex'],
                                     'city': params['city'], 'status': 6, 'is_closed': False})
            try:
                user = self.get_new_profile(params, users['items'])
            except KeyError:
                return None
            if user is None:
                offset += step_size
            else:
                break
        if user is not None:
            user['about'] = user['first_name'] + ' ' + user['last_name']
            user['photos'] = self.get_three_best_photos(user['id'])
        return user

    def get_params_by_profile(self, user_id):
        info, = self.api.method('users.get', {'user_id': user_id, 'fields': 'city,bdate,sex'})

        sex = 1 if info['sex'] == 2 else 2

        params = {'user_id': user_id, 'name': info['first_name'] + ' ' + info['last_name'],
                  'sex': sex,
                  }
        if 'city' in info and info['city'] is not None:
            set_city(params, info['city']['id'])
        if 'bdate' in info and info['bdate'] is not None:
            age = datetime.now().year - int(info['bdate'].split('.')[2])
            set_ages(params, age)
        return params

    def get_three_best_photos(self, user_id):
        try:
            profile_photos = self.api.method('photos.get', {'user_id': user_id, 'album_id': 'profile', 'extended': 1})
        except VkApiError:
            return ''
        try:
            photos = profile_photos['items']
        except KeyError:
            return ''
        all_photos = []
        for photo in photos:
            all_photos.append({'owner_id': photo['owner_id'], 'id': photo['id'], 'likes': photo['likes']['count'],
                               'comments': photo['comments']['count'], })
        all_photos.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        result = ''
        for num, photo in enumerate(all_photos):
            result += f'photo{photo["owner_id"]}_{photo["id"]},'
            if num == 2:
                break
        return result

    def get_city(self, city_name):
        cities = self.api.method('database.getCities', {'q': city_name})
        if cities['count'] > 0:
            return cities['items'][0]
        return None
