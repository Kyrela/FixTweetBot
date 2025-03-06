<span>
    <h1>
        <img src="assets\logo_alpha.png" width="50"/>
        FixTweetBot
    </h1>
</span>

[![Top.gg Upvotes](https://top.gg/api/widget/upvotes/1164651057243238400.svg)](https://top.gg/bot/1164651057243238400)
[![Top.gg Servers](https://top.gg/api/widget/servers/1164651057243238400.svg)](https://top.gg/bot/1164651057243238400)
![last commit](https://img.shields.io/github/last-commit/Kyrela/FixTweetBot)
[![Crowdin](https://badges.crowdin.net/fixtweetbot/localized.svg)](https://crowdin.com/project/fixtweetbot)
[![GitHub Release](https://img.shields.io/github/v/release/Kyrela/FixTweetBot?style=flat)](https://github.com/Kyrela/FixTweetBot/releases/latest)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/Kyrela)](https://github.com/sponsors/Kyrela)

[![Invite link](https://img.shields.io/badge/Invite_link-blue)](https://discord.com/oauth2/authorize?client_id=1164651057243238400)
[![Support server](https://img.shields.io/badge/Support_server-green)](https://discord.gg/3ej9JrkF3U)
[![Discord App Directory](https://img.shields.io/badge/Discord_App_Directory-grey)](https://discord.com/application-directory/1164651057243238400)
[![Tog.gg](https://img.shields.io/badge/Tog.gg-fc3164)](https://top.gg/bot/1164651057243238400)


FixTweetBot is a Discord bot that fixes social media embeds,
using online services (such as [FxTwitter](https://github.com/FixTweet/FxTwitter))

In concrete terms, this bot automatically repost social media links as a 'fixed' version
that contains a better embed (that allows to play videos directly in Discord, for example).

![showcase](assets/showcase.png)

## Features & Highlights

- Supports Twitter, Nitter, Instagram, TikTok, Reddit, Threads, Bluesky, Pixiv, IFunny, Fur Affinity, YouTube, and
  any custom websites of your choice
- Tweets translation
- Disable by website, channel, member or role
- Highly customizable behavior and appearance
- Multiple languages supported
- Modern interface for settings
- Respect markdown
- Respect privacy
- Source-available

More infos on the '[comparison table](#comparison-with-other-bots)'.

## Usage

Simply send a message containing a compatible social media link, and the bot will remove the embed if any and
automatically repost it as a 'fixed' link.

![usage screenshot](assets/usage.png)

You also can ignore a link by putting it between `<` and `>`, like this: `<https://twitter.com/...>`.

You can manage the bot's settings with the `/settings` command.

![settings screenshot](assets/settings.gif)

Lastly, you can use the `/about` command any time to get more information about the bot and to get help.

## Add the bot to your server

You can add the bot to your server by clicking on the following
link: [Invite link](https://discord.com/oauth2/authorize?client_id=1164651057243238400)
or view it from the [Discord App Directory](https://discord.com/application-directory/1164651057243238400)

Please also consider upvoting the bot on [Tog.gg](https://top.gg/bot/1164651057243238400)!

The bot is also available on
[Discord Bots](https://discord.bots.gg/bots/1164651057243238400) and
[Discord Bot List](https://discord.ly/fixtweet).

## Comparison with other bots

|                                              | FixTweetBot                                                                                                                                                                                                                                                                                                                  | [LinkFix](https://github.com/podaboutlist/linkfix-for-discord)                                                                                       | [Dystopia](https://top.gg/bot/1038138572613619793)                                                | [EmbedEz](https://embedez.com)                                                                                     | [Nano Embedding](https://discord.com/application-directory/978552836105326592)                                                                                                               | [Keto](https://github.com/stekc/Keto-Bot)                                                                                                                    | [ComebackTwitterEmbed](https://top.gg/fr/bot/1161267455335862282)                                                            | [TweetFixer](https://top.gg/fr/bot/1177042905622396928) | [VxT](https://top.gg/fr/bot/1015497909925580830)                                             | [VXC/FixTwitter](https://top.gg/fr/bot/1162350583198515210)      | [Twitter Video Embeds](https://discord.com/application-directory/842601826674540574) | [Auto FxTwitter](https://discord.com/application-directory/1275895582220877855) |
|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|----------------------------------------------------------------------------------------------|------------------------------------------------------------------|--------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| Social medias supported                      | - Twitter (FxTwitter)<br/>- Nitter (FxTwitter)<br/>- Instagram (InstaFix)<br/>- TikTok (fxTikTok)<br/>- Reddit (FixReddit)<br/>- Threads (FixThreads)<br/>- Bluesky (VixBluesky)<br/>- Pixiv (phixiv)<br/>- IFunny (EmbedEZ)<br/>- Fur Affinity (xfuraffinity)<br/>- YouTube (Koutube)<br/>- Custom Websites (like Mastodon) | - Twitter (FxTwitter)<br/>- Youtube Shorts (Youtube)<br/>- TikTok (vxtiktok)<br/>- Instagram (InstaFix)<br/>- Reddit (vxreddit)<br/>- Pixiv (phixiv) | - Twitter (FxTwitter)<br/>- TikTok (vxtiktok)<br/>- Reddit (FixReddit)<br/>- Instagram (InstaFix) | - Twitter (EmbedEZ)<br/>- TikTok (EmbedEZ)<br/>- Instagram (EmbedEZ)<br/>- Reddit (EmbedEZ)<br/>- IFunny (EmbedEZ) | - Twitter (custom)<br/>- Bluesky (custom)<br/>- Instagram (custom)<br/>- TikTok (custom)<br/>- Pixiv (custom)<br/>- DevianArt (custom)<br/>- Fur Affinity (custom)<br/>- Newgrounds (custom) | - Twitter (FxTwitter)<br/>- TikTok (QuickVids) <br/>- Instagram (InstaFix)<br/>- Reddit (FixReddit/Custom)<br/>- Apple Music (Odesli)<br/>- Spotify (Odesli) | - Twitter (custom)                                                                                                           | - Twitter (FxTwitter)                                   | - Twitter (FxTwitter)<br/>- Instagram (InstaFix)<br/>- TikTok (tiktxk)<br/>- Custom Websites | - Twitter (FxTwitter/vxTwitter)                                  | - Twitter (Custom)<br/>- TikTok (Custom)<br/>- Reddit (Custom)                       | - Twitter (FxTwitter)                                                           |
| Ignore message by                            | - Channel<br/>- Role<br/>- Member                                                                                                                                                                                                                                                                                            | ❌                                                                                                                                                    | ❌                                                                                                 | ❌                                                                                                                  | ❌                                                                                                                                                                                            | ❌                                                                                                                                                            | - Channel<br/>- Role<br/>- Member<br/>- Keywords                                                                             | ❌                                                       | - Role<br/>- Member                                                                          | ❌                                                                | ❌                                                                                    | ❌                                                                               |
| Modifications on the base message            | - Nothing<br/>- Remove the embed<br/>- Delete the message                                                                                                                                                                                                                                                                    | ❌                                                                                                                                                    | - Delete the message                                                                              | ❌                                                                                                                  | - Remove the embed                                                                                                                                                                           | - Remove the embed                                                                                                                                           | - Nothing<br/>- Delete the message (if it contains only the link)                                                            | - Delete the message                                    | - Delete the message<br/>- Nothing                                                           | - Delete the message                                             | - Delete (only if using webhook, else nothing)                                       | - Remove the embed                                                              |
| Message method                               | - Reply (without mention)<br/>- Message                                                                                                                                                                                                                                                                                      | - Replying (without mention)                                                                                                                         | - Message                                                                                         | - Message                                                                                                          | - Reply                                                                                                                                                                                      | - Reply                                                                                                                                                      | - Reply<br/>- Message                                                                                                        | - Message                                               | - Message (as bot or using webhook)                                                          | - Message                                                        | - Reply<br/>- Message (using webhook)                                                | - Reply                                                                         |
| Message content                              | Fixed links in hypertext (view render can be customized)                                                                                                                                                                                                                                                                     | Fixed links                                                                                                                                          | Author + full message content with fixed links in hypertext                                       | Fixed link                                                                                                         | Embed, with a second embed containing the video if any.                                                                                                                                      | Fixed link                                                                                                                                                   | Embed with separated video, photos in the embed **or** as attachments                                                        | Author's mention + message content with fixed links     | Message content with fixed links                                                             | Author's mention + message content with fixed links in hypertext | Embeds with video as an attachment **or** only medias                                | Fixed links                                                                     |
| Respect markdown                             | ✔️                                                                                                                                                                                                                                                                                                                           | ❌                                                                                                                                                    | ❌                                                                                                 | ❌                                                                                                                  | ❌                                                                                                                                                                                            | ❌                                                                                                                                                            | ❌                                                                                                                            | ❌                                                       | ❌                                                                                            | ❌                                                                | ✔️                                                                                   | ❌                                                                               |
| Possibility for op to delete the bot's post  | ❌                                                                                                                                                                                                                                                                                                                            | ❌                                                                                                                                                    | ✔️                                                                                                | ❌                                                                                                                  | ✔️                                                                                                                                                                                           | ❌                                                                                                                                                            | ✔️                                                                                                                           | ❌                                                       | ✔️ (for everyone, vote-based)                                                                | ✔️                                                               | ✔️                                                                                   | ❌                                                                               |
| Other features and notes                     | - Custom websites<br/>- Posts translation (Twitter)<br/>- Embed customization (Twi, Bsky, TikTok)<br/>- 'Disable/Enable all' on filters<br/>- 'Disable/Enable by default' on filters<br/>- Troubleshoot system                                                                                                               | ❌                                                                                                                                                    | ❌                                                                                                 | - Website interface<br/>- Download system                                                                          | - False positive on already-fixed links                                                                                                                                                      | ❌                                                                                                                                                            | - Posts translation (Twitter)<br/>- Download videos (Twitter)<br/>- Tweet save<br/>- Customization<br/>- React to other bots | ❌                                                       | - Custom websites<br/>- Quote tweet settings<br/>- Posts translation (Twitter)               | ❌                                                                | - Download videos                                                                    | ❌                                                                               |
| Permissions asked                            | Minimum                                                                                                                                                                                                                                                                                                                      | Unused ones                                                                                                                                          | Unused ones **and** missing ones                                                                  | Unused ones **and** missing ones                                                                                   | Unused ones **and** missing ones                                                                                                                                                             | Minimum                                                                                                                                                      | Not enough                                                                                                                   | Not enough                                              | Extremely abusive, for privacy and security                                                  | Administrator (real risk)                                        | Not enough                                                                           | Not enough                                                                      |
| Languages                                    | en, fr ([contribute to add more!](https://crowdin.com/project/fixtweetbot))                                                                                                                                                                                                                                                  | ➖                                                                                                                                                    | en                                                                                                | en                                                                                                                 | en                                                                                                                                                                                           | en                                                                                                                                                           | jp                                                                                                                           | en                                                      | en                                                                                           | jp                                                               | en                                                                                   | en                                                                              |
| Open-sourced                                 | Source-available                                                                                                                                                                                                                                                                                                             | ✔️                                                                                                                                                   | ❌                                                                                                 | ❌                                                                                                                  | ❌                                                                                                                                                                                            | ✔️                                                                                                                                                           | ❌                                                                                                                            | ❌                                                       | ❌                                                                                            | ❌                                                                | ❌                                                                                    | ❌                                                                               |
| Business model                               | Freemium                                                                                                                                                                                                                                                                                                                     | Free                                                                                                                                                 | Free                                                                                              | Freemium                                                                                                           | Free, donations accepted                                                                                                                                                                     | Free                                                                                                                                                         | Free                                                                                                                         | Free                                                    | Free                                                                                         | Free                                                             | Free                                                                                 | Free                                                                            |
| Server count                                 | ![Top.gg Servers](https://top.gg/api/widget/servers/1164651057243238400.svg)                                                                                                                                                                                                                                                 | 2.3K (07/09/24)                                                                                                                                      | 1.4K (07/09/24)                                                                                   | 2.5K (07/09/24)                                                                                                    | 3.8K (07/09/24)                                                                                                                                                                              | 14k (28/2/24)                                                                                                                                                | 8.3K (07/09/24)                                                                                                              | ➖                                                       | ➖                                                                                            | ➖                                                                | 9.1K (07/09/24)                                                                      | 11 (07/09/24)                                                                   |
| ____________________________________________ | _____________________________________________                                                                                                                                                                                                                                                                                | __________________________                                                                                                                           | ___________________________________                                                               | ___________________________________                                                                                | ________________________________________                                                                                                                                                     | _______________________________                                                                                                                              | ____________________________________________________                                                                         | ________________________________                        | ________________________________________________                                             | ________________________________________                         | _________________________________                                                    | _______________________                                                         |

_Do you know of another similar bot that is not included here? Feel free to open an issue!_

## Get help

If you need help, you can join the [support server](https://discord.gg/3ej9JrkF3U) or open an issue.

## Self-hosting

Simply install Python >= 3.10, clone the repository, and run `pip install -r requirements.txt`.

Be sure to have a database set up using MySQL.

Then, create a `override.config.yml` file containing the following:

```yaml
token: <your_personal_token>
dev_guild: <your_personnal_guild_id> # optional, for dev commands

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

## Help & Contributing

If you want to help, first of all, thank you! There are many ways to contribute:

### Money

You can buy the [premium version of the bot](
https://discord.com/application-directory/1164651057243238400/store/1260699263755751456), that will give you access to
more features and will help me to keep the bot running.

You can also simply [donate or sponsor me using GitHub Sponsors](https://github.com/sponsors/Kyrela), you'll get cool
little rewards, and you can even have your name displayed on the readme, and it will help me to keep the bot running.

### Contributing

You can help to [translate the bot into your language on Crowdin](https://crowdin.com/project/fixtweetbot).

If you're a developer, you can help by fixing bugs, adding new features, or improving the code quality by opening a
[Pull Request](https://github.com/Kyrela/FixTweetBot/pulls).

### Vote

You can [leave a star on the GitHub repository](https://github.com/Kyrela/FixTweetBot).

You can also [review the bot on Top.gg](https://top.gg/bot/1164651057243238400#reviews) and [vote for it](
https://top.gg/bot/1164651057243238400/vote).

Finally, you can also [upvote the bot on Discord Bot List](https://discordbotlist.com/bots/fixtweet/upvote).

## Links

- [Source code](https://github.com/Kyrela/FixTweetBot) (please leave a star!)
- [Discord App Directory page](https://discord.com/application-directory/1164651057243238400)
- [Top.gg page](https://top.gg/bot/1164651057243238400) (please leave an upvote!)
- [Support server](https://discord.gg/3ej9JrkF3U)
- [Translations on Crowdin](https://crowdin.com/project/fixtweetbot)
- [Invite link](https://discord.com/oauth2/authorize?client_id=1164651057243238400)
- [Discord Bots page](https://discord.bots.gg/bots/1164651057243238400)
- [Discord Bot List page](https://discord.ly/fixtweet)

## Awesome fixers

Here's, for the record, a non-exhaustive list of the fixers/proxies spotted in the wild:
- Twitter
  - [FxTwitter • fxtwitter.com](https://github.com/FixTweet/FxTwitter) *Used by FixTweetBot*
    - Other official public instances/redirects: `fixupx.com`, `twittpr.com`
    - Other unofficial public instances/redirects: `girlcockx.com`, `hitlerx.com`, `peepeepoopoodumdumtwitterx.org`, `skibidix.com`, `yiffx.com`, `imthehottest18yearoldononlyfansx.com` (http only)
  - [BetterTwitFix • vxtwitter.com](https://github.com/dylanpdx/BetterTwitFix)
    - Other official public instances/redirects: `fixvx.com`
    - Other unofficial public instances/redirects: `stupidpenisx.com`
  - [EmbedEZ • twitterez.com](https://embedez.com)
- Instagram
  - [InstaFix • ddinstagram.com](https://github.com/Wikidepia/InstaFix)
  - [kkinstagram • kkinstagram.com](https://kkinstagram.com)
  - [EmbedEZ • instagramez.com](https://embedez.com) *Used by FixTweetBot*
  - [fxinstagram • fxig.seria.moe](https://fxig.seria.moe)
- TikTok
  - [fxTikTok • tnktok.com](https://github.com/okdargy/fxtiktok) *Used by FixTweetBot*
  - [vxtiktok • vxtiktok.com](https://github.com/dylanpdx/vxtiktok)
  - [tiktxk • tiktxk.com](https://github.com/Britmoji/tiktxk)
  - [FxTikTok • tfxktok.com](https://tfxktok.com/)
  - [EmbedEZ • tiktokez.com](https://embedez.com)
- Reddit
  - [FixReddit • rxddit.com](https://github.com/MinnDevelopment/fxreddit) *Used by FixTweetBot*
  - [vxreddit • vxreddit.com](https://github.com/dylanpdx/vxReddit)
  - [s/e/xy Reddit • rxyddit.com](https://github.com/NurMarvin/sexy-reddit)
  - [EmbedEZ • redditez.com](https://embedez.com)
- Facebook
  - [EmbedEZ • facebookez.com](https://embedez.com) *Used by FixTweetBot*
  - [fxfacebook • fxfb.seria.moe](https://github.com/seriaati/fxfacebook)
- Bilibili
  - [EmbedEZ • bilibliez.com](https://embedez.com) *Used by FixTweetBot*
  - [fxBilibili fxbilibili.seria.moe](https://github.com/seriaati/fxBilibili)
- Threads
  - [FixThreads • fixthreads.net](https://github.com/milanmdev/fixthreads) *Used by FixTweetBot*
  - [vxThreads • vxthreads.net](https://github.com/everettsouthwick/vxThreads)
- Pixiv
  - [phixiv • phixiv.net](https://github.com/thelaao/phixiv) *Used by FixTweetBot*
    - Other official public instances/redirects: `ppxiv.net`
- IFunny
  - [EmbedEZ • ifunnyez.co](https://embedez.com) *Used by FixTweetBot*
- YouTube
  - [Koutube • koutube.com](https://github.com/iGerman00/koutube) *Used by FixTweetBot*
  - [youtube-discord-embed • yt.cdn.13373333.one](https://github.com/ray-1337/youtube-discord-embed/)
- Twitch
  - [fxtwitch • fxtwitch.seria.moe](https://github.com/seriaati/fxtwitch)
- Bluesky
  - [VixBluesky • bskx.app](https://github.com/Lexedia/VixBluesky) *Used by FixTweetBot*
    - Other official public instances/redirects: `bskyx.app` (deprecated)
    - Other unofficial public instances/redirects: `girlcockbsky.app` (nsfw content)
  - [FixBluesky • bsyy.app](https://github.com/ThornbushHQ/FixBluesky)
  - [xbsky • xbsky.app](https://github.com/colduw/xbsky)
  - [FxBluesky • fxbsky.app](https://bsky.app/profile/fxbsky.app)
  - [bskye • bskye.app](https://github.com/FerroEduardo/bskye)
  - [cbsky.app • cbsky.app](https://github.com/goeo-/cbsky.app)
  - [bsky-viewer • bsky-viewer.branchpanic.workers.dev](https://github.com/branchpanic/bsky-viewer)
- Roblox
  - [Rxblox2 • fixroblox.com](https://github.com/vys69/Rxblox2)
- Snapchat
  - [EmbedEZ • snapchatez.com](https://embedez.com) *Used by FixTweetBot*
- Spotify
  - [fxspotify • fxspotify.com](https://github.com/dotconnexion/fxspotify)
  - [FixSpotify • fixspotify.com](https://github.com/gurrrrrrett3/fixspotify)
- Furaffinity
  - [xfuraffinity • xfuraffinity.net](https://github.com/FirraWoof/xfuraffinity) *Used by FixTweetBot*
  - [fxraffinity • fxraffinity.net](https://github.com/kheina-com/fxraffinity)
    - Other official public instances/redirects: `fxfuraffinity.net`
  - [fxraffinity • fxraffinity.net](https://fxraffinity.net/)
- DeviantArt
  - [fixDeviantArt • fixdeviantart.com](https://github.com/Tschrock/fixdeviantart) *Used by FixTweetBot*
  - [fxDeviantArt • fxdeviantart.com](https://github.com/daisyUniverse/fxdeviantart)
- Iwara (nsfw content)
  - [fxiwara • fxiwara.seria.moe](https://github.com/seriaati/fxiwara)
- Mastodon
  - [FxMastodon • fx.zillanlabs.tech](https://fx.zillanlabs.tech/) *Used by FixTweetBot*
  - [FxMastodon • fxmas.to](https://github.com/Someguy123/fxmastodon)
  - [FxMastodon • fx.sizecraft.social](https://fx.sizecraft.social/)
- Tumblr
  - [fxtumblr • tpmblr.com](https://github.com/knuxify/fxtumblr) *Used by FixTweetBot*
  - [TxTumblr • txtumblr.com](https://github.com/MarkSuckerberg/txtumblr)
- Misskey
  - [FxMastodon • fx.sizecraft.social](https://fx.sizecraft.social/)

_Do you know of another proxy that is not included here? Feel free to open an issue!_

## Credits

### Proxies

Nothing would be possible without the proxies that allow the bot to access the internet. Don't hesitate to support them!

> [!NOTE]
We're not affiliated with any of these services.

- [FxTwitter](https://github.com/FixTweet/FxTwitter)
- [fxTikTok](https://github.com/okdargy/fxTikTok)
- [FixReddit](https://github.com/MinnDevelopment/fxreddit)
- [FixThreads](https://github.com/milanmdev/fixthreads)
- [VixBluesky](https://github.com/Lexedia/VixBluesky)
- [phixiv](https://github.com/thelaao/phixiv)
- [EmbedEZ](https://embedez.com)
- [xfuraffinity](https://github.com/FirraWoof/xfuraffinity)
- [Koutube](https://github.com/iGerman00/koutube)


### Dependencies

The bot is built on top of the following libraries:

- [discore](https://github.com/Kyrela/discore)
- [python-i18n](https://github.com/danhper/python-i18n)
- [psutil](https://github.com/giampaolo/psutil)
- [requests](https://github.com/psf/requests)
- [masonite-orm](https://github.com/MasoniteFramework/orm)
- [PyMySQL](https://github.com/PyMySQL/PyMySQL)
- [discord-markdown-ast-parser](https://github.com/Vioshim/discord-markdown-ast-parser)
- [Top.gg python-sdk](https://github.com/null8626/python-sdk/tree/patch-1)
