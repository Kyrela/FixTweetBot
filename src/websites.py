"""
Allows fixing links from various websites.
"""
import asyncio
import re
from typing import Optional, Self, Type, Iterable

import aiohttp

from database.models.Guild import *

__all__ = ('WebsiteLink', 'websites')

class WebsiteLink:
    """
    Base class for all websites.
    """

    name: str
    id: str

    def __init__(self, guild: Guild, url: str, spoiler: bool = False) -> None:
        """
        Initialize the website.

        :param guild: The guild where the link has been sent
        :param url: The URL to fix
        :param spoiler: If the URL is in a spoiler
        """

        self.guild: Guild = guild
        self.url: str = url
        self.spoiler: bool = spoiler

    @classmethod
    def if_valid(cls, guild: Guild, url: str, spoiler: bool = False) -> Optional[Self]:
        """
        Return a website if the URL is valid.

        :param guild: The guild where the link has been sent
        :param url: The URL to check
        :param spoiler: If the URL is in a spoiler
        :return: The website if the URL is valid, None otherwise
        """
        raise NotImplementedError

    async def get_fixed_url(self) -> Optional[tuple[str, str]]:
        """
        Get the fixed link and its hypertext label.
        :return: The fixed link and its hypertext label
        """
        raise NotImplementedError

    async def get_author_url(self) -> Optional[tuple[str, str]]:
        """
        Get the author link and its hypertext label.
        :return: The author link and its hypertext label
        """
        raise NotImplementedError

    async def get_original_url(self) -> Optional[tuple[str, str]]:
        """
        Get the original link and its hypertext label.
        :return: The original link and its hypertext label
        """
        raise NotImplementedError


class GenericWebsiteLink(WebsiteLink):
    """
    Represents a generic website link.
    """

    name: str
    id: str
    hypertext_label: str
    fixer_name: str
    fix_domain: str
    subdomains: Optional[dict[str, str]] = None
    routes: dict[str, re.Pattern[str]] = {}

    def __init__(self, guild: Guild, url: str, spoiler: bool = False) -> None:
        """
        Initialize the website.

        :param url: the URL of the website
        :param guild: the guild where the link check is happening
        :return: None
        """

        super().__init__(guild, url, spoiler)
        self.username: Optional[str] = None
        self.fixed_link: Optional[str] = self.fix_link()

    @classmethod
    def if_valid(cls, guild: Guild, url: str, spoiler: bool = False) -> Optional[Self]:
        """
        Return a website if the URL is valid.

        :param guild: the guild where the link check is happening
        :param url: the URL to check
        :param spoiler: if the URL is in a spoiler
        :return: the website if the URL is valid, None otherwise
        """

        if not guild.__getattr__(cls.id):
            return None

        website = cls(guild, url, spoiler)
        return website if website.fixed_link else None

    def get_domain_repl(self, route: str, match: re.Match[str]) -> str:
        """
        Get the domain replacement for the fixed link.
        :param route: The route to generate the replacement for
        :param match: The match object to generate the replacement with
        :return: The domain replacement for the fixed link
        """

        subdomain = ''
        if self.subdomains:
            subdomain = self.subdomains[self.guild.__getattr__(f"{self.id}_view")]

        return rf"https://{subdomain}{self.fix_domain}"

    def replace_link(self, route: str, match: re.Match[str]) -> str:
        """
        Generate a replacement for the corresponding route, with named groups.
        :param route: the route to generate the replacement for
        :param match: the match object to generate the replacement with
        """

        if route[0] != '/':
            route = '/' + route

        found_path_segments = [match[1] for match in re.finditer(r":(\w+)(?:\([^/]+\))?", route)]

        params = [
            g_name
            for g_name, g_value in match.groupdict().items()
            if g_name not in found_path_segments and g_value is not None and g_name not in ('domain', 'subdomain')
        ]

        route_repl = route
        route_repl = re.sub(r"/:(\w+)(?:\([^/]+\))?\?", r"", route_repl)
        route_repl = re.sub(r":(\w+)(?:\([^/]+\))?", r"\\g<\1>", route_repl)

        query_string_repl = ''
        if params:
            query_string_repl = '?' + '&'.join(rf"{param}=\g<{param}>" for param in params)

        return match.expand(self.get_domain_repl(route, match) + route_repl + self.route_fix_post_path_segments() + query_string_repl)

    def route_fix_post_path_segments(self) -> str:
        """
        Provide supplementary path segments for the fixed link.

        :return: the supplementary path segments
        """

        return ""

    def fix_link(self) -> Optional[str]:
        """
        Get the fixed link.

        :return: the fixed link
        """

        for route, regex in self.routes.items():
            if match := regex.fullmatch(self.url):
                if "username" in match.groupdict():
                    self.username = match.group("username")
                return self.replace_link(route, match)

    async def get_fixed_url(self) -> Optional[tuple[str, str]]:
        if not self.fixed_link:
            return None
        return self.fixed_link, self.fixer_name

    async def get_author_url(self) -> Optional[tuple[str, str]]:
        if not self.username:
            return None
        user_link = self.url.split(self.username)[0] + self.username
        return user_link, self.username

    async def get_original_url(self) -> Optional[tuple[str, str]]:
        return self.url, self.hypertext_label


