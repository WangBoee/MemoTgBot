from telebot.async_telebot import AsyncTeleBot
import asyncio

BOT_TOKEN = '6037196516:AAHAIIcAkxgyyDwet-B4Zrg-BZa7YxXW79s'
bot = AsyncTeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
	await bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
async def echo_all(message):
	await bot.reply_to(message, message.text)


asyncio.run(bot.polling())

