# Changelog

## 2.0.3

- Fix for unremoved embeds

## 2.0.2

- Fix for multiple links in the same markdown node

## 2.0.1

- Ignore the non-embeddable links in an inline-code
- Support for `/video/:id` and `/photo/:id` path

## 2.0

- Use a database, finally (mysql with masonite-orm)
- Put the fixed link in a pretty hypertext, with the author's name
- Ignore all non-embeddable links, like links in a spoiler or in a code block 

## 1.1.1

- Fixed a bug where the bot would try to remove embed from a message that doesn't exist anymore

## 1.1

- Added Links for support server and top.gg page in the `about` command
- Removed `bug`, `suggest` and `changelog` commands in favor of the support
  server
- When multiple links are detected, the bot will now post one message containing
  all the fixed links instead of one message per link

## 1.0

Initial release
- Ability to detect twitter.com and x.com links, remove the embed and repost them as fxtwitter.com links
- Commands `bug`, `suggest`, `changelog`, `enable`, `disable`, and `about`
