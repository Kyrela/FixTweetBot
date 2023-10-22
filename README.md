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

|                                         | FixTweetBot      | [LinkFix](https://github.com/podaboutlist/linkfix-for-discord) | [Dystopia](https://top.gg/bot/1038138572613619793)                    |
|-----------------------------------------|------------------|----------------------------------------------------------------|-----------------------------------------------------------------------|
| App commands support                    | ✓                | /                                                              | ✓                                                                     |
| Permissions asked                       | Minimum          | Unused ones                                                    | Unused ones                                                           |
| Languages support                       | fr, en           | /                                                              | en                                                                    |
| Service used                            | fxtwitter        | fxtwitter                                                      | vxtwitter                                                             |
| Multiple link support                   | ✓                | ✓                                                              | ✓                                                                     |
| Modifications on the base message       | remove the embed | ✕                                                              | delete the message                                                    |
| New message                             | fixed links      | replying (without mention), fixed links                        | indicate the author, repost the full message content with fixed links |
| Possibility to ignore specific links    | ✓                | ✕                                                              | ✕                                                                     |
| Possibility to ignore specific channels | ✓                | ✕                                                              | ✕                                                                     |
| Open-sourced                            | ✓                | ✓                                                              | ✕                                                                     |
| Other services support                  | ✕                | youtube                                                        | ✕                                                                     |

_Do you know of another similar bot that is not included here? Feel free to open an issue!_

## Self-hosting

Simply install Python >= 3.10, clone the repository, and run `pip install -r requirements.txt`.

Then, create a `.env` file containing the following:

```env
TOKEN=your_bot_token
DISCORE_CONFIG=prod.config.yml
```

You might also want to modify `config.yml` and `prod.config.yml`. More informations about how to do it
on [discore](https://github.com/Kyrela/discore).

Finally, run `python main.py`.

## Additional Credits

- [FixTweet](https://github.com/FixTweet/FixTweet/), the service used to fix Twitter embeds, by the
  [FixTweet team](https://github.com/FixTweet)
