# FixMediaBot

FixMediaBot is based on its upstream [FixTweetBot](https://github.com/KBotsWork/FixTweetBot). 
The main modifications in this bot are that this one is able to update previews for Twitter, Tiktok, and Instagram.

## Deployment

Given the sensitive nature of the content that this bot needs to process, I do not provide a public instance of this bot.
Instead, I encourage you to self-host in an environment that you trust to ensure the privacy of the messages that your
guild members send. To that end, I provide an easy way to get going using Docker.

To get started, make a new folder to act as a base and create a copy of `docker-compose.yml` in that folder.

```yml
services:
  fixMediaBot:
    image: ghcr.io/arthurlockman/fixmediabot:main
    restart: unless-stopped
    volumes:
      - ./override.config.yml:/app/override.config.yml
    depends_on:
      db:
        condition: service_healthy
  db:
    image: mariadb:10.3
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: fixmediabot
      MYSQL_ALLOW_EMPTY_PASSWORD: yes
    volumes:
      - ./dbSchema.sql:/docker-entrypoint-initdb.d/schema.sql:ro
      - db-data:/var/lib/mysql:rw
    healthcheck:
      test: [ "CMD", "mysqladmin" ,"ping", "-h", "localhost" ]
      timeout: 20s
      retries: 10

volumes:
  db-data:
```

In that folder, create a new file called `override.config.yml` with the following contents:

```yml
token: <your discord bot token>

database:
  host: db
  driver: mysql
  database: fixmediabot
  user: root
  port: 3306
```

Replace `<your discord bot token>` with the token you get from the Discord Developer Portal.

Last, download the `dbSchema.sql` file:

```bash
curl -o dbSchema.sql https://raw.githubusercontent.com/arthurlockman/FixMediaBot/main/dbSchema.sql
```

That should be all you need to do. Run `docker-compose up -d` in the folder you created and the bot should start up.

## Support

This isn't my full-time job. Support is given on a best-effort basis. Feel free to make PRs to address issues that you find.