def generate_regex(domain_names: str|list[str], route: str, params: Optional[list[str]] = None) -> re.Pattern[str]:
    """
    Generate a regex for the corresponding route, with named groups.
    :param domain_names: the domain name to generate the regex for
    :param route: the route to generate the regex for
    :param params: the parameters to generate the regex with
    :return: the generated regex
    """

    if route[0] != '/':
        route = '/' + route

    if isinstance(domain_names, str):
        domain_names = [domain_names]

    domain_regex = r"(?P<domain>" + '|'.join([re.escape(domain_name) for domain_name in domain_names]) + r")"

    route_regex = route
    route_regex = re.sub(r"/:(\w+)\(([^/]+)\)\?", r"(?:/\2)?", route_regex)
    route_regex = re.sub(r"/:(\w+)\?", r"(?:/[^/?#]+)?", route_regex)
    route_regex = re.sub(r":(\w+)\(([^/]+)\)", r"(?P<\1>\2)", route_regex)
    route_regex = re.sub(r":(\w+)", r"(?P<\1>[^/?#]+)", route_regex)

    query_string_param_regexes = []
    if params:
        query_string_param_regexes = [rf"(?:(?=(?:\?|.*&){param}=(?P<{param}>[^&#]+)))?" for param in params]
    query_string_regex = r"/?(?:" + ''.join(query_string_param_regexes) + r"\?[^#]+)?"

    return re.compile(r"https?://(?:(?P<subdomain>[^.]+)\.)?" + domain_regex + route_regex + query_string_regex + r"(?:#.+)?", re.IGNORECASE)


def generate_routes(domain_names: str|list[str], routes: dict[str, Optional[list[str]]]) -> dict[str, re.Pattern[str]]:
    """
    Generate regexes for the corresponding routes, with named groups.
    :param domain_names: the domain name to generate the regexes for
    :param routes: the routes to generate the regexes for
    :return: the generated regexes
    """

    return {
        route: generate_regex(domain_names, route, params)
        for route, params in routes.items()
    }


class EmbedEZLink(GenericWebsiteLink):
    fixer_name = "EmbedEZ"

    async def get_fixed_url(self) -> Optional[tuple[str, str]]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://embedez.com/api/v1/providers/combined", params={'q': self.url}, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        return None
        except asyncio.TimeoutError:
            return None
        return await super().get_fixed_url()


