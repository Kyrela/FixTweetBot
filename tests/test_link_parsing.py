import asyncio

import discord_markdown_ast_parser as dmap

from cogs.link_fix import get_embeddable_urls
from database.models.Guild import FxEmbedView
from src.websites import TwitterLink, generate_regex


class FakeGuild:
    lang = 'en'

    def __init__(self, **settings):
        self.settings = settings

    def __getitem__(self, key):
        return self.settings[key]


def test_markdown_parser_ignores_code_and_preserves_spoilers():
    nodes = dmap.parse('`https://x.com/ignored/status/1` ||https://x.com/user/status/2||')

    assert get_embeddable_urls(nodes) == [('https://x.com/user/status/2', True)]


def test_generated_route_requires_the_whole_url_to_match():
    regex = generate_regex('example.com', '/:username/post/:id')

    match = regex.fullmatch('https://www.example.com/alice/post/42?ref=test')
    assert match is not None
    assert match['username'] == 'alice'
    assert match['id'] == '42'
    assert regex.fullmatch('https://evil.example/example.com/alice/post/42') is None


def test_twitter_link_renders_expected_proxy():
    guild = FakeGuild(
        twitter=True,
        twitter_view=FxEmbedView.NORMAL,
        twitter_tr=False,
    )
    link = TwitterLink(guild, 'https://x.com/alice/status/42')

    fixed_url, label = asyncio.run(link.get_fixed_url())
    assert fixed_url == 'https://fxtwitter.com/i/status/42'
    assert label == 'FxTwitter'
