# Embed fixer list

A list of every embed fixer (or proxy) found that rewrites links from social platforms and media sites
so that Discord and similar apps display a better embed (playable video, full-resolution images, stats, etc).

Each section covers one platform and lists the fixers that support it: the project link, its main domain, and any
official or unofficial alternative domains. Entries marked "_Used by FixTweetBot_" are the ones this bot relies on.
Some platforms also include a collapsible **Comparison table** of the link types each fixer handles (may not be up to date).
A **Deprecated** section records services that no longer work.

> [!WARNING]
> Fixers and/or the websites they link to may contain NSFW content, hate slurs, or other undesirable material.

> [!TIP]
> This list is part of the [FixTweetBot](https://github.com/Kyrela/FixTweetBot) project. If you'd rather not fix
> links by hand, you can use FixTweetBot to do it automatically in Discord.

> [!NOTE]
> Are you aware of any other fixer that isn't included here? Feel free to open an issue!

## <img src="assets/twitter.webp" alt="Twitter" height="20"/> Twitter
- [FxTwitter • fxtwitter.com](https://github.com/FixTweet/FxTwitter) *Used by FixTweetBot*
  - Other official public instances/redirects: `fixupx.com`, `twittpr.com`
  - Other unofficial public instances/redirects: `girlcockx.com`, `hitlerx.com`, `peepeepoopoodumdumtwitterx.org`, `skibidix.com`, `yiffx.com`, `imthehottest18yearoldononlyfansx.com`, `cunnyx.com`, `boycuntx.com`, `autistic.kids`, `yaoisex.com`, `niggerfaggotx.com`, `gockx.com`, `boypussyx.com`, `forsenx.com`, `ucobx.com`, `catgirlsex.com`, `catgirlx.com`, `epsteinx.com`, `femboysx.com`, `hotfemboysex.com`, `lilgayboy45.com`
- [BetterTwitFix • vxtwitter.com](https://github.com/dylanpdx/BetterTwitFix)
  - Other official public instances/redirects: `fixvx.com`
  - Other unofficial public instances/redirects: `stupidpenisx.com`, `hotyurisex.com` (nsfw content), `mpregx.com`, `furryfeetx.com`, `faggotx.com`
- [teapot • No official instance](https://github.com/amaanq/teapot)
  - Unofficial public instances: `goyimx.com`
- [EmbedEZ • twitterez.com](https://embedez.com)
  - Other official public instances/redirects: `jobna.me`, `xeezz.com`
- [Embeds.now • embeds.now/twitter.com](https://embeds.now)
  - Other official public instances/redirects: `embeds.now/x.com`, `x.embeds.now`, `tw.embeds.now`
- [mbedfx • mbedfx.app/x](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
- [FixEmbed • fixembed.app/x](https://github.com/kenhendricks00/FixEmbed)
  - Other official public instances/redirects: `fixembed.app/twitter`, `fixembed.app/embed?url=`
<details>
  <summary>Deprecated</summary>

- [TwitFix • fxtwitter.com](https://github.com/daisyUniverse/TwitFix)
</details>

## <img src="assets/instagram.webp" alt="Instagram" height="20"/> Instagram
- [OGInstagram • oginstagram.com](https://github.com/seirenkr/OGInstagram) *Used by FixTweetBot*
- [InstagramEmbed • vxinstagram.com](https://github.com/Lainmode/InstagramEmbed-vxinstagram)
  - Other unofficial public instances/redirects: `fxig.seria.moe`, `ins.so`
- [InstaFix Revived • instagram7.com](https://github.com/Bl0ck154/InstaFix-Revived)
- [kkScript • kkinstagram.com](https://kkscript.com)
- [InstaFix • official instance deprecated](https://github.com/Wikidepia/InstaFix)
  - Other unofficial public instances/redirects: `uuinstagram.com`, `eeinstagram.com`, `instafix.zzinstagram.com`, `onebigram.com`, `iaxxis.gay`
- [Instagram embedding proxy • zzinstagram.com](https://github.com/Knoppiix/InstaEmbedRouter) (load balancer between multiple fixers)
- [InstaFix • toinstagram.com](https://toinstagram.com/)
- [FXInstagram • ig.mynameistito.com](https://github.com/mynameistito/fxinstagram)
- [FxInstagram • xnstagram.com](https://xnstagram.com/)
- [FXinstagram • fxinstagram.com](https://fxinstagram.com)
- [Embeds.now • embeds.now/instagram.com](https://embeds.now)
  - Other official public instances/redirects: `kirkstagram.com`, `instagramfix.com`, `embeds.now`, `i.embeds.now`, `ig.embeds.now`
- [mbedfx • mbedfx.app/ig](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
- [FixEmbed • fixembed.app/ig](https://github.com/kenhendricks00/FixEmbed)
  - Other official public instances/redirects: `fixembed.app/instagram`, `fixembed.app/embed?url=`
<details>
  <summary>Comparison table</summary>

| Link type / Feature                                          | [OGInstagram](https://github.com/seirenkr/OGInstagram) | [InstagramEmbed](https://github.com/Lainmode/InstagramEmbed-vxinstagram) | [InstaFix Revived](https://github.com/Bl0ck154/InstaFix-Revived) | [kkScript](https://kkscript.com)              | [InstaFix](https://github.com/Wikidepia/InstaFix) instances | Link example                                                       |
  |--------------------------------------------------------------|--------------------------------------------------------|--------------------------------------------------------------------------|------------------------------------------------------------------|-----------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------------------|
| `/p/:hash` (photo)                                           | ✔️                                                     | ✔️                                                                       | ➖ First image duplicated                                        | ➖ Ignore image index, display only the first | ➖ No image (just text)                                     | https://www.instagram.com/p/DKMv_h9o_Oj                            |
| `/p/:hash?img_index=:img_index` (photo with index)           | ✔️                                                     | ➖ Wrong image index (+1)                                                | ✔️                                                               | ➖ Ignore image index, display only the first | ➖ No image (just text)                                     | https://www.instagram.com/p/DKMv_h9o_Oj/?img_index=2               |
| `/:username/p/:hash` (photo)                                 | ✔️                                                     | ✔️                                                                       | ➖ First image duplicated                                        | ➖ Ignore image index, display only the first | ➖ No image (just text)                                     | https://www.instagram.com/grimkujow/p/DKMv_h9o_Oj                  |
| `/:username/p/:hash?img_index=:img_index` (photo with index) | ✔️                                                     | ➖ Wrong image index (+1)                                                | ✔️                                                               | ➖ Ignore image index, display only the first | ➖ No image (just text)                                     | https://www.instagram.com/grimkujow/p/DKMv_h9o_Oj/?img_index=2     |
| `/p/:hash` (video)                                           | ✔️                                                     | ✔️                                                                       | ✔️                                                               | ✔️                                            | ✔️                                                          | https://www.instagram.com/p/C73Fe0oh_rV/?hl=fr                     |
| `/:username/p/:hash` (video)                                 | ✔️                                                     | ✔️                                                                       | ✔️                                                               | ✔️                                            | ✔️                                                          | https://www.instagram.com/12love_of_life_/p/C73Fe0oh_rV/?hl=fr     |
| `/share/:hash`                                               | ❌                                                     | ✔️                                                                       | ❌                                                               | ✔️                                            | ❌                                                          | https://www.instagram.com/share/_a7bsO89b                          |
| `/share/reel/:hash`                                          | ❌                                                     | ✔️                                                                       | ✔️                                                               | ❌                                            | ✔️                                                          | https://www.instagram.com/share/reel/_gdkGEJBn                     |
| `/share/p/:hash`                                             | ❌                                                     | ✔️                                                                       | ➖ Display only the first image                                  | ❌                                            | ➖ Just text, and not eeinstagram                           | https://www.instagram.com/share/p/BBFVaX2n1Y                       |
| `/reels/:hash`                                               | ✔️                                                     | ✔️                                                                       | ✔️                                                               | ✔️                                            | ✔️                                                          | https://www.instagram.com/reels/C6bfaFzIqqR/?hl=fr                 |
| `/reel/:hash`                                                | ✔️                                                     | ✔️                                                                       | ✔️                                                               | ✔️                                            | ✔️                                                          | https://www.instagram.com/reel/C6bfaFzIqqR/?hl=fr                  |
| `/:username/reel/:hash`                                      | ✔️                                                     | ✔️                                                                       | ✔️                                                               | ✔️                                            | ✔️                                                          | https://www.instagram.com/olafurw/reel/C6bfaFzIqqR/?hl=fr          |
| `/stories/:username/:id`                                     | ✔️                                                     | ❌                                                                       | ✔️                                                               | ❌                                            | ➖ Not eeinstagram                                          | / (Links expire after 24h)                                         |
| `/stories/highlights/:id`                                    | ❌                                                     | ❌                                                                       | ❌                                                               | ❌                                            | ❌                                                          | https://www.instagram.com/stories/highlights/18011779940152346/    |
| `/:username`                                                 | ✔️                                                     | ❌                                                                       | ❌                                                               | ❌                                            | ❌                                                          | https://www.instagram.com/grimkujow                                |
| `/:username/reels`                                           | ❌                                                     | ❌                                                                       | ❌                                                               | ❌                                            | ❌                                                          | https://www.instagram.com/grimkujow/reels/                         |
| `/:username/tagged`                                          | ❌                                                     | ❌                                                                       | ❌                                                               | ❌                                            | ❌                                                          | https://www.instagram.com/grimkujow/tagged/                        |
| `/explore/search/keyword?q=:q`                               | ❌                                                     | ❌                                                                       | ❌                                                               | ❌                                            | ❌                                                          | https://www.instagram.com/explore/search/keyword/?q=%23photography |
| NSFW Content                                                 | ✔️                                                     | ✔️                                                                       | ❌                                                               | ❌                                            | ❌                                                          | https://www.instagram.com/p/BoRbLA1gl0o/?hl=fr                     |
| Translation                                                  | ❌                                                     | ❌                                                                       | ❌                                                               | ❌                                            | ❌                                                          | /                                                                  |
| Normal view                                                  | ✔️                                                     | ❌                                                                       | ✔️                                                               | ❌                                            | ✔️                                                          | /                                                                  |
| Direct view                                                  | ✔️                                                     | ✔️                                                                       | ❌                                                               | ✔️                                            | ➖ Not garanteed                                            | /                                                                  |
| Gallery view                                                 | ✔️                                                     | ❌                                                                       | ❌                                                               | ❌                                            | ➖ Not garanteed                                            | /                                                                  |
| Text view                                                    | ❌                                                     | ❌                                                                       | ❌                                                               | ❌                                            | ❌                                                          | /                                                                  |

> Instagram Embedding Proxy (zzinstagram.com) is a load balancer between multiple fixers, so it isn't predictive and isn't included in the table.
> Tested the 27/07/2026
</details>
<details>
  <summary>Deprecated</summary>

- [InstaFix • ddinstagram.com](https://github.com/Wikidepia/InstaFix)
  - Other unofficial public instances/redirects: `fxstagram.com`
- [EmbedEZ • instagramez.com](https://embedez.com)
  - Other official public instances/redirects: `g.embedez.com`
- [fxinstagram • fxig.seria.moe](https://fxig.seria.moe)
- [Instagram Embed Fixer • gginstagram.com](https://github.com/ThePotato97/InstaFixerCF)
</details>

## <img src="assets/tiktok.webp" alt="TikTok" height="20"/> TikTok
- [fxTikTok • tnktok.com](https://github.com/okdargy/fxtiktok) *Used by FixTweetBot*
- [tiktxk • tiktxk.com](https://github.com/Britmoji/tiktxk)
- [FxTikTok • tfxktok.com](https://tfxktok.com/)
- [EmbedEZ • tiktokez.com](https://embedez.com)
- [kkScript • kktiktok.com](https://kkscript.com)
- [FixTikTok • fixtiktok.com](https://github.com/Xetera/fixtiktok)
- [Embeds.now • embeds.now/tiktok.com](https://embeds.now)
  - Other official public instances/redirects: `embeds.now/vm.tiktok.com`, `tt.embeds.now`, `vm.embeds.now`, `vt.embeds.now`
- [mbedfx • mbedfx.app/tt](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
- [FixEmbed • fixembed.app/embed?url=](https://github.com/kenhendricks00/FixEmbed)
<details>
  <summary>Deprecated</summary>

- [vxtiktok • vxtiktok.com](https://github.com/dylanpdx/vxtiktok)
- [Fix Tiktok • fxtiktok.herokuapp](https://github.com/biggant1/fixtiktok)
</details>

## <img src="assets/reddit.webp" alt="Reddit" height="20"/> Reddit
- [FixReddit • rxddit.com](https://github.com/MinnDevelopment/fxreddit)
  - Other unofficial public instances/redirects: `fxreddit.seria.moe`
- [vxreddit • vxreddit.com](https://github.com/dylanpdx/vxReddit) *Used by FixTweetBot*
- [s/e/xy Reddit • rxyddit.com](https://github.com/NurMarvin/sexy-reddit)
- [EmbedEZ • redditez.com](https://embedez.com)
- [Embeds.now • embeds.now/reddit.com](https://embeds.now)
  - Other official public instances/redirects: `embeds.now/redd.it`, `r.embeds.now`, `rd.embeds.now`
- [mbedfx • mbedfx.app/rd](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
- [FixEmbed • fixembed.app/reddit](https://github.com/kenhendricks00/FixEmbed)
  - Other official public instances/redirects: `fixembed.app/embed?url=`
<details>
  <summary>Comparison table</summary>

| Link type / Feature                                    | [FixReddit](https://github.com/MinnDevelopment/fxreddit) | [vxreddit](https://github.com/dylanpdx/vxReddit)  | [s/e/xy Reddit](https://github.com/NurMarvin/sexy-reddit) | [EmbedEZ](https://embedez.com) | Link example                                                                                                                                                                                     |
  |--------------------------------------------------------|----------------------------------------------------------|---------------------------------------------------|-----------------------------------------------------------|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `r/:subreddit`                                         | ✔️                                                       | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/r/tipofmytongue/                                                                                                                                                          |
| `/r/:subreddit/comments/:hash/:slug` (photo)           | ✔️                                                       | ✔️                                                | ✔️                                                        | ✔️                             | https://reddit.com/r/shittymoviedetails/comments/160onpq/breaking_actor_from_home_alone_2_arrested_today                                                                                         |
| `/r/:subreddit/comments/:hash/:slug` (multiple photos) | ✔️                                                       | ✔️                                                | ❌                                                        | ✔️                             | https://www.reddit.com/r/trucsmoches/comments/1ldhq8j/série_de_chapeaux_moches_lequel_est_votre_préféré/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button |
| `/r/:subreddit/comments/:hash/:slug` (text only)       | ➖ No hyperlink for subreddits                           | ➖ No hyperlink for subreddits                    | ➖ No hyperlink for subreddits                            | ✔️                             | https://www.reddit.com/r/place/comments/15d263v/i_analysed_rplace_2023_dataset_here_is_what_i/?utm_source=share&utm_medium=android_app&utm_name=androidcss&utm_term=1&utm_content=1              |
| `/r/:subreddit/comments/:hash/:slug` (deleted)         | ✔️                                                       | ✔️                                                | ✔️                                                        | ✔️                             | https://www.reddit.com/r/AceAttorney/comments/1kbb3h2/what_do_you_think_are_some_of_the_creepiest/                                                                                               |
| `/r/:subreddit/comments/:hash/:slug` (gif)             | ✔️                                                       | ✔️                                                | ✔️                                                        | ✔️                             | https://www.reddit.com/r/gifs/comments/1mn9i6z/big_pupper_with_more_to_love/                                                                                                                     |
| `/r/:subreddit/comments/:hash/:slug` (video)           | ➖ No video sound                                        | ✔️                                                | ❌                                                        | ✔️                             | https://www.reddit.com/r/SipsTea/comments/1ifj2nc/rock_paper_scissors_is_a_big_event_in_japan/                                                                                                   |
| `/r/:subreddit/comments/:hash/:slug` (crosspost)       | ➖ Don't show the OG post                                | ➖ Don't show the OG post                         | ➖ Don't show the OG post                                 | ➖ Show the image twice        | https://www.reddit.com/r/Firearms/comments/t4f6rm/never_be_disarmed/                                                                                                                             |
| `/r/:subreddit/comments/:hash/:slug` (link)            | ➖ Don't show the link                                   | ➖ Don't show embedded content, no hypertext link | ❌                                                        | ➖ Don't show the link         | https://www.reddit.com/r/france/comments/1mmr0xa/on_rcollapse_people_are_kept_abreast_of_the/                                                                                                    |
| `/r/:subreddit/comments/:hash/:slug` (poll)            | ➖ Only show poll choices and vote number                | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/r/polls/comments/1mnic4n/what_videogame_has_the_best_soundtracks/                                                                                                         |
| `/r/:subreddit/comments/:hash`                         | ✔️                                                       | ✔️                                                | ❌                                                        | ✔️                             | https://reddit.com/r/shittymoviedetails/comments/160onpq                                                                                                                                         |
| `/r/:subreddit/comments/:hash/:slug/:comment_hash`     | ✔️                                                       | ➖ Show OG post                                   | ❌                                                        | ➖ Show OG post                | https://reddit.com/r/shittymoviedetails/comments/160onpq/breaking_actor_from_home_alone_2_arrested_today/jxnkq4g                                                                                 |
| `/r/:subreddit/s/:hash`                                | ✔️                                                       | ✔️                                                | ❌                                                        | ✔️                             | https://reddit.com/r/MemePiece/s/15w6vzg82W                                                                                                                                                      |
| `/:hash`                                               | ✔️                                                       | ❌                                                | ❌                                                        | ❌                             | https://reddit.com/160onpq                                                                                                                                                                       |
| `/media?url=:url`                                      | ❌                                                       | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/media?url=https%3A%2F%2Fi.redd.it%2F5ua5ucs3tdif1.jpeg                                                                                                                    |
| `/:hash_media`                                         | ❌                                                       | ❌                                                | ❌                                                        | ❌                             | https://i.redd.it/5ua5ucs3tdif1.jpeg                                                                                                                                                             |
| `/user/:username`                                      | ✔️                                                       | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/user/battlefield/                                                                                                                                                         |
| `/user/:username/comments/:hash/:slug`                 | ❌                                                       | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/user/AUTOMATA88/comments/1ifj2nc/rock_paper_scissors_is_a_big_event_in_japan/                                                                                             |
| `/user/:username/comments/:hash`                       | ❌                                                       | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/user/AUTOMATA88/comments/1ifj2nc                                                                                                                                          |
| `/u/:username`                                         | ✔️                                                       | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/u/battlefield/                                                                                                                                                            |
| `/u/:username/comments/:hash/:slug`                    | ❌                                                       | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/u/AUTOMATA88/comments/1ifj2nc/rock_paper_scissors_is_a_big_event_in_japan/                                                                                                |
| `/u/:username/comments/:hash`                          | ❌                                                       | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/u/AUTOMATA88/comments/1ifj2nc                                                                                                                                             |
| `/mod/:subreddit/rules`                                | ❌                                                       | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/mod/tipofmytongue/rules/                                                                                                                                                  |
| `/r/:subreddit/wiki/:page`                             | ➖ Show the subreddit description                        | ❌                                                | ❌                                                        | ❌                             | https://www.reddit.com/r/unixporn/wiki/index                                                                                                                                                     |
| Translation                                            | ❌                                                       | ❌                                                | ❌                                                        | ✔️                             | /                                                                                                                                                                                                |
| Normal view                                            | ✔️                                                       | ✔️                                                | ✔️                                                        | ✔️                             | /                                                                                                                                                                                                |
| Direct view                                            | ❌                                                       | ❌                                                | ❌                                                        | ✔️                             | /                                                                                                                                                                                                |
| Gallery view                                           | ❌                                                       | ❌                                                | ❌                                                        | ❌                             | /                                                                                                                                                                                                |
| Text view                                              | ❌                                                       | ❌                                                | ❌                                                        | ❌                             | /                                                                                                                                                                                                |

> Tested the 12/08/2025
</details>
<details>
  <summary>Deprecated</summary>

- [RedditEmbedFix • redditfx.com](https://github.com/Matthbo/RedditEmbedFix)
</details>

## <img src="assets/facebook.webp" alt="Facebook" height="20"/> Facebook
- [fxfacebook • fxfb.seria.moe](https://github.com/seriaati/fxfacebook)
- [facebed • facebed.com](https://github.com/4pii4/facebed)
  - Other unofficial public instances/redirects: `drhong.ddns.net:9812` (http only), `facebed.seria.moe` *Used by FixTweetBot*
- [Embeds.now • embeds.now/facebook.com](https://embeds.now)
  - Other official public instances/redirects: `embeds.now/fb.watch`, `fb.embeds.now`, `fw.embeds.now`
- [mbedfx • mbedfx.app/fb](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
<details>
  <summary>Comparison table</summary>

| Link type                                        | [Facebed](https://github.com/4pii4/facebed) | [fxfacebook](https://github.com/seriaati/fxfacebook) | Link example                                                                                                                                                  |
  |--------------------------------------------------|---------------------------------------------|------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/:username/posts/:slug/:id`                     | ✔️                                          | ❌                                                   | https://www.facebook.com/PhucLongPremium87XuanThuy/posts/inspiring-workspace-phuc-long-premium-một-không-gian-làm-việc-được-tạo-nên-để-bạ/122223830864155872/ |
| `/:username/posts/:hash`                         | ✔️                                          | ❌                                                   | https://www.facebook.com/tiemcaphetovo/posts/pfbid02Aggw4udS1dFnwrK4J5mcZ6aLZZyi1zakSckDTLC4NEgYFqwCsaJqqHiukbzrWMt1l                                         |
| `/:username/videos/:id`                          | ✔️                                          | ❌                                                   | https://www.facebook.com/SansoneDeejay/videos/271051965695290                                                                                                 |
| `/marketplace/item/:marketplace_id`              | ❌                                          | ❌                                                   | https://www.facebook.com/marketplace/item/1099705522062104/                                                                                                   |
| `/share/r/:hash`                                 | ✔️                                          | ❌                                                   | https://www.facebook.com/share/r/15B1URzika/                                                                                                                  |
| `/share/p/:hash`                                 | ❌                                          | ❌                                                   | https://www.facebook.com/share/p/C3DxyLM3Bf8R8a3u/                                                                                                            |
| `/share/v/:hash`                                 | ✔️                                          | ❌                                                   | https://www.facebook.com/share/v/1GdMNgXLSG/                                                                                                                  |
| `/share/:hash`                                   | ✔️                                          | ❌                                                   | https://facebook.com/share/1GdMNgXLSG/                                                                                                                        |
| `/reel/:id`                                      | ✔️                                          | ❌                                                   | https://www.facebook.com/reel/588109690402315                                                                                                                 |
| `/photo?fbid=:fbid`                              | ✔️                                          | ❌                                                   | https://www.facebook.com/photo/?fbid=1220500346751179                                                                                                         |
| `/photo.php?fbid=:fbid`                          | ✔️                                          | ❌                                                   | https://www.facebook.com/photo.php/?fbid=1220500346751179                                                                                                     |
| `/watch?v=:v`                                    | ✔️                                          | ❌                                                   | https://www.facebook.com/watch/?v=1481060365360701                                                                                                            |
| `/:hash`                                         | ❌                                          | ❌                                                   | https://fb.watch/B4Qtd0WLlk/                                                                                                                                  |
| `/story.php?story_fbid=:story_fbid&id=:id`       | ❌                                          | ❌                                                   | https://www.facebook.com/story.php?story_fbid=457992036868931&id=100079744151043                                                                              |
| `/stories/:id/:hash`                             | ❌                                          | ❌                                                   | https://www.facebook.com/stories/102075155260376/UzpfSVNDOjE0NDM5NzA0ODM0MjIxNTM=/                                                                            |
| `/permalink.php?story_fbid=:story_fbid&id=:id`   | ✔️                                          | ❌                                                   | https://www.facebook.com/permalink.php?story_fbid=pfbid0q6xWiU8EYzdkmwWKzYLu8PHQWkWsmPLDc5AGb9xUuygKuCyV2rL3uf1YTPL1b4z2l&id=61568885281801                   |
| `/events/s/:slug/:id`                            | ❌                                          | ❌                                                   | https://facebook.com/events/s/sbk-xperience-cours-et-soiree-/3974856429449647                                                                                 |
| `/groups/:id`                                    | ❌                                          | ❌                                                   | https://facebook.com/groups/364997627165697                                                                                                                   |
| `/groups/:id?multi_permalinks=:multi_permalinks` | ✔️                                          | ❌                                                   | https://facebook.com/groups/364997627165697/?multi_permalinks=2845630405769061&hoisted_section_header_type=recently_seen                                      |
| `/groups/:id/posts/:hash`                        | ✔️                                          | ❌                                                   | https://www.facebook.com/groups/1495321534752609/posts/1796616717956421/                                                                                      |
| `/groups/:id/permalink/:hash`                    | ✔️                                          | ❌                                                   | https://www.facebook.com/groups/1495321534752609/permalink/1796616717956421/                                                                                  |
| Translation                                      | ❌                                          | ❌                                                   | /                                                                                                                                                             |
| Normal view                                      | ✔️                                          | ✔️                                                   | /                                                                                                                                                             |
| Direct view                                      | ❌                                          | ❌                                                   | /                                                                                                                                                             |
| Gallery view                                     | ❌                                          | ❌                                                   | /                                                                                                                                                             |
| Text view                                        | ❌                                          | ❌                                                   | /                                                                                                                                                             |

> Tested the 16/02/2026
</details>
<details>
  <summary>Deprecated</summary>

- [EmbedEZ • facebookez.com](https://embedez.com)
</details>

## <img src="assets/bilibili.webp" alt="Bilibili" height="20"/> Bilibili
- [EmbedEZ • bilibiliez.com](https://embedez.com)
- [fxBilibili • fxbilibili.seria.moe](https://github.com/seriaati/fxBilibili)
- [BiliFix • vxbilibili.com](https://vxbilibili.com/) *Used by FixTweetBot*
  - Other official public instances/redirects: `vxb23.tv`
- [FixEmbed • fixembed.app/bilibili](https://github.com/kenhendricks00/FixEmbed)
  - Other official public instances/redirects: `fixembed.app/b23`, `fixembed.app/embed?url=`

## <img src="assets/threads.webp" alt="Threads" height="20"/> Threads
- [FixThreads • official instance deprecated](https://github.com/milanmdev/fixthreads)
  - Other unofficial public instances/redirects: `fixthreads.seria.moe` *Used by FixTweetBot*, `drhong.ddns.net:9813` (http only)
- [FzThreads • fzthreads.com](https://github.com/AVianJay/fzthreads)
- [Embeds.now • embeds.now/threads.com](https://embeds.now)
  - Other official public instances/redirects: `embeds.now/threads.net`, `th.embeds.now`
- [mbedfx • mbedfx.app/th](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
- [FixEmbed • fixembed.app/threads](https://github.com/kenhendricks00/FixEmbed)
  - Other official public instances/redirects: `fixembed.app/embed?url=`
<details>
  <summary>Deprecated</summary>

- [FixThreads • fixthreads.net](https://github.com/milanmdev/fixthreads)
- [vxThreads • vxthreads.net](https://github.com/everettsouthwick/vxThreads)
- [EmbedEZ • threadsez.net](https://embedez.com)
  - Other official public instances/redirects: `threadsez.com`
</details>

## <img src="assets/pixiv.webp" alt="Pixiv" height="20"/> Pixiv
- [phixiv • phixiv.net](https://github.com/thelaao/phixiv) *Used by FixTweetBot*
  - Other official public instances/redirects: `ppxiv.net`
- [FixEmbed • fixembed.app/pixiv](https://github.com/kenhendricks00/FixEmbed)
  - Other official public instances/redirects: `fixembed.app/embed?url=`

## <img src="assets/pinterest.webp" alt="Pinterest" height="20"/> Pinterest
- [EmbedEZ • pinterestez.com](https://embedez.com) *Used by FixTweetBot*
- [Embeds.now • embeds.now/pinterest.com](https://embeds.now)
  - Other official public instances/redirects: `embeds.now/pin.it`, `pi.embeds.now`, `pn.embeds.now`
- [mbedfx • mbedfx.app/pn](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
- [FixEmbed • fixembed.app/pin](https://github.com/kenhendricks00/FixEmbed)
  - Other official public instances/redirects: `fixembed.app/pinterest`, `fixembed.app/embed?url=`

## <img src="assets/ifunny.webp" alt="IFunny" height="20"/> IFunny
- [EmbedEZ • ifunnyez.co](https://embedez.com) *Used by FixTweetBot*

## <img src="assets/youtube.webp" alt="YouTube" height="20"/> YouTube
- [Koutube • koutube.com](https://github.com/iGerman00/koutube) *Used by FixTweetBot*
  - Other official public instances/redirects: `koutu.be`
- [FixYouTube • y.outube.duckdns.org](https://github.com/birabittoh/fixyoutube-go)
- [Embeds.now • embeds.now/youtube.com](https://embeds.now)
  - Other official public instances/redirects: `embeds.now`, `yt.embeds.now`
- [mbedfx • mbedfx.app/yt](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
- [FixEmbed • fixembed.app/yt](https://github.com/kenhendricks00/FixEmbed) (community posts only)
  - Other official public instances/redirects: `fixembed.app/youtube`, `fixembed.app/embed?url=`
<details>
  <summary>Deprecated</summary>

- [youtube-discord-embed • yt.cdn.13373333.one](https://github.com/ray-1337/youtube-discord-embed/)
</details>

## <img src="assets/twitch.webp" alt="Twitch" height="20"/> Twitch
- [fxtwitch • fxtwitch.seria.moe](https://github.com/seriaati/fxtwitch) *Used by FixTweetBot*
- [mbedfx • mbedfx.app/tw](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
- [FixEmbed • fixembed.app/embed?url=](https://github.com/kenhendricks00/FixEmbed)
<details>
  <summary>Deprecated</summary>

- [FxTwitch • fxtwitch.tv](https://fxtwitch.tv)
- [Txitch • txitch.tv](https://txitch.tv)
</details>

## <img src="assets/bluesky.webp" alt="Bluesky" height="20"/> Bluesky
- [VixBluesky • bskx.app](https://github.com/Lexedia/VixBluesky)
  - Other official public instances/redirects: `bskyx.app` (deprecated)
  - Other unofficial public instances/redirects: `girlcockbsky.app` (nsfw content)
- [FixBluesky • bsyy.app](https://github.com/ThornbushHQ/FixBluesky)
- [xbsky • xbsky.app](https://github.com/colduw/xbsky)
- [FxBluesky • fxbsky.app](https://github.com/FxEmbed/FxEmbed) *Used by FixTweetBot*
- [vxBsky • vxbsky.app](https://github.com/dylanpdx/vxBsky)
- [bskye • bskye.app](https://github.com/FerroEduardo/bskye)
- [cbsky.app • cbsky.app](https://github.com/goeo-/cbsky.app)
- [bsky-viewer • bsky-viewer.branchpanic.workers.dev](https://github.com/branchpanic/bsky-viewer)
- [boobsky • boobsky.app](https://boobsky.app/)
- [Embeds.now • embeds.now/bsky.app](https://embeds.now)
  - Other official public instances/redirects: `bs.embeds.now`
- [mbedfx • mbedfx.app/bs](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
- [FixEmbed • fixembed.app/bsky](https://github.com/kenhendricks00/FixEmbed)
  - Other official public instances/redirects: `fixembed.app/bluesky`, `fixembed.app/embed?url=`

## <img src="assets/roblox.webp" alt="Roblox" height="20"/> Roblox
- [Rxblox2 • fixroblox.com](https://github.com/vys69/Rxblox2)

## <img src="assets/snapchat.webp" alt="Snapchat" height="20"/> Snapchat
- [EmbedEZ • snapchatez.com](https://embedez.com) *Used by FixTweetBot*

## <img src="assets/spotify.webp" alt="Spotify" height="20"/> Spotify
- [fxspotify • fxspotify.com](https://github.com/dotconnexion/fxspotify) *Used by FixTweetBot*
- [FixSpotify • open.fixspotify.com](https://github.com/evastarlight/fixspotify)
  - Other official public instances/redirects: `fixspotify.link`
- [Embeds.now • embeds.now/open.spotify.com](https://embeds.now)
  - Other official public instances/redirects: `sp.embeds.now`, `sl.embeds.now`, `embeds.now`, `embeds.now/spotify.link`

## <img src="assets/furaffinity.webp" alt="FurAffinity" height="20"/> FurAffinity
- [xfuraffinity • xfuraffinity.net](https://github.com/FirraWoof/xfuraffinity) *Used by FixTweetBot*
- [fxraffinity • fxraffinity.net](https://github.com/kheina-com/fxraffinity)
  - Other official public instances/redirects: `fxfuraffinity.net`

## <img src="assets/deviantart.webp" alt="DeviantArt" height="20"/> DeviantArt
- [fixDeviantArt • fixdeviantart.com](https://github.com/Tschrock/fixdeviantart) *Used by FixTweetBot*
- [FixEmbed • fixembed.app/da](https://github.com/kenhendricks00/FixEmbed)
  - Other official public instances/redirects: `fixembed.app/deviantart`, `fixembed.app/stash`, `fixembed.app/embed?url=`
<details>
  <summary>Deprecated</summary>

- [fxDeviantArt • fxdeviantart.com](https://github.com/daisyUniverse/fxdeviantart)
</details>

## <img src="assets/mastodon.webp" alt="Mastodon" height="20"/> Mastodon
- [FxMastodon • fx.zillanlabs.tech](https://fx.zillanlabs.tech/)
- [FxMastodon • fxmas.to](https://github.com/Someguy123/fxmastodon) *Used by FixTweetBot*
- [FxMastodon • fx.sizecraft.social](https://fx.sizecraft.social/)
- [Embeds.now • embeds.now/mastodon.social](https://embeds.now)
  - Other official public instances/redirects: `ma.embeds.now`
- [mbedfx • mbedfx.app/ms](https://github.com/shamu4life/mbedfx) (works with any instance)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`

## <img src="assets/tumblr.webp" alt="Tumblr" height="20"/> Tumblr
- [fxtumblr • tpmblr.com](https://github.com/knuxify/fxtumblr) *Used by FixTweetBot*
  - Other official public instances/redirects: `fx.dissonant.dev`
- [TxTumblr • txtumblr.com](https://github.com/MarkSuckerberg/txtumblr)
- [Embeds.now • embeds.now/tumblr.com](https://embeds.now)
  - Other official public instances/redirects: `tb.embeds.now`
- [FixEmbed • fixembed.app/embed?url=](https://github.com/kenhendricks00/FixEmbed)

## <img src="assets/misskey.webp" alt="Misskey" height="20"/> Misskey
- [FxMastodon • fx.sizecraft.social](https://fx.sizecraft.social/)
- [mbedfx • mbedfx.app/mk](https://github.com/shamu4life/mbedfx) (works with any instance)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`

## <img src="assets/imgur.webp" alt="Imgur" height="20"/> Imgur
- [EmbedEZ • imgurez.com](https://embedez.com) *Used by FixTweetBot*
- [mbedfx • mbedfx.app/im](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`
<details>
  <summary>Comparison table</summary>

| Link type                         | [EmbedEZ • imgurez.com](https://embedez.com/) | Link example                                         |
  |-----------------------------------|-----------------------------------------------|------------------------------------------------------|
| `/gallery/:slug_hash`             | ✔️                                            | https://imgur.com/gallery/house-of-memories-2ATCVHQ  |
| `/:hash`                          | ✔️                                            | https://imgur.com/CAvBSVj                            |
| `/:hash.mp4`                      | ❌                                            | https://i.imgur.com/CAvBSVj.mp4                      |
| `/user/:username/posts`           | ❌                                            | https://imgur.com/user/friendlynoodles/posts         |
| `/user/:username/favorites`       | ❌                                            | https://imgur.com/user/friendlynoodles/favorites     |
| `/user/:username/comments`        | ❌                                            | https://imgur.com/user/friendlynoodles/comments      |
| `/user/:username/about`           | ❌                                            | https://imgur.com/user/friendlynoodles/about         |
| `/gallery/:slug_hash/comment/:id` | ❌                                            | https://imgur.com/gallery/zg2DdD7/comment/2468524531 |
| `/t/:category`                    | ❌                                            | https://imgur.com/t/funny?source=featured_tag_module |
| Translation                       | ✔️                                            | /                                                    |
| Normal view                       | ✔️                                            | /                                                    |
| Direct view                       | ✔️                                            | /                                                    |
| Gallery view                      | ❌                                            | /                                                    |
| Text view                         | ❌                                            | /                                                    |

> Tested the 28/07/2025
</details>

## <img src="assets/linkedin.webp" alt="LinkedIn" height="20"/> LinkedIn
- [Embeds.now • embeds.now/linkedin.com](https://embeds.now)
  - Other official public instances/redirects: `embeds.now/lnkd.in`, `li.embeds.now`, `ld.embeds.now`

## <img src="assets/weibo.webp" alt="Weibo" height="20"/> Weibo
- [EmbedEZ • weiboez.com](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                        | [EmbedEZ • weiboez.com](https://embedez.com/) | Link example                                                         |
  |----------------------------------|-----------------------------------------------|----------------------------------------------------------------------|
| `/:id/:hash` (video)             | ✔️                                            | https://weibo.com/7405254778/PuuM33YS9                               |
| `/:id/:hash` (photo)             | ✔️                                            | https://weibo.com/7405254778/PuFIHwypn                               |
| `/:id/:hash` (multiple photo)    | ✔️                                            | https://weibo.com/7405254778/PullQdkk4                               |
| `/:id/:hash` (text only)         | ✔️                                            | https://weibo.com/1816375314/Pn2yKkBKS                               |
| `/:id/:hash` (quote tweet)       | ✔️                                            | https://weibo.com/1816375314/PlYXx4Pxb                               |
| `/:id/:hash` (video quote tweet) | ✔️                                            | https://weibo.com/1816375314/Pc7tIqUaI                               |
| `/:id/:hash` (image quote tweet) | ✔️                                            | https://weibo.com/1816375314/P7AgmbPjT                               |
| `/:id/:hash` (multiple gif)      | ➖ Thumbnail                                  | https://weibo.com/7051114584/Puc8OtcBZ                               |
| `/status/:hash`                  | ✔️                                            | https://m.weibo.cn/status/PuuM33YS9?jumpfrom=weibocom                |
| `/tv/show/:id`                   | ❌                                            | https://weibo.com/tv/show/1034:5192921763217419?mid=5193035542692662 |
| `/u/:id`                         | ❌                                            | https://weibo.com/u/2142058927                                       |
| `/u/:username`                   | ❌                                            | https://weibo.com/n/%E7%86%8A%E5%87%BA%E6%B2%A1                      |
| Translation                      | ✔️                                            |                                                                      |
| Normal view                      | ✔️                                            |                                                                      |
| Direct view                      | ✔️                                            |                                                                      |
| Gallery view                     | ❌                                            |                                                                      |
| Text view                        | ❌                                            |                                                                      |

> Tested the 29/07/2025
</details>

## <img src="assets/xiaohongshu.webp" alt="Xiaohongshu" height="20"/> Xiaohongshu
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*

## AliExpress
- [fixaliexpress • alimbedxpress.com](https://github.com/Alfredooe/fixaliexpress)

## <img src="assets/newgrounds.webp" alt="Newgrounds" height="20"/> Newgrounds
- [FixNewgrounds • fixnewgrounds.com](https://github.com/SauceyRed/fix-newgrounds) *Used by FixTweetBot*
- [EmbedEZ • newgroundsez.com](https://embedez.com)
<details>
  <summary>Comparison table</summary>

| Link type                                 | [FixNewgrounds](https://github.com/SauceyRed/fix-newgrounds) | Link example                                                                             |
  |-------------------------------------------|--------------------------------------------------------------|------------------------------------------------------------------------------------------|
| `/portal/view/:id` (game)                 | ❌                                                           | https://www.newgrounds.com/portal/view/1016050                                           |
| `/portal/view/:id` (video)                | ❌                                                           | https://www.newgrounds.com/portal/view/891548                                            |
| `/audio/listen/:id`                       | ❌                                                           | https://www.newgrounds.com/audio/listen/1519750                                          |
| `/series/:slug`                           | ❌                                                           | https://www.newgrounds.com/series/punch-punch-forever                                    |
| `/news/post/:id`                          | ❌                                                           | https://ncmentisart.newgrounds.com/news/post/1598683                                     |
| `/bbs/topic/:id/:page`                    | ❌                                                           | https://www.newgrounds.com/bbs/topic/1553471/1                                           |
| `/art/view/:username/:slug` (image)       | ✔️                                                           | https://www.newgrounds.com/art/view/grizzace/stocking-3                                  |
| `/art/view/:username/:slug` (gif)         | ✔️                                                           | https://www.newgrounds.com/art/view/infinitebrians/space-station-ost-comp-jam-commission |
| `/art/view/:username/:slug` (gallery)     | ➖ Only the first                                            | https://www.newgrounds.com/art/view/omegakevin/deadlock-graves                           |
| `/art/view/:username/:slug` (gif gallery) | ➖ Only the first                                            | https://www.newgrounds.com/art/view/awksalotl/chibits-lanterns                           |
| NSFW Content                              | ✔️                                                           | https://www.newgrounds.com/art/view/squibble-ink/stocking-anarchy                        |
| Translation                               | ❌                                                           | /                                                                                        |
| Normal view                               | ✔️                                                           | /                                                                                        |
| Direct view                               | ❌                                                           | /                                                                                        |
| Gallery view                              | ❌                                                           | /                                                                                        |
| Text view                                 | ❌                                                           | /                                                                                        |

> Tested the 28/01/2026
</details>

## <img src="assets/gocomics.webp" alt="GoComics" height="20"/> GoComics
- [FxGoComics • fxgocomics.com](https://github.com/shayypy/fxgocomics)

## <img src="assets/ptt.webp" alt="PTT" height="20"/> PTT
- [fxptt • fxptt.seria.moe](https://github.com/seriaati/fxptt)

## <img src="assets/dailymotion.webp" alt="Dailymotion" height="20"/> Dailymotion
- [mbedfx • mbedfx.app/dm](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`

## <img src="assets/streamable.webp" alt="Streamable" height="20"/> Streamable
- [mbedfx • mbedfx.app/st](https://github.com/shamu4life/mbedfx)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`

## <img src="assets/lemmy.webp" alt="Lemmy" height="20"/> Lemmy
- [mbedfx • mbedfx.app/lm](https://github.com/shamu4life/mbedfx) (works with any instance)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`

## <img src="assets/peertube.webp" alt="PeerTube" height="20"/> PeerTube
- [mbedfx • mbedfx.app/pt](https://github.com/shamu4life/mbedfx) (works with any instance)
  - Other official public instances/redirects: `mbedfx.app`, `megapenispoopenfarten.sex`, `forsen.sex`, `sorryifuckedyour.mom`, `hotsinglesnear.you`

## <img src="assets/safebooru.webp" alt="Safebooru" height="20"/> Safebooru
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                                    | [EmbedEZ](https://embedez.com/) | Link example                                                |
  |----------------------------------------------|---------------------------------|-------------------------------------------------------------|
| `/index.php?page=post&s=view&id=:id` (image) | ✔️                              | https://safebooru.org/index.php?page=post&s=view&id=6197518 |
| `/index.php?page=post&s=view&id=:id` (gif)   | ✔️                              | https://safebooru.org/index.php?page=post&s=view&id=496225  |
| Translation                                  | ❌                              | /                                                           |
| Normal view                                  | ✔️                              | /                                                           |
| Direct view                                  | ✔️                              | /                                                           |
| Gallery vie                                  | ❌                              | /                                                           |
| Text view                                    | ❌                              | /                                                           |

> Tested the 13/11/2025
</details>

## <img src="assets/iwara.webp" alt="Iwara" height="20"/> Iwara (nsfw content)
- [fxiwara • fxiwara.seria.moe](https://github.com/seriaati/fxiwara)

## <img src="assets/rule34.webp" alt="Rule34" height="20"/> Rule34 (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                                    | [EmbedEZ](https://embedez.com/) | Link example                                                                                           |
  |----------------------------------------------|---------------------------------|--------------------------------------------------------------------------------------------------------|
| `/index.php?page=post&s=view&id=:id` (image) | ✔️                              | https://rule34.xxx/index.php?page=post&s=view&id=10745133&tags=safe_for_work+sort%3Ascore%3Adesc       |
| `/index.php?page=post&s=view&id=:id` (gif)   | ✔️                              | https://rule34.xxx/index.php?page=post&s=view&id=7287076&tags=safe_for_work+sort%3Ascore%3Adesc+gif    |
| `/index.php?page=post&s=view&id=:id` (video) | ✔️                              | https://rule34.xxx/index.php?page=post&s=view&id=14396991&tags=safe_for_work+sort%3Ascore%3Adesc+video |
| Translation                                  | ❌                              | /                                                                                                      |
| Normal view                                  | ✔️                              | /                                                                                                      |
| Direct view                                  | ✔️                              | /                                                                                                      |
| Gallery vie                                  | ❌                              | /                                                                                                      |
| Text view                                    | ❌                              | /                                                                                                      |

> Tested the 13/11/2025
</details>

## <img src="assets/gelbooru.webp" alt="Gelbooru" height="20"/> Gelbooru (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                                    | [EmbedEZ](https://embedez.com/) | Link example                                                                                         |
  |----------------------------------------------|---------------------------------|------------------------------------------------------------------------------------------------------|
| `/index.php?page=post&s=view&id=:id` (image) | ✔️                              | https://gelbooru.com/index.php?page=post&s=view&id=12945750&tags=rating%3As+stocking_%28psg%29+      |
| `/index.php?page=post&s=view&id=:id` (gif)   | ✔️                              | https://gelbooru.com/index.php?page=post&s=view&id=2961695&tags=rating%3As+stocking_%28psg%29+gif    |
| `/index.php?page=post&s=view&id=:id` (video) | ❌                              | https://gelbooru.com/index.php?page=post&s=view&id=12466868&tags=rating%3As+stocking_%28psg%29+video |
| Translation                                  | ❌                              | /                                                                                                    |
| Normal view                                  | ✔️                              | /                                                                                                    |
| Direct view                                  | ✔️                              | /                                                                                                    |
| Gallery vie                                  | ❌                              | /                                                                                                    |
| Text view                                    | ❌                              | /                                                                                                    |

> Tested the 13/11/2025
</details>

## <img src="assets/danbooru.webp" alt="Danbooru" height="20"/> Danbooru (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type            | [EmbedEZ](https://embedez.com/) | Link example                                                                   |
  |----------------------|---------------------------------|--------------------------------------------------------------------------------|
| `/posts/:id` (image) | ✔️                              | https://danbooru.donmai.us/posts/10021344?q=rating%3As+stocking_%28psg%29+     |
| `/posts/:id` (gif)   | ✔️                              | https://danbooru.donmai.us/posts/9100029?q=rating%3As+stocking_%28psg%29+gif   |
| `/posts/:id` (video) | ✔️                              | https://danbooru.donmai.us/posts/7974439?q=rating%3As+stocking_%28psg%29+video |
| Translation          | ❌                              | /                                                                              |
| Normal view          | ✔️                              | /                                                                              |
| Direct view          | ✔️                              | /                                                                              |
| Gallery vie          | ❌                              | /                                                                              |
| Text view            | ❌                              | /                                                                              |

> Tested the 13/11/2025
</details>

## <img src="assets/e621.webp" alt="E621" height="20"/> E621/E926 (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type            | [EmbedEZ](https://embedez.com/) | Link example                                                    |
  |----------------------|---------------------------------|-----------------------------------------------------------------|
| `/posts/:id` (image) | ✔️                              | https://e926.net/posts/4849807?q=stocking_anarchy+rating%3As    |
| `/posts/:id` (gif)   | ✔️                              | https://e926.net/posts/352765?q=stocking_anarchy+gif+rating%3As |
| `/posts/:id` (video) | ✔️                              | https://e926.net/posts/2976753?q=video+rating%3As+order%3Ascore |
| Translation          | ❌                              | /                                                               |
| Normal view          | ✔️                              | /                                                               |
| Direct view          | ✔️                              | /                                                               |
| Gallery vie          | ❌                              | /                                                               |
| Text view            | ❌                              | /                                                               |

> Tested the 13/11/2025
</details>

## <img src="assets/realbooru.webp" alt="Realbooru" height="20"/> Realbooru (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                                    | [EmbedEZ](https://embedez.com/) | Link example                                               |
  |----------------------------------------------|---------------------------------|------------------------------------------------------------|
| `/index.php?page=post&s=view&id=:id` (image) | ✔️                              | https://realbooru.com/index.php?page=post&s=view&id=588549 |
| `/index.php?page=post&s=view&id=:id` (gif)   | ✔️                              | https://realbooru.com/index.php?page=post&s=view&id=91904  |
| `/index.php?page=post&s=view&id=:id` (video) | ✔️                              | https://realbooru.com/index.php?page=post&s=view&id=958458 |
| Translation                                  | ❌                              | /                                                          |
| Normal view                                  | ✔️                              | /                                                          |
| Direct view                                  | ✔️                              | /                                                          |
| Gallery vie                                  | ❌                              | /                                                          |
| Text view                                    | ❌                              | /                                                          |

> Tested the 13/11/2025
</details>

## <img src="assets/hypnohub.webp" alt="Hypnohub" height="20"/> Hypnohub (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                                    | [EmbedEZ](https://embedez.com/) | Link example                                              |
  |----------------------------------------------|---------------------------------|-----------------------------------------------------------|
| `/index.php?page=post&s=view&id=:id` (image) | ✔️                              | https://hypnohub.net/index.php?page=post&s=view&id=246070 |
| `/index.php?page=post&s=view&id=:id` (gif)   | ✔️                              | https://hypnohub.net/index.php?page=post&s=view&id=254792 |
| `/index.php?page=post&s=view&id=:id` (video) | ✔️                              | https://hypnohub.net/index.php?page=post&s=view&id=245996 |
| Translation                                  | ❌                              | /                                                         |
| Normal view                                  | ✔️                              | /                                                         |
| Direct view                                  | ✔️                              | /                                                         |
| Gallery vie                                  | ❌                              | /                                                         |
| Text view                                    | ❌                              | /                                                         |

> Tested the 13/11/2025
</details>

## <img src="assets/konachan.webp" alt="Konachan" height="20"/> Konachan (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                | [EmbedEZ](https://embedez.com/) | Link example                                                                             |
  |--------------------------|---------------------------------|------------------------------------------------------------------------------------------|
| `/post/show/:id` (image) | ✔️                              | https://konachan.net/post/show/238624/2girls-aqua_eyes-black_hair-blonde_hair-bow-chuck- |
| `/post/show/:id` (gif)   | ✔️                              | https://konachan.net/post/show/367018/all_male-animated-book-brown_hair-fairy-game_conso |
| Translation              | ❌                              | /                                                                                        |
| Normal view              | ✔️                              | /                                                                                        |
| Direct view              | ✔️                              | /                                                                                        |
| Gallery vie              | ❌                              | /                                                                                        |
| Text view                | ❌                              | /                                                                                        |

> Tested the 13/11/2025
</details>

## <img src="assets/yandere.webp" alt="Yande.re" height="20"/> Yande.re (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                | [EmbedEZ](https://embedez.com/) | Link example                      |
  |--------------------------|---------------------------------|-----------------------------------|
| `/post/show/:id` (image) | ✔️                              | https://yande.re/post/show/994233 |
| Translation              | ❌                              | /                                 |
| Normal view              | ✔️                              | /                                 |
| Direct view              | ✔️                              | /                                 |
| Gallery vie              | ❌                              | /                                 |
| Text view                | ❌                              | /                                 |

> Tested the 13/11/2025
</details>

## <img src="assets/derpibooru.webp" alt="Derpibooru" height="20"/> Derpibooru (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type             | [EmbedEZ](https://embedez.com/) | Link example                                  |
  |-----------------------|---------------------------------|-----------------------------------------------|
| `/images/:id` (image) | ✔️                              | https://derpibooru.org/images/3711306         |
| `/images/:id` (gif)   | ✔️                              | https://derpibooru.org/images/3710947?q=gif   |
| `/images/:id` (video) | ✔️                              | https://derpibooru.org/images/3702391?q=video |
| Translation           | ❌                              | /                                             |
| Normal view           | ✔️                              | /                                             |
| Direct view           | ✔️                              | /                                             |
| Gallery vie           | ❌                              | /                                             |
| Text view             | ❌                              | /                                             |

> Tested the 13/11/2025
</details>

## <img src="assets/paheal.webp" alt="Rule34 Paheal" height="20"/> Rule34.paheal (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                | [EmbedEZ](https://embedez.com/) | Link example                                                |
  |--------------------------|---------------------------------|-------------------------------------------------------------|
| `/post/view/:id` (image) | ✔️                              | https://rule34.paheal.net/post/view/3779460#search=SFW      |
| `/post/view/:id` (gif)   | ✔️                              | https://rule34.paheal.net/post/view/7097489#search=animated |
| `/post/view/:id` (video) | ✔️                              | https://rule34.paheal.net/post/view/7101541#search=animated |
| Translation              | ❌                              | /                                                           |
| Normal view              | ✔️                              | /                                                           |
| Direct view              | ✔️                              | /                                                           |
| Gallery vie              | ❌                              | /                                                           |
| Text view                | ❌                              | /                                                           |

> Tested the 13/11/2025
</details>

## <img src="assets/xbooru.webp" alt="Xbooru" height="20"/> Xbooru (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                                    | [EmbedEZ](https://embedez.com/) | Link example                                             |
  |----------------------------------------------|---------------------------------|----------------------------------------------------------|
| `/index.php?page=post&s=view&id=:id` (image) | ✔️                              | https://xbooru.com/index.php?page=post&s=view&id=683401  |
| `/index.php?page=post&s=view&id=:id` (gif)   | ✔️                              | https://xbooru.com/index.php?page=post&s=view&id=209728  |
| `/index.php?page=post&s=view&id=:id` (video) | ✔️                              | https://xbooru.com/index.php?page=post&s=view&id=1036764 |
| Translation                                  | ❌                              | /                                                        |
| Normal view                                  | ✔️                              | /                                                        |
| Direct view                                  | ✔️                              | /                                                        |
| Gallery vie                                  | ❌                              | /                                                        |
| Text view                                    | ❌                              | /                                                        |

> Tested the 13/11/2025
</details>

## <img src="assets/tbib.webp" alt="TBIB" height="20"/> TBIB (nsfw content)
- [EmbedEZ](https://embedez.com) *Used by FixTweetBot*
<details>
  <summary>Comparison table</summary>

| Link type                                    | [EmbedEZ](https://embedez.com/) | Link example                                            |
  |----------------------------------------------|---------------------------------|---------------------------------------------------------|
| `/index.php?page=post&s=view&id=:id` (image) | ✔️                              | https://tbib.org/index.php?page=post&s=view&id=25925420 |
| `/index.php?page=post&s=view&id=:id` (gif)   | ✔️                              | https://tbib.org/index.php?page=post&s=view&id=1392687  |
| Translation                                  | ❌                              | /                                                       |
| Normal view                                  | ✔️                              | /                                                       |
| Direct view                                  | ✔️                              | /                                                       |
| Gallery vie                                  | ❌                              | /                                                       |
| Text view                                    | ❌                              | /                                                       |

> Tested the 13/11/2025
</details>

> [!NOTE]
> Are you aware of any other fixer that isn't included here? Feel free to open an issue!