class TwitterLink(GenericWebsiteLink):
    """
    Twitter website.
    """

    name = 'Twitter'
    id = 'twitter'
    hypertext_label = 'Tweet'
    fix_domain = "fxtwitter.com"
    fixer_name = "FxTwitter"
    subdomains = {
        TwitterView.NORMAL: 'm.',
        TwitterView.GALLERY: 'g.',
        TwitterView.TEXT_ONLY: 't.',
        TwitterView.DIRECT_MEDIA: 'd.',
        TwitterView.COMPATIBILITY: '',
    }
    routes = generate_routes(
        ["twitter.com", "x.com", "nitter.lucabased.xyz", "nitter.poast.org", "nitter.privacydev.net", "xcancel.com"],
        {
            "/:username/status/:id": None,
            "/:username/status/:id/:media_type(photo|video)/:media_id": None,
    })

    def route_fix_post_path_segments(self) -> str:
        return f"/{self.guild.twitter_tr_lang}" if self.guild.twitter_tr else ""


class InstagramLink(EmbedEZLink):
    """
    Instagram website.
    """

    name = 'Instagram'
    id = 'instagram'
    hypertext_label = 'Instagram'
    fix_domain = "instagramez.com"
    routes = generate_routes(
        "instagram.com",
        {
            "/:media_type(p|reels?|tv|share)/:id": ['img_index'],
            "/:username/:media_type(p|reels?|tv|share)/:id": ['img_index'],
    })


class TikTokLink(GenericWebsiteLink):
    """
    Tiktok website.
    """

    name = 'TikTok'
    id = 'tiktok'
    hypertext_label = 'Tiktok'
    fix_domain = "tnktok.com"
    fixer_name = "fxTikTok"
    subdomains = {
        TiktokView.NORMAL: 'a.',
        TiktokView.GALLERY: '',
        TiktokView.DIRECT_MEDIA: 'd.',
    }
    routes = generate_routes(
        "tiktok.com",
        {
            "/@:username/:media_type(video|photo)/:id": None,
            "/:shortlink_type(t|embed)/:id": None,
            "/:id": None,
    })


class RedditLink(GenericWebsiteLink):
    """
    Reddit website.
    """

    name = 'Reddit'
    id = 'reddit'
    hypertext_label = 'Reddit'
    fix_domain = "vxreddit.com"
    fixer_name = "vxreddit"
    routes = generate_routes(
        ["reddit.com", "redditmedia.com"],
        {
            "/:post_type(u|r|user)/:username/:type(comments|s)/:id/:slug?": None,
            "/:post_type(u|r|user)/:username/:type(comments|s)/:id/:slug/:comment": None,
            "/:id": None,
    })


class ThreadsLink(GenericWebsiteLink):
    """
    Threads website.
    """

    name = 'Threads'
    id = 'threads'
    hypertext_label = 'Threads'
    fix_domain = "fixthreads.net"
    fixer_name = "FixThreads"
    routes = generate_routes(
        "threads.net",
        {
            "/@:username/post/:id": None,
    })


class BlueskyLink(GenericWebsiteLink):
    """
    Bluesky website.
    """

    name = 'Bluesky'
    id = 'bluesky'
    hypertext_label = 'Bluesky'
    fix_domain = "bskx.app"
    fixer_name = "VixBluesky"
    subdomains = {
        BlueskyView.NORMAL: '',
        BlueskyView.DIRECT_MEDIA: 'r.',
        BlueskyView.GALLERY: 'g.',
    }
    routes = generate_routes(
        "bsky.app",
        {
            "/profile/did:user_id/post/:id": None,
            "/profile/:username/post/:id": None,
    })


class SnapchatLink(EmbedEZLink):
    """
    Snapchat website.
    """

    name = 'Snapchat'
    id = 'snapchat'
    hypertext_label = 'Snapchat'
    fix_domain = "snapchatez.com"
    routes = generate_routes(
        "snapchat.com",
        {
            "/p/:id1/:id2/:id3?": None,
            "/spotlight/:id": None,
    })


