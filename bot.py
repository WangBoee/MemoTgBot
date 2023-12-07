from utils import *


@bot.message_handler(commands=["start", "help"])
async def send_help(message):
    logging.info(f"Help message sent to {message.chat.id}")
    await bot.reply_to(message, "https://github.com/lyx9805/MemoTgBot")


@bot.message_handler(content_types=["text"])
@auth
async def send_text_memo(message):
    try:
        logging.debug(f"Json信息：{message.json}")

        if 'entities' not in message.json:
            message_text = message.text
        else:
            message_text = extract_entities(message.text, message.entities)
        msg_link = getMsgLink(message)
        if msg_link:
            message_text = f"{message_text}\n\n[Message link]({msg_link})"
        memo_id = await memo.send_memo(content=message_text, visibility=MEMO_PUBLIC)
        logging.info(f"Memo sent: {DOMAIN}m/{memo_id}")
        await bot.reply_to(message, f"{DOMAIN}m/{memo_id}")
    except Exception as e:
        logging.error(f"Error: {e} in send_text_memo")
        await bot.reply_to(message, f"Error: {e}")


@bot.message_handler(content_types=["photo"])
@auth
async def send_photo_memo(message):
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
                }
                media_group[message.media_group_id] = init_val
    else:
        # only one photo
        try:
            file_info = await bot.get_file(get_file_id(message))
            file = await bot.download_file(file_info.file_path)

            res_id = await res.create_res(file)
            logging.debug(f"file_id:{get_file_id(message)},file_info:{file_info},"
                          f"res_id:{res_id},message.caption:{message.caption},[res_id]:{[res_id]}")
            if 'caption_entities' not in message.json:
                caption = message.caption
            else:
                caption = extract_entities(message.caption, message.caption_entities)
            msg_link = getMsgLink(message)
            if msg_link:
                caption = f"{caption}\n\n[Message link]({msg_link})"
            memo_id = await memo.send_memo(
                content=caption, visibility=MEMO_PUBLIC, res_id_list=[res_id]
            )
            await bot.reply_to(message, f"{DOMAIN}m/{memo_id}")
        except Exception as e:
            logging.error(f"Error: {e} in send_photo_memo")
            await bot.reply_to(message, f"Error: {e}")
