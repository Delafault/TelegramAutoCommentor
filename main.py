# -Импорт библиотек
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.sync import TelegramClient
from telethon.events import NewMessage
from telethon.errors import ChannelPrivateError
import configparser
import asyncio
import random
import os
import re

logo = """
▀█▀ █▀▀ ▄▄ █▀▀ █▀█ █▀▄▀█ █▀▄▀█|ᵇʸ ᵈᵉˡᵃᶠᵃᵘˡᵗ
░█░ █▄█ ░░ █▄▄ █▄█ █░▀░█ █░▀░█
"""


# -Функция для чистки консоли
def cls_cmd():
    os.system('cls' if os.name == 'nt' else 'clear')

# -Определение принтов
def gd_print(value):
    green_color = '\033[32m'
    reset_color = '\033[0m'
    result = f"\n>{green_color} {value} {reset_color}\n"
    print(result)

def bd_print(value):
    red_color = '\033[31m'
    reset_color = '\033[0m'
    result = f"\n>{red_color} {value} {reset_color}\n"
    print(result)

# -Создание клиента и получение необходимых данных из 'settings.ini'
config = configparser.ConfigParser()
config.read('settings.ini')
cls_cmd()

if 'Telegram' not in config:
    config['Telegram'] = {}

if 'api_id' not in config['Telegram'] or not config['Telegram']['api_id']:
    api_id = input('Введите api_id: ')
    while not api_id:
        bd_print('Значение не может быть пустым.')
        api_id = input('Введите api_id: ')
    config['Telegram']['api_id'] = api_id

if 'api_hash' not in config['Telegram'] or not config['Telegram']['api_hash']:
    api_hash = input('Введите api_hash: ')
    while not api_hash:
        bd_print('Значение не может быть пустым.')
        api_hash = input('Введите api_hash: ')
    config['Telegram']['api_hash'] = api_hash

if 'device_model' not in config['Telegram'] or not config['Telegram']['device_model']:
    device_model = input('Введите device_model: ')
    while not device_model:
        bd_print('Значение не может быть пустым.')
        device_model = input('Введите device_model: ')
    config['Telegram']['device_model'] = device_model

if 'system_version' not in config['Telegram'] or not config['Telegram']['system_version']:
    system_version = input('Введите system_version: ')
    while not system_version:
        bd_print('Значение не может быть пустым.')
        system_version = input('Введите system_version: ')
    config['Telegram']['system_version'] = system_version

while 'texts_commented' not in config['Telegram'] or not config['Telegram']['texts_commented']:
    print('Введите текстовые комментарии (для завершения введите пустую строку, для комментария с несколькими строками используйте "\\n" для создания новой строки):')
    texts_commented_lines = []
    while True:
        line = input()
        if not line:
            if not texts_commented_lines:
                bd_print('Список текстовых комментариев пуст. Пожалуйста, введите хотя бы один комментарий:')
            else:
                break
        texts_commented_lines.append(line)
    texts_commented = '\n'.join(texts_commented_lines)
    comments = texts_commented.split('\n')

    formatted_comments = []
    current_comment = ""
    for comment in comments:
        if comment.startswith('\t') or comment.startswith(' '):
            current_comment += comment.lstrip() + '\n'
        else:
            if current_comment:
                formatted_comments.append(current_comment.rstrip())
            current_comment = comment + '\n'

    if current_comment:
        formatted_comments.append(current_comment.rstrip())
    formatted_texts_commented = '\n'.join(formatted_comments)
    config['Telegram']['texts_commented'] = formatted_texts_commented

while 'channel_usernames' not in config['Telegram'] or not config['Telegram']['channel_usernames']:
    print('Введите группы для комментирования записей (без @, каждый с новой строки, для завершения введите пустую строку):')
    channel_usernames_lines = []
    while True:
        line = input()
        if not line:
            if not channel_usernames_lines:
                bd_print('Список каналов пуст. Пожалуйста, введите хотя бы один @username канала:')
            else:
                break
        channel_usernames_lines.append(line)
    channel_usernames = ' ,'.join(channel_usernames_lines)
    config['Telegram']['channel_usernames'] = channel_usernames

