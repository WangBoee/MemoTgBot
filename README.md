# Usage
## Docker
    docker run -d \
        --name memotgbot \
        -e BOT_TOKEN="Your Token" \
        -e CHAT_ID="Your ID" \
        -e CHANNEL_ID="Your channel" \
        -e MEMO_API="Your Memoapi" \
        lyx98/memotgbot
## docker-compose
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

# Thanks