class FacebookLink(EmbedEZLink):
    """
    Facebook website.
    """

    name = 'Facebook'
    id = 'facebook'
    hypertext_label = 'Facebook'
    fix_domain = "facebookez.com"
    routes = generate_routes(
        "facebook.com",
        {
            "/:username/:media_type(posts|videos)/:id": None,
            "/marketplace/item/:marketplace_id": None,
            "/share/r/:share_r_id": None,
            "/:link_type(share|reel)/:id": None,
            "/photos": ['fbid'],
            "/photo": ['fbid'],
            "/watch": ['v'],
            "/story.php": ['id', 'story_fbid'],
    })


class PixivLink(GenericWebsiteLink):
    """
    Pixiv website.
    """

    name = 'Pixiv'
    id = 'pixiv'
    hypertext_label = 'Pixiv'
    fix_domain = "phixiv.net"
    fixer_name = "phixiv"
    routes = generate_routes(
        "pixiv.net",
        {
            "/member_illust.php": ['illust_id'],
            "/:lang?/artworks/:id/:media?": None,
    })


class TwitchLink(GenericWebsiteLink):
    """
    Twitch website.
    """

    name = 'Twitch'
    id = 'twitch'
    hypertext_label = 'Twitch'
    fix_domain = "fxtwitch.seria.moe"
    fixer_name = "fxtwitch"
    routes = generate_routes(
        "twitch.tv",
        {
            "/:username/clip/:id": None,
    })


class SpotifyLink(GenericWebsiteLink):
    """
    Spotify website.
    """

    name = 'Spotify'
    id = 'spotify'
    hypertext_label = 'Spotify'
    fix_domain = "fxspotify.com"
    fixer_name = "fxspotify"
    routes = generate_routes(
        "spotify.com",
        {
            "/:lang?/track/:id": None,
    })


class DeviantArtLink(GenericWebsiteLink):
    """
    DeviantArt website.
    """

    name = 'DeviantArt'
    id = 'deviantart'
    hypertext_label = 'DeviantArt'
    fix_domain = "fixdeviantart.com"
    fixer_name = "fixDeviantArt"
    routes = generate_routes(
        "deviantart.com",
        {
            "/:username/:media_type(art|journal)/:id": None,
    })


class MastodonLink(GenericWebsiteLink):
    """
    Mastodon website.
    """

    name = 'Mastodon'
    id = 'mastodon'
    hypertext_label = 'Mastodon'
    fix_domain = "fx.zillanlabs.tech"
    fixer_name = "FxMastodon"
    routes = generate_routes(
        ["mastodon.social", "mstdn.jp", "mastodon.cloud", "mstdn.social", "mastodon.world", "mastodon.online", "mas.to", "techhub.social", "mastodon.uno", "infosec.exchange"],
        {
            "/@:username/:id": None,
    })

    def get_domain_repl(self, route: str, match: re.Match[str]) -> str:
        return rf"https://{self.fix_domain}/\g<domain>"


class TumblrLink(GenericWebsiteLink):
    """
    Tumblr website.
    """

    name = 'Tumblr'
    id = 'tumblr'
    hypertext_label = 'Tumblr'
    fix_domain = "tpmblr.com"
    fixer_name = "fxtumblr"
    routes = generate_routes(
        "tumblr.com",
        {
            "/post/:id/:slug?": None,
            "/:username/:id/:slug?": None,
    })

    def get_domain_repl(self, route: str, match: re.Match[str]) -> str:
        if match['subdomain'] and match['subdomain'] != 'www':
            self.username = match['subdomain']
            return rf"https://\g<subdomain>.{self.fix_domain}"
        return rf"https://{self.fix_domain}"

    async def get_author_url(self) -> Optional[tuple[str, str]]:
        if not self.username:
            return None
        user_link = f"https://{self.username}.tumblr.com"
        return user_link, self.username


