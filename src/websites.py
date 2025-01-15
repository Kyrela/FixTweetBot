import re
from typing import Optional, Self, Type

from database.models.Guild import *

__all__ = ('WebsiteLink', 'websites')

class WebsiteLink:
    """
    Base class for all websites.
    """

    name: str
    id: str
    supports_username = False

    def __init__(self, guild: Guild, url: str, spoiler: bool = False) -> None:
        """
        Initialize the website.

        :param url: the URL of the website
        :param guild: the guild where the link check is happening
        :return: None
        """

        self.url = url
        self.matches = self.get_matches()
        self.guild = guild
        self.spoiler = spoiler

    @classmethod
    def if_valid(cls, guild: Guild, url: str, spoiler: bool = False) -> Optional[Self]:
        """
        Return a website if the URL is valid.

        :param guild: the guild where the link check is happening
        :param url: the URL to check
        :return: the website if the URL is valid, None otherwise
        """

        website = cls(guild, url, spoiler)
        return website if website.valid else None

    @classmethod
    def is_enabled(cls, guild: Guild) -> bool:
        """
        Check if the website is enabled.

        :param guild: the guild where the link check is happening
        :return: True if the website is enabled, False otherwise
        """

        return guild.__getattr__(cls.id)

    @property
    def enabled(self) -> bool:
        """
        Check if the website is enabled.

        :return: True if the website is enabled, False otherwise
        """

        return self.__class__.is_enabled(self.guild)

    @property
    def subdomains(self) -> dict:
        """
        Get the subdomains of the website.

        :return: the subdomains of the website
        """

        return {}

    @property
    def fix_domain(self) -> str:
        """
        Get the domain to fix the URL.

        :return: the domain to fix the URL
        """

        raise NotImplementedError

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        """
        Get the regexes of the website.

        :return: the regexes of the website
        """

        raise NotImplementedError

    def get_matches(self) -> list[Optional[re.Match[str]]]:
        """
        Get the matches of the URL.

        :return: the matches of the URL
        """

        return [regex.fullmatch(self.url) for regex in self.regexes]

    @property
    def valid(self) -> bool:
        """
        Check if the URL is valid and the website is enabled.

        :return: True if the URL is valid and the website is enabled, False otherwise
        """

        return self.enabled and any(self.matches)

    @property
    def valid_matches(self) -> list[re.Match[str]]:
        """
        Get the valid matches.

        :return: the valid matches
        """

        return list(filter(None, self.matches))

    @property
    def valid_match(self) -> Optional[re.Match[str]]:
        """
        Get the valid link.

        :return: the valid link
        """

        valid_matches = self.valid_matches
        return valid_matches[0] if valid_matches else None

    def fix_link(self, match: re.Match) -> str:
        """
        Fix the link.

        :return: the fixed link
        """

        raise NotImplementedError

    @property
    def fixed_link(self) -> Optional[str]:
        """
        Get the fixed link.

        :return: the fixed link
        """

        link = self.fix_link(self.valid_match)
        if not link:
            return None
        if self.spoiler:
            return f"||{link} ||"
        return link


class TwitterLink(WebsiteLink):
    """
    Twitter website.
    """

    name = 'Twitter'
    id = 'twitter'
    supports_username = True

    @property
    def fix_domain(self) -> str:
        return "fxtwitter.com"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:(?:www|m|mobile)\.)?"
                r"(?:twitter\.com|x\.com|"
                r"nitter\.(?:lucabased\.xyz|poast\.org|privacydev\.net)|xcancel.com)"
                r"/(\w+)/status/(\d+)(/(?:photo|video)/\d)?/?(?:\?\S+)?(?:#\S+)?", re.IGNORECASE),
        ]

    @property
    def subdomains(self) -> dict:
        return {
            TwitterView.NORMAL: '',
            TwitterView.GALLERY: 'g.',
            TwitterView.TEXT_ONLY: 't.',
            TwitterView.DIRECT_MEDIA: 'd.',
        }

    def fix_link(self, match: re.Match) -> Optional[str]:
        fxtwitter_link = (f"https://{self.subdomains[self.guild.twitter_view]}{self.fix_domain}/{match[1]}/status"
                          f"/{match[2]}")
        fxtwitter_link += match[3] or ''
        fxtwitter_link += ('/' + self.guild.twitter_tr_lang) if self.guild.twitter_tr else ''
        return (
            f"[Tweet • {match[1]}]({fxtwitter_link})")


