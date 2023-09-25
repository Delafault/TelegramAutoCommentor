### ОБЯЗАТЕЛЬНО ЗАПОЛНИТЕ ДАННЫЕ НИЖЕ ↓

# -Варианты текстовых комментариев
texts_commented = ["Ого вау круто класс", "Бывает", "лол", "По базе, так сказать.", "Ого, пофиг"]

# -Группы для комментирования записей (без @)
channel_usernames = ['kanalbeznazvaniya', 'unnamedcanal']

# -Параметр автоматического вступления в канал
auto_join = True #Заменить 'False' на 'True', чтобы активировать режим.

#########################################


# -Импорт библиотек
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.sync import TelegramClient
from telethon.events import NewMessage
import configparser
import random
import os

# -Чистка консоли
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

api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

client = TelegramClient('SESSION_FOR_TELEGRAM_COMMENTOR', api_id, api_hash, device_model=config['Telegram']['device_model'], system_version=config['Telegram']['system_version'])

# -Вывод логотипа
print(""" (TG-COMMENTOR 2.0)""")

# -Обработчик новых сообщений
async def main():

    channel_entities = [await client.get_entity(username) for username in channel_usernames]

    commented_messages = {entity.id: set() for entity in channel_entities}

    if auto_join:
        for username in channel_usernames:
            try:
                await client(JoinChannelRequest(username))
                gd_print(f"Присоединились к каналу @{username}")
            except Exception as e:
                bd_print(f"Не удалось присоединиться к каналу @{username}: {e}")

    async def handle_new_posts(event):
        print("Создан новый пост. Комментирую...")
        message = event.message
        comment_text = random.choice(texts_commented)
        
        for entity in channel_entities:
            if entity.id == message.peer_id.channel_id:
                if not message.out and message.id not in commented_messages[entity.id]:
                    try:
                        await client.send_message(entity=entity, message=comment_text, comment_to=message)
                        gd_print("Созданный пост успешно прокомментирован.")
                        commented_messages[entity.id].add(message.id)
                    except Exception as e:
                        bd_print(f"Возникла ошибка при комментировании записи: {e}")

    for entity in channel_entities:
        client.add_event_handler(handle_new_posts, event=NewMessage(incoming=True, chats=entity))

    await client.run_until_disconnected()

# -Запуск
with client:
    gd_print("Бот запущен. Мониторим канал(ы)...")
    client.loop.run_until_complete(main())