"""
Allows fixing links from various websites.
"""
import asyncio
import re
from typing import Optional, Self, Type, Iterable, Callable

import aiohttp

from database.models.Guild import *

__all__ = ('WebsiteLink', 'websites')

def call_if_valid(func: Callable) -> Callable:
    """
    A static method decorator that ensures the wrapped function is executed only if
    the instance is in a valid state. If the instance is not valid, a `ValueError`
    is raised.

    :param func: The function to be wrapped and whose execution is conditional
                 upon the validity of the instance.
    :return: A wrapper function that enforces a validity check before executing
             the wrapped function.
    """
    def wrapper(self, *args, **kwargs):
        """
        Represents a link to a website and provides functionality to validate it
        before executing specific operations. The static method `call_if_valid`
        is used as a decorator to ensure that any decorated method is only executed
        if the calling instance is valid.
        """
        if self.is_valid():
            return func(self, *args, **kwargs)
        raise ValueError("Invalid website link")
    return wrapper

class WebsiteLink:
    """
    Base class for all websites.
    """

    name: str
    id: str

    def __init__(self, guild: Guild, url: str) -> None:
        """
        Initialize the website.

        :param guild: The guild where the link has been sent
        :param url: The URL to fix
        """

        self.guild: Guild = guild
        self.url: str = url

    @classmethod
    def if_valid(cls, *args, **kwargs) -> Optional[Self]:
        """
        Return a website if the URL is valid.

        :param args: The arguments to pass to the constructor
        :param kwargs: The keyword arguments to pass to the constructor
        :return: The website if the URL is valid, None otherwise
        """

        self = cls(*args, **kwargs)
        return self if self.is_valid() else None

    def is_valid(self) -> bool:
        """
        Indicates if the link is valid.

        :return: True if the link is valid, False otherwise
        """

        raise NotImplementedError

    @call_if_valid
    async def get_fixed_url(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get the fixed link and its hypertext label.
        :return: The fixed link and its hypertext label
        """
        raise NotImplementedError

    @call_if_valid
    async def get_author_url(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get the author link and its hypertext label.
        :return: The author link and its hypertext label
        """
        raise NotImplementedError

    @call_if_valid
    async def get_original_url(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get the original link and its hypertext label.
        :return: The original link and its hypertext label
        """
        raise NotImplementedError

    @call_if_valid
    async def render(self) -> Optional[str]:
        """
        Render the fixed link according to the guild's settings and the context

        :return: The rendered fixed link
        """

        fixed_url, fixed_label = await self.get_fixed_url()
        if not fixed_url:
            return None
        author_url, author_label = await self.get_author_url()
        original_url, original_label = await self.get_original_url()
        fixed_link = f"[{original_label}](<{original_url}>)"
        if author_url:
            fixed_link += f" • [{author_label}](<{author_url}>)"
        fixed_link += f" • [{fixed_label}]({fixed_url})"
        return fixed_link


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
    is_translation: bool = False
    routes: dict[str, re.Pattern[str]] = {}

    def __init__(self, guild: Guild, url: str) -> None:
        """
        Initialize the website.

        :param url: the URL of the website
        :param guild: the guild where the link check is happening
        :return: None
        """

        super().__init__(guild, url)
        self.match, self.repl = self.get_match_and_repl()

    @classmethod
    def if_valid(cls, guild: Guild, url: str) -> Optional[Self]:
        """
        Return a website if the URL is valid.

        :param guild: the guild where the link check is happening
        :param url: the URL to check
        :return: the website if the URL is valid, None otherwise
        """

        if not guild[cls.id]:
            return None

        website = cls(guild, url)
        return website if website.is_valid() else None

    def is_valid(self) -> bool:
        return True if self.match else False

    def get_repl(self, route: str, match: re.Match[str]) -> str:
        """
        Generate a replacement for the corresponding route, with named groups.
        :param route: the route to generate the replacement for
        :param match: the match for the corresponding route
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

        return (
            "https://{domain}"
            + route_repl
            + "{post_path_segments}"
            + query_string_repl
        )

    def route_fix_post_path_segments(self) -> str:
        """
        Provide supplementary path segments for the fixed link.

        :return: the supplementary path segments
        """
        if not self.is_translation:
            return ""

        return f"/{self.guild.lang}" if self.guild[f"{self.id}_tr"] else ""

    def route_fix_subdomain(self) -> str:
        if not self.subdomains:
            return ''
        return self.subdomains[self.guild[f"{self.id}_view"]]


    def get_match_and_repl(self) -> tuple[Optional[re.Match[str]], Optional[str]]:
        """
        Get the match for the fixed link, if any, and generate a replacement for the corresponding route.

        :return: the match for the fixed link and the replacement for the corresponding route, or None if no match is found
        """

        for route, regex in self.routes.items():
            if match := regex.fullmatch(self.url):
                return match, self.get_repl(route, match)
        return None, None

    @call_if_valid
    def get_patched_url(self, domain, subdomain='', post_path_segments='') -> str:
        """
        Generate a patched URL based on the provided domain, subdomain, and post path segments.
        :param domain: The domain to use for the patched URL
        :param subdomain: The subdomain to prepend to the domain
        :param post_path_segments: The additional path segments to append to the URL
        :return: The patched URL as a string
        """
        patched_url = self.match.expand(self.repl.format(
            domain=subdomain + domain,
            post_path_segments=post_path_segments
        ))
        return patched_url

    @call_if_valid
    async def get_fixed_url(self) -> tuple[Optional[str], Optional[str]]:
        fixed_url = self.get_patched_url(
            self.fix_domain,
            self.route_fix_subdomain(),
            self.route_fix_post_path_segments()
        )
        return fixed_url, self.fixer_name

    @call_if_valid
    async def get_author_url(self) -> tuple[Optional[str], Optional[str]]:
        if not ('username' in self.match.groupdict() and self.match['username']):
            return None, None
        username = self.match["username"]
        user_link = (await self.get_original_url())[0].split(username)[0] + username
        return user_link, username

    @call_if_valid
    async def get_original_url(self) -> tuple[Optional[str], Optional[str]]:
        subdomain = ""
        if self.match['subdomain'] and self.match['subdomain'] != 'www':
            subdomain = self.match['subdomain'] + '.'
        original_url = self.get_patched_url(self.match['domain'], subdomain)
        return original_url, self.hypertext_label


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
    subdomains = {
        EmbedEzView.NORMAL: '',
        EmbedEzView.DIRECT_MEDIA: 'd.',
    }
    is_translation = True

    async def get_fixed_url(self) -> tuple[Optional[str], Optional[str]]:
        subdomain = ""
        if self.match['subdomain'] and self.match['subdomain'] != 'www':
            subdomain = self.match['subdomain'] + '.'
        subdomain = self.route_fix_subdomain() + subdomain
        prepared_url = self.get_patched_url(self.match['domain'], subdomain, self.route_fix_post_path_segments())
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://embedez.com/api/v1/providers/combined", params={'q': prepared_url}, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        return None, None
                    search_hash = (await response.json())['data']['key']
                    return f"https://embedez.com/embed/{search_hash}", self.fixer_name
        except asyncio.TimeoutError:
            return None, None


class TwitterLink(GenericWebsiteLink):
    """
    Twitter website.
    """

    name = 'Twitter'
    id = 'twitter'
    hypertext_label = 'Tweet'
    fix_domain = "fxtwitter.com"
    fixer_name = "FxTwitter"
    is_translation = True
    subdomains = {
        TwitterView.NORMAL: 'm.',
        TwitterView.GALLERY: 'g.',
        TwitterView.TEXT_ONLY: 't.',
        TwitterView.DIRECT_MEDIA: 'd.',
    }
    routes = generate_routes(
        ["twitter.com", "x.com", "nitter.net", "xcancel.com", "nitter.poast.org", "nitter.privacyredirect.com", "lightbrd.com", "nitter.space", "nitter.tiekoetter.com"],
        {
            "/:username/status/:id": None,
            "/:username/status/:id/:media_type(photo|video)/:media_id": None,
    })


class InstagramLink(EmbedEZLink):
    """
    Instagram website.
    """

    name = 'Instagram'
    id = 'instagram'
    hypertext_label = 'Instagram'
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
        ["threads.net", "threads.com"],
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
    routes = generate_routes(
        "snapchat.com",
        {
            "/p/:id1/:id2/:id3?": None,
            "/spotlight/:id": None,
    })


class FacebookLink(GenericWebsiteLink):
    """
    Facebook website.
    """

    name = 'Facebook'
    id = 'facebook'
    hypertext_label = 'Facebook'
    fix_domain = "facebed.com"
    fixer_name = "facebed"
    routes = generate_routes(
        "facebook.com",
        {
            "/:username/posts/:hash": None,
            "/share/:type(v|r)/:hash": None,
            "/reel/:id": None,
            "/photo": ['fbid'],
            "/watch": ['v'],
            "/permalink.php": ['story_fbid', 'id'],
            "/groups/:id/:type(posts|permalink)/:hash": None,
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

    async def get_fixed_url(self) -> tuple[Optional[str], Optional[str]]:
        fixed_url = self.get_patched_url(self.fix_domain + r"/\g<domain>")
        return fixed_url, self.fixer_name


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

    async def get_fixed_url(self) -> tuple[Optional[str], Optional[str]]:
        subdomain = ''
        if self.match['subdomain'] and self.match['subdomain'] != 'www':
            subdomain = r"\g<subdomain>."
        fixed_url = self.get_patched_url(self.fix_domain, subdomain)
        return fixed_url, self.fixer_name

    async def get_author_url(self) -> tuple[Optional[str], Optional[str]]:
        username = self.match['username'] \
            if 'username' in self.match.groupdict() else self.match['subdomain']
        if not username or username == "www":
            return None, None
        user_link = f"https://{username}.tumblr.com"
        return user_link, username


class BiliBiliLink(GenericWebsiteLink):
    """
    BiliBili website.
    """

    name = 'BiliBili'
    id = 'bilibili'
    hypertext_label = 'BiliBili'
    fix_domain = "vxbilibili.com"
    fixer_name = "BiliFix"
    routes = generate_routes(
        ["bilibili.com", "b23.tv", "b22.top"],
        {
            "/video/:id": None,
            "/:id": None,
            "/bangumi/play/:id": None,
            "/bangumi/media/:id": None,
            "/bangumi/v2/media-index": ["media_id"],
            "/opus/:id": None,
            "/dynamic/:id": None,
            "/space/:id": None,
            "/detail/:id": None,
            "/m/detail/:id": None,
        })

    async def get_fixed_url(self) -> tuple[Optional[str], Optional[str]]:
        subdomain = ""
        if self.match['subdomain'] and self.match['subdomain'] not in ('www', 'm'):
            subdomain = self.match['subdomain'] + '.'
        fixed_url = self.get_patched_url("vx" + self.match['domain'], subdomain)
        return fixed_url, self.fixer_name


class IFunnyLink(EmbedEZLink):
    """
    IFunny website.
    """

    name = 'IFunny'
    id = 'ifunny'
    hypertext_label = 'IFunny'
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


class ImgurLink(EmbedEZLink):
    """
    Imgur website.
    """

    name = 'Imgur'
    id = 'imgur'
    hypertext_label = 'Imgur'
    routes = generate_routes(
        "imgur.com",
        {
            "/gallery/:slug_hash": None,
            "/:hash": None,
        })


class WeiboLink(EmbedEZLink):
    """
    Weibo website.
    """

    name = 'Weibo'
    id = 'weibo'
    hypertext_label = 'Weibo'
    routes = generate_routes(
        ["weibo.com", "weibo.cn"],
        {
            "/:id/:hash": None,
        })


class Rule34Link(EmbedEZLink):
    """
    Rule34 website.
    """

    name = 'Rule34'
    id = 'rule34'
    hypertext_label = 'Rule34'
    routes = generate_routes(
        "rule34.xxx",
        {
            "/index.php": ['page', 's', 'id'],
        })


class CustomLink(WebsiteLink):
    """
    Custom website.
    """

    name = 'Custom'
    id = 'custom'

    def __init__(self, guild: Guild, url: str) -> None:
        super().__init__(guild, url)
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
    def if_valid(cls, guild: Guild, url: str) -> Optional[Self]:

        if not guild.custom_websites:
            return None

        self = cls(guild, url)
        return self if self.is_valid() else None

    def is_valid(self) -> bool:
        return self.fixed_link is not None

    @call_if_valid
    async def get_fixed_url(self) -> tuple[Optional[str], Optional[str]]:
        if not self.fixed_link:
            return None, None
        fixer_name = self.fixer_domain
        fixer_name = fixer_name.split("/")[0]
        fixer_elements = fixer_name.split(".")
        if len(fixer_elements) > 1:
            fixer_name = ".".join(fixer_elements[:-1])
        else:
            fixer_name = fixer_elements[0]
        fixer_name = fixer_name.capitalize()
        return self.fixed_link, fixer_name

    @call_if_valid
    async def get_author_url(self) -> tuple[Optional[str], Optional[str]]:
        return None, None

    @call_if_valid
    async def get_original_url(self) -> tuple[Optional[str], Optional[str]]:
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
    ImgurLink,
    WeiboLink,
    Rule34Link,
    CustomLink
]
