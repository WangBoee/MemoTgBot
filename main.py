from channel import *
from bot import *


# 启动机器人
async def main():
    await asyncio.gather(bot.polling(), multi_photo_checker())


if __name__ == "__main__":
    asyncio.run(main())
