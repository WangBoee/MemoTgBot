import asyncio
from utils import *


async def savetomemo_and_delreply(message_text, channel_id, message_id):
    # Send to memo
    await memo.send_memo(content=message_text, visibility=MEMO_PUBLIC)
    logging.info('Successfully save to memo!')

    # 回复频道消息
    reply_text = f"🎉Success!"
    reply_message = await bot.send_message(channel_id, reply_text, reply_to_message_id=message_id)

    # 延时5秒后删除回复消息
    await asyncio.sleep(5)
    await bot.delete_message(channel_id, reply_message.message_id)


async def multi_photo_checker():
    while True:
        logging.debug(f"Multi photo checker started")
        for message_group_id, data in list(media_group.items()):
            logging.info(f"Set {message_group_id} is ready to send")
            file_list = []
            res_id_list = []
            for fid in data["fid_list"]:
                file_info = await bot.get_file(fid)
                file = await bot.download_file(file_info.file_path)
                file_list.append(file)
            for f in file_list:
                res_id = await res.create_res(f)
                res_id_list.append(res_id)
            media_group.pop(message_group_id)
            memo_id = await memo.send_memo(content=data["caption"], visibility=MEMO_PUBLIC, res_id_list=res_id_list)
            if 'channel_id' not in data:
                await bot.reply_to(data["message"], f"{DOMAIN}m/{memo_id}")
            else:
                reply_text = f"🎉Success!"
                reply_message = await bot.send_message(data['channel_id'], reply_text)

                # 延时5秒后删除回复消息
                await asyncio.sleep(5)
                await bot.delete_message(data['channel_id'], reply_message.message_id)

        await asyncio.sleep(5)


@bot.channel_post_handler(content_types=['text'])
@auth
async def handle_channel_message(message):
    try:
        print(f"message: {message}")
        logging.debug(f"频道消息：{message}")
        logging.debug(f"Json信息：{message.json}")

        # 获取频道消息的内容和其他相关信息
        message_id = message.message_id
        channel_id = message.chat.id
        if 'entities' not in message.json:
            message_text = message.text
        else:
            message_text = extract_entities(message.text, message.entities)

        await savetomemo_and_delreply(message_text, channel_id, message_id)

    except Exception as e:
        # 错误处理
        error_message = f"处理频道消息时发生错误: {e}"
        if message.chat.id == CHANNEL_ID:
            await bot.send_message(message.chat.id, error_message)
        logging.error(f"处理频道消息时发生错误: {e}")


@bot.channel_post_handler(content_types=['photo'])
@auth
async def handle_photo_message(message):
    try:
        logging.info(f"频道消息：{message}")
        if message.media_group_id:
            logging.info(f"Media group ID: {message.media_group_id}")
            with lock:
                # Shouldn't download here since download is slow
                fid = get_file_id(message)
                prev_val = media_group.get(message.media_group_id)
                if prev_val:
                    prev_val["fid_list"].append(fid)
                    if message.caption:
                        prev_val["caption"].append(message.caption)
                else:
                    if 'caption_entities' not in message.json:
                        caption = message.caption
                    else:
                        caption = extract_entities(message.caption, message.caption_entities)
                    init_val = {
                        "message": message,
                        "caption": caption or "",
                        "fid_list": [fid],
                        "channel_id": message.chat.id,
                    }
                    media_group[message.media_group_id] = init_val
        else:
            # 获取图片信息
            photo = message.photo[-1]  # 获取最后一张图片，较大的尺寸
            file_id = photo.file_id
            message_id = message.message_id
            channel_id = message.chat.id

            # 下载图片
            file_info = await bot.get_file(file_id)
            file = await bot.download_file(file_info.file_path)

            # 在这里可以将图片保存到本地、进行图像处理等操作
            res_id = await res.create_res(file)

            # 保存到memo中
            if 'caption_entities' not in message.json:
                caption = message.caption
            else:
                caption = extract_entities(message.caption, message.caption_entities)
            await memo.send_memo(content=caption, visibility=MEMO_PUBLIC, res_id_list=[res_id])
            logging.info('Successfully save to memo!')

            # 回复消息
            reply_text = f"🎉Success!"
            reply_message = await bot.send_message(channel_id, reply_text, reply_to_message_id=message_id)

            # 延时5秒后删除回复消息
            await asyncio.sleep(5)
            await bot.delete_message(channel_id, reply_message.message_id)

    except Exception as e:
        # 错误处理
        logging.error(f"处理图片消息时发生错误: {e}")


@bot.channel_post_handler(content_types=["document", "video", "audio"])
async def handle_file_message(message):
    try:
        logging.debug(f"频道消息：{message}")
        logging.debug(f"json消息：{message.json}")

        channel_id = message.chat.id
        message_id = message.id
        tel_link = 'https://t.me/c/' + str(channel_id)[4:] + '/' + str(message_id)
        if message.caption is None:
            caption = ''
        else:
            if 'caption_entities' not in message.json:
                caption = message.caption
            else:
                caption = extract_entities(message.caption, message.caption_entities) + '\n'
        content = f"⭐**Telegram File**⭐\n" + caption + \
                  f"\n🗂**[{message.json[message.content_type]['file_name']}]({tel_link})**"
        await savetomemo_and_delreply(content, channel_id, message_id)
    except Exception as e:
        logging.error(f"Error: {e} in handle_file_message")
