<span>
    <h1>
        <img src="assets\logo_alpha.png" width="50"/>
        FixTweetBot
    </h1>
</span>

[![invite link](https://img.shields.io/badge/invite_link-blue)](https://discord.com/api/oauth2/authorize?client_id=1164651057243238400&permissions=274877934592&scope=bot%20applications.commands)
[![Tog.gg](https://img.shields.io/badge/Tog.gg-fc3164)](https://top.gg/bot/1164651057243238400)
[![Discord Bots](https://top.gg/api/widget/upvotes/1164651057243238400.svg)](https://top.gg/bot/1164651057243238400)
![last commit](https://img.shields.io/github/last-commit/Kyrela/FixTweetBot)

FixTweetBot is a Discord bot that fixes Twitter embeds, using the
[FixTweet](https://github.com/FixTweet/FixTweet) service.

In concrete terms, this bot automatically repost `x.com` and `twitter.com` posts as `fxtwitter` ones.

## Usage

Simply send a message containing a Twitter link, and the bot will remove the twitter embed if any and automatically
repost it as a `fxtwitter` link.

![usage screenshot](assets/screenshot.png)

You can disable or enable the bot in a channel by using the `\disable` and `\enable` commands.

You also can ignore a link by putting it between `<` and `>`, like this: `<https://twitter.com/...>`.

## Add the bot to your server

You can add the bot to your server by clicking on the following
link: [Invite link](https://discord.com/api/oauth2/authorize?client_id=1164651057243238400&permissions=274877934592&scope=bot%20applications.commands)

Please also consider upvoting the bot on [Tog.gg](https://top.gg/bot/1164651057243238400)!

The bot is also available on
[Discord Bots](https://discord.bots.gg/bots/1164651057243238400) and
[Discord Bot List](https://discord.ly/fixtweet).

## Comparison with other bots

|                                                          | FixTweetBot                  | [LinkFix](https://github.com/podaboutlist/linkfix-for-discord) | [Dystopia](https://top.gg/bot/1038138572613619793)                    | [Discord External Video Embeds](https://github.com/adryd325/discord-twitter-video-embeds)                                                | [EmbedEz](https://embedez.com)                                                                                                        | [TweetEmbedder](https://github.com/PenguinLucky/TweetEmbedder)                |
|----------------------------------------------------------|------------------------------|----------------------------------------------------------------|-----------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| App commands support                                     | ✓                            | /                                                              | ✓                                                                     | ✓                                                                                                                                        | ✓                                                                                                                                     | /                                                                             |
| Permissions asked                                        | Minimum                      | Unused ones              <br/>                                 | Unused ones                                                           | Minimum                                                                                                                                  | Privacy violating (ability to read message history, force you to join servers, use other bots commands, read your email address, etc) | Minimum except for a privacy violating one (read message history)             |
| Languages support                                        | fr, en                       | /                                                              | en                                                                    | en                                                                                                                                       | en                                                                                                                                    | /                                                                             |
| Service used                                             | fxtwitter                    | fxtwitter                                                      | vxtwitter                                                             | home-made using discord embeds (doesn't allow videos in embed)                                                                           | Home-made (embedez.com)                                                                                                               | home-made using discord embeds and the fxtwitter api. Doesn't support videos. |
| Multiple link support                                    | ✓                            | ✓                                                              | ✓                                                                     | ✓                                                                                                                                        | ✕                                                                                                                                     | ✓                                                                             |
| Modifications on the base message                        | remove the embed             | ✕                                                              | delete the message                                                    | nothing OR remove embeds OR delete                                                                                                       | ✕                                                                                                                                     | ✕                                                                             |
| New message                                              | fixed links                  | replying (without mention), fixed links                        | indicate the author, repost the full message content with fixed links | reply with the medias OR reply with medias and embed separately OR re-create the message using webhooks with medias and embed separately | fixed link                                                                                                                            | reply with an embed (with videos thumbnails if any video)                     |
| Possibility to ignore non-video posts                    | ✕                            | ✕                                                              | ✕                                                                     | ✓                                                                                                                                        | ✕                                                                                                                                     | ✕                                                                             |
| Content of text-only posts                               | Tweet content, stats, author | Tweet content, stats, author                                   | Tweet content, likes, author                                          | Tweet content, likes, retweets, author                                                                                                   | author                                                                                                                                | Tweet content, likes, retweets, author                                        |
| Ignore non-embedable links                               | only <>                      | ✕                                                              | ✕                                                                     | ✓                                                                                                                                        | ✕                                                                                                                                     | ✕                                                                             |
| Possibility to ignore specific channels                  | ✓                            | ✕                                                              | ✕                                                                     | ✕                                                                                                                                        | ✕                                                                                                                                     | ✕                                                                             |
| Possibility for original author to delete the bot's post | ✕                            | ✕                                                              | ✕                                                                     | ✓                                                                                                                                        | ✕                                                                                                                                     | ✕                                                                             |
| Open-sourced                                             | ✓                            | ✓                                                              | ✕                                                                     | ✓                                                                                                                                        | ✕                                                                                                                                     | ✓                                                                             |
| Other services support                                   | ✕                            | Youtube                                                        | TikTok                                                                | Tiktok, Reddit                                                                                                                           | Tiktok, Instagram, Reddit                                                                                                             | ✕                                                                             |
| Business model                                           | Free                         | Free                                                           | Free                                                                  | Free                                                                                                                                     | Freemium                                                                                                                              | Free                                                                          |
| Website interface                                        | ✕                            | ✕                                                              | ✕                                                                     | ✕                                                                                                                                        | ✓                                                                                                                                     | ✕                                                                             |
| Download system                                          | ✕                            | ✕                                                              | ✕                                                                     | ✕                                                                                                                                        | ✓                                                                                                                                     | ✕                                                                             |
| Supports user link                                       | ✕                            | ✕                                                              | ✕                                                                     | ✕                                                                                                                                        | ✕                                                                                                                                     | ✓                                                                             |

_Do you know of another similar bot that is not included here? Feel free to open an issue!_

## Self-hosting

Simply install Python >= 3.10, clone the repository, and run `pip install -r requirements.txt`.

Be sure to have a database set up using MySQL.

Then, create a `override.config.yml` file containing the following:

```yaml
token: <your_personal_token>
dev_guild: <your_personnal_guild_id> # for dev commands

database:
  host: <your_database_host>
  driver: <your_database_driver>
  database: <your_database_name>
  user: <your_database_user>
  password: <your_database_password>
  port: <your_database_port>
```

You can also override any other config value from `config.yml` in this file.
You might also want to modify other configuration options. More information about how to do it
on [discore](https://github.com/Kyrela/discore).

Now, initialize the database by running `masonite-orm migrate -C database/config.py -d database/migrations`.

Finally, run `python main.py`.

## Get help

If you need help, you can join the [support server](https://discord.gg/3ej9JrkF3U) or open an issue.

## Links

- [Source code](https://github.com/Kyrela/FixTweetBot) (please leave a star!)
- [Original FixTweet Project](https://github.com/FixTweet/FixTweet) (We are not affiliated in any way, but please
  support their work!)
- [Top.gg page](https://top.gg/bot/1164651057243238400) (please leave an upvote!)
- [Support server](https://discord.gg/3ej9JrkF3U)
- [Invite link](https://discord.com/api/oauth2/authorize?client_id=1164651057243238400&permissions=274877934592&scope=bot%20applications.commands)
- [Discord Bots page](https://discord.bots.gg/bots/1164651057243238400)
- [Discord Bot List page](https://discord.ly/fixtweet)

## Additional Credits

- [FixTweet](https://github.com/FixTweet/FixTweet/), the service used to fix Twitter embeds, by the
  [FixTweet team](https://github.com/FixTweet)
