import re
from typing import Optional, Self

import discore

from database.models.Guild import *

__all__ = ('WebsiteLink', 'TwitterLink', 'InstagramLink', 'CustomLink')


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
        return "https://fxtwitter.com"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:www\.)?(?:twitter\.com|x\.com|nitter\.net)/(\w+)"
                r"/status/(\d+)(/(?:photo|video)/\d)?/?(?:\?\S+)?")
        ]

    def fix_link(self, match: re.Match) -> Optional[str]:
        fxtwitter_link = f"{self.fix_domain}/{match[1]}/status/{match[2]}"
        fxtwitter_link += match[3] or ''
        fxtwitter_link += ('/' + self.guild.twitter_tr_lang) if self.guild.twitter_tr else ''
        return (
            f"[Tweet • {discore.escape_markdown(match[1])}]({fxtwitter_link})")


class InstagramLink(WebsiteLink):
    """
    Instagram website.
    """

    name = 'Instagram'
    id = 'instagram'

    @property
    def fix_domain(self) -> str:
        return "https://ddinstagram.com"

    @property
    def regexes(self) -> list[re.Pattern[str]]:
        return [
            re.compile(
                r"https?://(?:www\.)?instagram\.com/(p|reels?)/([\w-]+)/?(\?\S+)?"
            )
        ]

    def fix_link(self, match: re.Match) -> str:
        return f"[Instagram]({self.fix_domain}/{match[1]}/{match[2]}{match[3] or ''})"


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
            re.compile(fr"https?://(?:www\.)?({website.domain})/(.+)")
            for website in self.custom_websites
        ]

    def fix_link(self, match: re.Match) -> str:
        website = self.custom_websites.where('domain', match[1]).first()
        return f"[{website.name}](https://{website.fix_domain}/{match[2]})"
