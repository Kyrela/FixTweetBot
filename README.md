
<span>
    <h1>
        <img src="assets\logo_alpha.png" width="50"/>
        FixTweetBot
    </h1>
</span>

[![invite link](https://img.shields.io/badge/invite_link-blue)](https://discord.com/api/oauth2/authorize?client_id=1164651057243238400&permissions=274877934592&scope=bot%20applications.commands)
![last commit](https://img.shields.io/github/last-commit/Kyrela/FixTweetBot)

FixTweetBot is a Discord bot that fixes Twitter embeds, using the
[FixTweet](https://github.com/FixTweet/FixTweet) service.

In concrete terms, this bot automatically repost `x.com` and `twitter.com` posts as `fxtwitter` ones.

## Usage

Simply send a message containing a Twitter link, and the bot will automatically repost it as a `fxtwitter` link.

You can disable or enable the bot in a channel by using the `\disable` and `\enable` commands.

## Add the bot to your server

You can add the bot to your server by clicking on the following link: [Invite link](https://discord.com/api/oauth2/authorize?client_id=1164651057243238400&permissions=274877934592&scope=bot%20applications.commands)

## Self-hosting

Simply install Python >= 3.10, clone the repository, and run `pip install -r requirements.txt`.

Then, create a `.env` file containing the following:

```env
TOKEN=your_bot_token
DISCORE_CONFIG=prod.config.yml
```

You might also want to modify `config.yml` and `prod.config.yml`. More informations about how to do it on [discore](https://github.com/Kyrela/discore).

Finally, run `python main.py`.

## Additional Credits

- [FixTweet](https://github.com/FixTweet/FixTweet/), the service used to fix Twitter embeds, by the
  [FixTweet team](https://github.com/FixTweet)