class InstagramLink(WebsiteLink):
    """
    Instagram website.
    """

    name = 'Instagram'
    id = 'instagram'

    @property
    def fix_domain(self) -> str:
        return "instagramez.com"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:www\.)?instagram\.com/(p|reels?|tv|share)/([\w-]+)/?(\?\S+)?",
                re.IGNORECASE),
            re.compile(
                r"https?://(?:www\.)?instagram\.com/([\w.]+)/reels?/([\w-]+)/?(?:\?\S+)?",
                re.IGNORECASE),
        ]

    def fix_link(self, match: re.Match) -> str:
        if match.re == self.regexes[0]:
            return (
                f"[Instagram](https://{self.fix_domain}"
                f"/{match[1]}/{match[2]}{match[3] or ''})")
        return (
            f"[Instagram • {match[1]}](https://{self.fix_domain}"
            f"/{match[1]}/reel/{match[2]})")


class TikTokLink(WebsiteLink):
    """
    Tiktok website.
    """

    name = 'TikTok'
    id = 'tiktok'

    @property
    def fix_domain(self) -> str:
        return "tnktok.com"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        domain_regex = r"https?://(?:www\.|v[mt]\.)?tiktok\.com/"
        return [
            re.compile(
                domain_regex + r"@([\w.-]+)/(video|photo)/(\w+)/?(?:\?\S+)?",
                re.IGNORECASE),
            re.compile(
                domain_regex + r"(?:t/|embed/)?(\w+)/?(?:\?\S+)?",
                re.IGNORECASE),
        ]

    @property
    def subdomains(self) -> dict:
        return {
            TiktokView.NORMAL: 'a.',
            TiktokView.GALLERY: '',
            TiktokView.DIRECT_MEDIA: 'd.',
        }

    def fix_link(self, match: re.Match) -> str:
        if match.re == self.regexes[0]:
            return (
                f"[Tiktok • {match[1]}](https://{self.subdomains[self.guild.tiktok_view]}{self.fix_domain}"
                f"/@{match[1]}/{match[2]}/{match[3]})")
        else:
            return (
                f"[Tiktok](https://{self.subdomains[self.guild.tiktok_view]}{self.fix_domain}"
                f"/t/{match[1]})")


class RedditLink(WebsiteLink):
    """
    Reddit website.
    """

    name = 'Reddit'
    id = 'reddit'

    @property
    def fix_domain(self) -> str:
        return "rxddit.com"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        domain_regex = r"https?://(?:www\.|old\.)?reddit(?:media)?\.com/"
        return [
            re.compile(
                domain_regex + r"r/(\w+)/comments/(\w+)(?:/\w+)?/?(?:\?\S+)?",
                re.IGNORECASE),
            re.compile(
                domain_regex + r"r/(\w+)/comments/(\w+/\w+/\w+)/?(?:\?\S+)?",
                re.IGNORECASE),
            re.compile(
                domain_regex + r"r/(\w+)/s/(\w+)/?(?:\?\S+)?",
                re.IGNORECASE),
            re.compile(
                domain_regex + r"(\w+)/?(?:\?\S+)?",
                re.IGNORECASE),
        ]

    def fix_link(self, match: re.Match) -> str:
        if match.re == self.regexes[0] or match.re == self.regexes[1]:
            return f"[Reddit • {match[1]}](https://{self.fix_domain}/r/{match[1]}/comments/{match[2]})"
        elif match.re == self.regexes[2]:
            return f"[Reddit • {match[1]}](https://{self.fix_domain}/r/{match[1]}/s/{match[2]})"
        else:
            return f"[Reddit • {match[1]}](https://{self.fix_domain}/{match[1]})"


class ThreadsLink(WebsiteLink):
    """
    Threads website.
    """

    name = 'Threads'
    id = 'threads'

    @property
    def fix_domain(self) -> str:
        return "fixthreads.net"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:www\.)?threads\.net/@([\w.]+)/post/(\w+)/?(?:\?\S+)?",
                re.IGNORECASE),
        ]

    def fix_link(self, match: re.Match) -> str:
        return f"[Threads • {match[1]}](https://{self.fix_domain}/@{match[1]}/post/{match[2]})"


class BlueskyLink(WebsiteLink):
    """
    Bluesky website.
    """

    name = 'Bluesky'
    id = 'bluesky'

    @property
    def fix_domain(self) -> str:
        return "bskx.app"

    @property
    def subdomains(self) -> dict:
        return {
            BlueskyView.NORMAL: '',
            BlueskyView.DIRECT_MEDIA: 'r.',
            BlueskyView.GALLERY: 'g.',
        }

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:www\.)?bsky\.app/profile/([\w.-]+)/post/(\w+)/?(?:\?\S+)?",
                re.IGNORECASE),
        ]

    def fix_link(self, match: re.Match) -> str:
        return (f"[Bluesky • {match[1]}](https://{self.subdomains[self.guild.bluesky_view]}{self.fix_domain}/"
                f"profile/{match[1]}/post/{match[2]})")