if 'auto_join' not in config['Telegram'] or not config['Telegram']['auto_join']:
    while True:
        auto_join_input = input('Хотите активировать режим автоматического вступления в канал? (True/False): ')
        if auto_join_input.lower() in ['true', 'false']:
            config['Telegram']['auto_join'] = auto_join_input.lower()
            break
        else:
            bd_print('Пожалуйста, введите "True" или "False".')

with open('settings.ini', 'w') as configfile:
    config.write(configfile)

api_id = config['Telegram'].get('api_id', None)
api_hash = config['Telegram'].get('api_hash', None)
device_model = config['Telegram'].get('device_model', None)
system_version = config['Telegram'].get('system_version', None)
texts_commented = config['Telegram'].get('texts_commented', None) #or texts_commented = ['привет', 'да', 'Как дела?\nУ меня всё хорошо']
channel_usernames = config['Telegram'].get('channel_usernames', None)
auto_join = config['Telegram'].get('auto_join', None)
client = TelegramClient('SESSION_FOR_TELEGRAM_COMMENTOR', api_id, api_hash, device_model=device_model, system_version=system_version)

if texts_commented is not None:
    comments = texts_commented.split('\n')
    texts_commented = []
    for comment in comments:
        comment = comment.replace('\\n', '\n')
        texts_commented.extend(re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', comment))
if channel_usernames is not None:
    channels = channel_usernames.split(', ')
    channel_usernames = [channel.strip() for channel in channels if channel]


# -Тип главная функция
async def main():

    name = await client.get_me()
    gd_print(f"Бот запущен ({name.first_name}). Мониторим канал(ы)...")
    try:
        channel_entities = None
        channel_entities = [await client.get_entity(username) for username in channel_usernames]
        commented_messages = {entity.id: set() for entity in channel_entities}
    except Exception as e:
        bd_print(f"Ошибка: {e}")
        if 'No user has' in str(e) and 'as username' in str(e) and channel_entities == None:
            bd_print("Плохо дело. Ни один канал не был найден. Работать негде. Скрипт завершён.")
            exit()

    if auto_join.lower() == "true":
        for username in channel_usernames:
            try:
                await client(JoinChannelRequest(username))
                gd_print(f"Присоединились к каналу @{username}")
            except Exception as e:
                bd_print(f"Не удалось присоединиться к каналу @{username}: {e}")

    # -Обработчик события создания новых постов.
    async def handle_new_posts(event):
        loop = asyncio.get_event_loop()
        start_time = loop.time()
        print("> Создан новый пост. Комментирую...")
        message = event.message
        comment_text = random.choice(texts_commented)
        for entity in channel_entities:
            if entity.id == message.peer_id.channel_id:
                if not message.out and message.id not in commented_messages[entity.id]:
                    try:
                        await client.send_message(entity=entity, message=str(comment_text), comment_to=message)
                        end_time = loop.time()
                        elapsed_time = end_time - start_time
                        gd_print(f"Созданный пост успешно прокомментирован. Затраченное время: {round(elapsed_time, 2)} секунд.")
                        commented_messages[entity.id].add(message.id)
                    except ChannelPrivateError as banorprivate:
                        bd_print(f"Ошибка по привату: {banorprivate}")
                    except Exception as e:
                        bd_print(f"Возникла ошибка при комментировании записи: {e}")

    for entity in channel_entities:
        client.add_event_handler(handle_new_posts, event=NewMessage(incoming=True, chats=entity))

    await client.run_until_disconnected()

# -Запуск, чистка консоли и вывод лого
if __name__ == "__main__":
    cls_cmd()
    print(logo)
    with client:
        client.loop.run_until_complete(main())
