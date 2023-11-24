from api import Memo, Resource
from telebot import asyncio_helper
from telebot.async_telebot import AsyncTeleBot
import threading
import logging
import re
import os

CHAT_ID = os.getenv("CHAT_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MEMO_API = os.getenv("MEMO_API")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MEMO_API_VER = os.getenv("MEMO_API_VER") if os.getenv("MEMO_API_VER") is not None else 'v1'
MEMO_PUBLIC = os.getenv("MEMO_PUBLIC") if os.getenv("MEMO_PUBLIC") is not None else 'PUBLIC'

CHANNEL_IDs = CHANNEL_ID.split(",")
CHAT_IDs = CHAT_ID.split(",")
DOMAIN = MEMO_API.split("api/")[0]
OPENID = MEMO_API.split("=")[1]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

res = Resource(DOMAIN, OPENID, MEMO_API_VER)
memo = Memo(DOMAIN, OPENID, MEMO_API_VER)
bot = AsyncTeleBot(BOT_TOKEN)
lock = threading.Lock()
media_group = {}  # 用于存储不同组的图片


def auth(func):
    async def wrapper(message):
        # 检查消息是否来自目标频道或用户
        if str(message.chat.id) in CHANNEL_IDs or CHAT_IDs:
            await func(message)
        else:
            logging.warning(f"Unauthorized access: {message.chat.id}")
            await bot.reply_to(message, "Unauthorized access")

    return wrapper


def get_file_id(message) -> str:
    try:
        file_id = getattr(message, message.content_type)[-1].file_id
    except Exception:
        file_id = getattr(message, message.content_type).file_id
    return file_id



def format_entity(entity_text, entity_info_list):
    formatted_text = entity_text
    for entity_type, length, entity_url in entity_info_list:
        if entity_type == 'text_link':
            formatted_text = f"[{formatted_text.strip()}]({entity_url})"
        elif entity_type == 'bold':
            formatted_text = f"**{formatted_text.strip()}**"
        elif entity_type == 'italic':
            formatted_text = f"*{formatted_text.strip()}*"
        elif entity_type == 'strikethrough':
            formatted_text = f"~~{formatted_text.strip()}~~"
        elif entity_type == 'mention':
            formatted_text = f"[{formatted_text.strip()}](https://t.me/{entity_text.strip()[1:]})"
        else:
            formatted_text = formatted_text.strip()
    return formatted_text
            

def is_supported_entity(entity):
    return entity.type in ['text_link', 'bold', 'italic', 'strikethrough', 'mention']

def extract_entities(text, entities):
    # 提取实体的 offset 和 length
    entity_dict = {}

    for entity in entities:
        if not is_supported_entity(entity):
            continue

        entity_offset = entity.offset * 2
        length = entity.length * 2
        entity_type = entity.type
        entity_url = entity.url

        # 使用字典存储相同 offset 的 entity
        if entity_offset in entity_dict:
            entity_dict[entity_offset].append((entity_type, length, entity_url))
        else:
            entity_dict[entity_offset] = [(entity_type, length, entity_url)]

    text_utf16 = text.encode('utf-16', 'surrogatepass')[2:]
    formatted_text = ""
    last_entity_end = 0

    for entity_offset, entity_info_list in sorted(entity_dict.items()):

        # 添加不在entity内的部分
        formatted_text += text_utf16[last_entity_end:entity_offset].decode('utf-16', 'ignore')

        # 提取entity文本
        length = entity_info_list[0][1]
        entity_text = text_utf16[entity_offset:entity_offset + length].decode('utf-16', 'ignore')
        if '\n' in entity_text:
            pattern = r'(\n)'
            split_text = re.split(pattern, entity_text)
            for text in split_text:
                if text == '\n':
                    formatted_text += '\n'
                elif text == '':
                    pass
                else:
                    formatted_text += format_entity(entity_text, entity_info_list)
        else:
            formatted_text += format_entity(entity_text, entity_info_list)
        last_entity_end = entity_offset + length

    formatted_text += text_utf16[last_entity_end:].decode('utf-16', 'ignore')
    return formatted_text