class SnapchatLink(WebsiteLink):
    """
    Snapchat website.
    """

    name = 'Snapchat'
    id = 'snapchat'

    @property
    def fix_domain(self) -> str:
        return "snapchatez.com"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:www\.|story\.)?snapchat\.com/p/([\w-]+)/(\d+)/?(?:\?\S+)?",
                re.IGNORECASE),
            re.compile(
                r"https?://(?:www\.|story\.)?snapchat\.com/p/([\w-]+)/(\d+)/(\d+)/?(?:\?\S+)?",
                re.IGNORECASE),
            re.compile(
                r"https?://(?:www\.)?snapchat\.com/spotlight/([\w-]+)/?(?:\?\S+)?",
                re.IGNORECASE),
        ]

    def fix_link(self, match: re.Match) -> str:
        if match.re == self.regexes[0]:
            return f"[Snapchat](https://{self.fix_domain}/p/{match[1]}/{match[2]})"
        if match.re == self.regexes[1]:
            return f"[Snapchat](https://{self.fix_domain}/p/{match[1]}/{match[2]}/{match[3]})"
        return f"[Snapchat](https://{self.fix_domain}/spotlight/{match[1]})"


class PixivLink(WebsiteLink):
    """
    Pixiv website.
    """

    name = 'Pixiv'
    id = 'pixiv'

    @property
    def fix_domain(self) -> str:
        return "phixiv.net"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:www\.)?pixiv\.net/(?:\w{2}/)?artworks/(\d+)(/\d+)?/?(?:\?\S+)?",
                re.IGNORECASE),
            re.compile(
                r"https?://(?:www\.)?pixiv\.net/member_illust.php\?illust_id=(\d+)",
                re.IGNORECASE),
        ]

    def fix_link(self, match: re.Match) -> str:
        if match.re == self.regexes[1]:
            return f"[Pixiv](https://{self.fix_domain}/artworks/{match[1]})"
        return f"[Pixiv](https://{self.fix_domain}/artworks/{match[1]}{match[2] or ''})"


class IFunnyLink(WebsiteLink):
    """
    IFunny website.
    """

    name = 'IFunny'
    id = 'ifunny'

    @property
    def fix_domain(self) -> str:
        return "ifunnyez.co"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:www\.|br\.)?ifunny\.co/(?:video|picture|gif)/([\w-]+)/?(?:\?\S+)?",
                re.IGNORECASE),
        ]

    def fix_link(self, match: re.Match) -> str:
        return f"[IFunny](https://{self.fix_domain}/picture/{match[1]})"


class FurAffinityLink(WebsiteLink):
    """
    FurAffinity website.
    """

    name = 'Fur Affinity'
    id = 'furaffinity'

    @property
    def fix_domain(self) -> str:
        return "xfuraffinity.net"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:www\.)?furaffinity\.net/view/(\d+)/?(?:\?\S+)?",
                re.IGNORECASE),
        ]

    def fix_link(self, match: re.Match) -> str:
        return f"[Fur Affinity](https://{self.fix_domain}/view/{match[1]})"


class YouTubeLink(WebsiteLink):
    """
    YouTube website.
    """

    name = 'YouTube'
    id = 'youtube'

    @property
    def fix_domain(self) -> str:
        return "koutu.be"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(www\.|music\.|m\.)?youtube\.com/watch(\?\S+)",
                re.IGNORECASE),
            re.compile(
                r"https?://(?:www\.)?youtu.be/([\w-]+)(?:\?\S+)?",
                re.IGNORECASE),
            re.compile(
                r"https?://(?:www\.)?youtube.com/shorts/([\w-]+)(?:\?\S+)?",
                re.IGNORECASE),
        ]

    def fix_link(self, match: re.Match) -> str:
        if match.re == self.regexes[0]:
            subdomain = 'music.' if 'music.' == match[1] else ''
            return f"[YouTube{' Music' if subdomain else ''}](https://{subdomain}{self.fix_domain}/watch{match[2]})"
        return f"[YouTube](https://{self.fix_domain}/{match[1]})"


class CustomLink(WebsiteLink):
    """
    Custom website.
    """

    name = 'Custom'
    id = 'custom'

    def __init__(self, guild: Guild, url: str, spoiler: bool = False) -> None:
        self.custom_websites = guild.custom_websites
        super().__init__(guild, url, spoiler)

    @classmethod
    def is_enabled(cls, guild: Guild) -> bool:
        return not guild.custom_websites.is_empty()

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(fr"https?://(?:www\.)?({re.escape(website.domain)})/(.+)", re.IGNORECASE)
            for website in self.custom_websites
        ]

    def fix_link(self, match: re.Match) -> str:
        website = self.custom_websites.where('domain', match[1]).first()
        return f"[{website.name}](https://{website.fix_domain}/{match[2]})"


websites: list[Type[WebsiteLink]] = [
    TwitterLink,
    InstagramLink,
    RedditLink,
    TikTokLink,
    ThreadsLink,
    BlueskyLink,
    SnapchatLink,
    PixivLink,
    IFunnyLink,
    FurAffinityLink,
    YouTubeLink,
    CustomLink
]
