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


CHANNEL_IDs = CHANNEL_ID.split(",")
CHAT_IDs = CHAT_ID.split(",")
DOMAIN = MEMO_API.split("api/")[0]
OPENID = MEMO_API.split("=")[1]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

res = Resource(DOMAIN, OPENID)
memo = Memo(DOMAIN, OPENID)
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


def format_entity(entity_type, entity_text, entity_url):
    if entity_type == 'bold':
        return f"**{entity_text.strip()}**"
    elif entity_type == 'italic':
        return f"*{entity_text.strip()}*"
    # elif entity_type == 'underline':
    #     return f"__{entity_text.strip()}__"
    elif entity_type == 'strikethrough':
        return f"~~{entity_text.strip()}~~"
    elif entity_type == 'text_link':
        return f"[{entity_text.strip()}]({entity_url})"
    else:
        return entity_text.strip()


def extract_entities(text, entities):
    # 提取实体的 offset 和 length
    entity_list = []
    for entity in entities:
        entity_list.append((entity.type, entity.offset * 2, entity.length * 2, entity.url))
    entity_list.sort(key=lambda x: x[1])

    # 编码为UTF-16
    text_utf16 = text.encode('utf-16', 'surrogatepass')[2:]
    formatted_text = ""
    last_entity_end = 0

    for entity_type, entity_offset, length, entity_url in entity_list:
        # 添加不在entity内的部分
        formatted_text += text_utf16[last_entity_end:entity_offset].decode('utf-16', 'ignore')

        # 提取entity文本
        entity_text = text_utf16[entity_offset:entity_offset + length].decode('utf-16', 'ignore')
        # print(entity_text)
        # 判断entity换行符位置及操作
        if '\n' in entity_text:
            pattern = r'(\n)'
            split_text = re.split(pattern, entity_text)
            for text in split_text:
                if text == '\n':
                    formatted_text += '\n'
                elif text == '':
                    pass
                else:
                    formatted_text += format_entity(entity_type, text, entity_url)
        else:
            # 添加entity的 Markdown 格式
            formatted_text += format_entity(entity_type, entity_text.strip(), entity_url)

        last_entity_end = entity_offset + length
    # 添加剩余的文本部分
    formatted_text += text_utf16[last_entity_end:].decode('utf-16', 'ignore')
    return formatted_text
