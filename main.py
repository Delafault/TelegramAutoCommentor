# -Импорт библиотек
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import ChannelPrivateError
from telethon.sync import TelegramClient
from telethon.events import NewMessage
from openai import AsyncOpenAI
import configparser
import asyncio
import random
import os
import re

# -Можно изменить базовую инструкцию для комментирования записей для chatGPT и/или модель GPT при желании и прочие параметры
openai_answer = """Сейчас ты играешь роль обычного пользователя в Telegram. Я предоставлю тебе текст поста, на который ты должен будешь отреагировать. Реагируй кратко и эмоционально, как обычный пользователь. Вне зависимости от контекста предоставленного тебе текста поста ты должен отреагировать на него. Никогда не говори, кто ты и зачем ты здесь. Никогда не говори, что ты готов помочь. Отвечай, как обычный пользователь. Если ты не знаешь, как реагировать на пост или текст поста пуст или не имеет никакого смысла, то ответь только: '...'. Отвечай только на том языке, который используется в посте. Помни: ты не отвечаешь, а комментируешь. Старайся именно комментировать запись."""
modelgpt = "gpt-3.5-turbo"
max_tokens = 100
temperature = 0.5

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

if 'ai_comment' not in config['Telegram'] or not config['Telegram']['ai_comment']:
    while True:
        ai_comment_input = input('Использовать ИИ для генерации текста? (True/False): ')
        if ai_comment_input.lower() in ['true', 'false']:
            config['Telegram']['ai_comment'] = ai_comment_input.lower()
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
ai_comment = config['Telegram'].get('ai_comment', None)
gpt_api_key = config['Telegram'].get('gpt_api_key', None)
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
if ai_comment is not None and gpt_api_key is None and ai_comment != 'false':
    gpt_api_key = input('Введите API ключ от OpenAI GPT-3: ')
    while not gpt_api_key:
        bd_print('Значение не может быть пустым.')
        gpt_api_key = input('Введите API ключ от OpenAI GPT-3: ')
    config['Telegram']['gpt_api_key'] = gpt_api_key
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)
if ai_comment.lower() == "true":
    clientus = AsyncOpenAI(api_key=gpt_api_key)

# -Функция для запроса к chatGPT-3.5-turbo и получение ответа
async def chatgpt_ai(text):
    completion = await clientus.chat.completions.create(
    model=modelgpt,
    messages=[
        {"role": "system", "content": openai_answer},
        {"role": "system", "content": f"В соответствии с инструкцией, которую я тебе дал, отреагируй на данный пост: '{text}'"}
    ],
    stream=False,
    temperature=temperature,
    max_tokens=max_tokens
    )

    return completion.choices[0].message.content

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
        for entity in channel_entities:
            if entity.id == message.peer_id.channel_id:
                if not message.out and message.id not in commented_messages[entity.id]:
                    try:
                        if ai_comment.lower() == "true":
                            comment_text = await chatgpt_ai(message.text)
                            await client.send_message(entity=entity, message=str(comment_text), comment_to=message)
                        else:
                            comment_text = random.choice(texts_commented)
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