class BiliBiliLink(GenericWebsiteLink):
    """
    BiliBili website.
    """

    name = 'BiliBili'
    id = 'bilibili'
    hypertext_label = 'BiliBili'
    fix_domain = "fxbilibili.seria.moe"
    fixer_name = "fxBilibili"
    routes = generate_routes(
        ["bilibili.com", "b23.tv"],
        {
            "/video/:id": None,
            "/:id": None,
            "/bangumi/play/:id": None,
        })

    def get_domain_repl(self, route: str, match: re.Match[str]) -> str:
        if match['domain'] == 'b23.tv':
            return rf"https://{self.fix_domain}/b23"
        return rf"https://{self.fix_domain}"


class IFunnyLink(EmbedEZLink):
    """
    IFunny website.
    """

    name = 'IFunny'
    id = 'ifunny'
    hypertext_label = 'IFunny'
    fix_domain = "ifunnyez.co"
    routes = generate_routes(
        "ifunny.co",
        {
            "/:media_type(video|picture|gif)/:id": None,
    })


class FurAffinityLink(GenericWebsiteLink):
    """
    FurAffinity website.
    """

    name = 'Fur Affinity'
    id = 'furaffinity'
    hypertext_label = 'Fur Affinity'
    fix_domain = "xfuraffinity.net"
    fixer_name = "xfuraffinity"
    routes = generate_routes(
        "furaffinity.net",
        {
            "/view/:id": None,
    })


class YouTubeLink(GenericWebsiteLink):
    """
    YouTube website.
    """

    name = 'YouTube'
    id = 'youtube'
    hypertext_label = 'YouTube'
    fix_domain = "koutube.com"
    fixer_name = "Koutube"
    routes = generate_routes(
        ["youtube.com", "youtu.be"],
        {
            "/watch": ['v'],
            "/playlist": ['list'],
            "/shorts/:id": None,
            "/:id": None,
    })


class CustomLink(WebsiteLink):
    """
    Custom website.
    """

    name = 'Custom'
    id = 'custom'

    def __init__(self, guild: Guild, url: str, spoiler: bool = False) -> None:
        super().__init__(guild, url, spoiler)
        self.fixed_link: Optional[str] = None
        self.hypertext_label: Optional[str] = None
        self.fixer_domain: Optional[str] = None

        # noinspection PyTypeChecker
        self.custom_websites: Iterable = guild.custom_websites
        for website in self.custom_websites:
            if match := re.fullmatch(
                    fr"https?://(?:www\.)?({re.escape(website.domain)})/(.+)", self.url, re.IGNORECASE):
                self.fixed_link = f"https://{website.fix_domain}/{match[2]}"
                self.hypertext_label = website.name
                self.fixer_domain = website.fix_domain

    @classmethod
    def if_valid(cls, guild: Guild, url: str, spoiler: bool = False) -> Optional[Self]:

        if not guild.custom_websites:
            return None

        website = cls(guild, url, spoiler)
        return website if website.fixed_link else None

    async def get_fixed_url(self) -> Optional[tuple[str, str]]:
        if not self.fixed_link:
            return None
        fixer_name = self.fixer_domain
        fixer_name = fixer_name.split("/")[0]
        fixer_elements = fixer_name.split(".")
        if len(fixer_elements) > 1:
            fixer_name = ".".join(fixer_elements[:-1])
        else:
            fixer_name = fixer_elements[0]
        fixer_name = fixer_name.capitalize()
        return self.fixed_link, fixer_name

    async def get_author_url(self) -> Optional[tuple[str, str]]:
        return None

    async def get_original_url(self) -> Optional[tuple[str, str]]:
        if not self.fixed_link:
            return None
        return self.url, self.hypertext_label


websites: list[Type[WebsiteLink]] = [
    TwitterLink,
    InstagramLink,
    TikTokLink,
    RedditLink,
    ThreadsLink,
    BlueskyLink,
    SnapchatLink,
    FacebookLink,
    PixivLink,
    TwitchLink,
    SpotifyLink,
    DeviantArtLink,
    MastodonLink,
    TumblrLink,
    BiliBiliLink,
    IFunnyLink,
    FurAffinityLink,
    YouTubeLink,
    CustomLink
]
