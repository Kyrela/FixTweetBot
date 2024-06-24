import re
from typing import Optional, Self

import discore

from database.models.Guild import *

__all__ = ('WebsiteLink', 'TwitterLink', 'InstagramLink')


class WebsiteLink:
    """
    Base class for all websites.
    """

    name: str
    id: str
    regexes: list[re.Pattern[str]]
    fix_domain: str

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
        self.enabled = guild.__getattr__(self.id)
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
    regexes = [
        re.compile(
            r"https?://(?:www\.)?(?:twitter\.com|x\.com|nitter\.net)/(\w+)"
            r"/status/(\d+)(/(?:photo|video)/\d)?/?(?:\?\S+)?")
    ]
    fix_domain = "https://fxtwitter.com"

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
    regexes = [
        re.compile(
            r"https?://(?:www\.)?instagram\.com/(p|reels?)/([\w-]+)/?(\?\S+)?"
        )
    ]
    fix_domain = "https://ddinstagram.com"

    def fix_link(self, match: re.Match) -> str:
        return f"[Instagram]({self.fix_domain}/{match[1]}/{match[2]}{match[3] or ''})"
