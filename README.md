# MemoTgBot Project
## Introduction
This project is my personal application for learning Python. Rebuilding based on the project [telegramMemoBot](https://github.com/qazxcdswe123/telegramMemoBot). 

Project features:
- Saving text in Markdown format to Memo.
- Using Memo to record channel information and transform channels into personal media management tools.


## Usage
### docker
    docker run -d \
        --name memotgbot \
        -e BOT_TOKEN="Your Token" \
        -e CHAT_ID="Your ID" \
        -e CHANNEL_ID="Your ChannelID" \
        -e MEMO_API="Your Memoapi" \
        lyx98/memotgbot
Example usage

    docker run -d \
        --name memotgbot \
        -e BOT_TOKEN="6037516:AAHAIIcAkxgyyDw" \
        -e CHAT_ID="16007444,1234" \
        -e CHANNEL_ID="-10019770855,-1001489946" \
        -e MEMO_API="https://example.com/api/memo?openId=abc" \
        lyx98/memotgbot
### docker-compose
    version: "3.0"
    services:
      memotgbot:
        image: lyx98/memotgbot
        container_name: memotgbot
        environment:
          - BOT_TOKEN=Your Token
          - CHAT_ID=Your ID
          - CHANNEL_ID=Your channel
          - MEMO_API=Your Memoapi
        restart: always
Example Usage

    version: "3.0"
    services:
      memotgbot:
        image: lyx98/memotgbot
        container_name: memotgbot
        environment:
          - BOT_TOKEN=6037516:AAHAIIcAkxgyyDw
          - CHAT_ID=16007444,1234
          - CHANNEL_ID=-10019770855,-1001489946
          - MEMO_API=https://example.com/api/memo?openId=abc
        restart: always

## Thanks
[memos](https://github.com/usememos/memos)

[telegramMemoBot](https://github.com/qazxcdswe123/telegramMemoBot)