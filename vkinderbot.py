import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import access_token, community_token
from engine.botengine import VKinderEngine, set_city, set_ages


class VKinderBot:

    def __init__(self, bots_token, grant_access_token):
        self.interface = vk_api.VkApi(token=bots_token)
        self.bot_engine = VKinderEngine(grant_access_token)
        self.params = None

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send', {'user_id': user_id, 'message': message, 'attachment': attachment,
                                                'random_id': get_random_id()})

    def event_handler(self):
        vk_long_poll = VkLongPoll(self.interface)

        for event in vk_long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.bot_engine.get_params_by_profile(event.user_id)
                    self.message_send(event.user_id, f'Здравствуйте, {self.params["name"]}.')
                    if 'city' not in self.params:
                        self.message_send(event.user_id, f'В Вашем профиле не указан город проживания. Введите город.')
                    elif 'age_from' not in self.params:
                        self.message_send(event.user_id, f'В Вашем профиле не указан возраст. Введите возраст в годах.')
                elif command == 'поиск':
                    if self.params is None:
                        self.message_send(event.user_id, 'Напишите "Привет" для начала работы сервиса.')
                    else:
                        user = self.bot_engine.search_user(self.params)
                        self.message_send(event.user_id, f'Найден: {user["about"]}, https://vk.com/id{user["id"]}',
                                          attachment=user["photos"])
                        self.bot_engine.put_to_viewed(user["id"], self.params['user_id'])
                elif command == 'пока':
                    self.params = None
                    self.message_send(event.user_id, 'Приятно было поработать, надеюсь, Вы ещё вернётесь.')
                elif self.params is not None and 'city' not in self.params:
                    city = self.bot_engine.get_city(command)
                    if city is not None:
                        self.message_send(event.user_id, f'Город для поиска: {city["title"]}.')
                        set_city(self.params, city['id'])
                        if 'age_from' not in self.params:
                            self.message_send(event.user_id, f'В Вашем профиле не указан возраст.'
                                                             f' Укажите возраст числом (в годах).')
                elif self.params is not None and 'age_from' not in self.params:
                    if command.isdigit():
                        set_ages(self.params, int(command))
                        self.message_send(event.user_id, f'Установлен возраст для поиска: {int(command)}')
                else:
                    self.message_send(event.user_id, 'Сервис поддерживает только две команды: "Привет" и "Поиск".')


if __name__ == '__main__':
    bot = VKinderBot(community_token, access_token)
    bot.event_handler()
