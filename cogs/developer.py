import datetime
import json
import subprocess
import sys
from importlib import metadata

import psutil
from textwrap import shorten
from typing import Optional

import discore

__all__ = ('Developer',)

import requests

p = psutil.Process()
p.cpu_percent()


def execute_command(command: str, timeout: int = 30) -> str:
    """
    Execute a shell command
    :param command: the command to execute
    :param timeout: the timeout of the command
    :return: the output of the command
    """

    try:
        output = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        return "Command expired"
    try:
        res = []
        if stdout := output[0].decode('utf-8'):
            res.append(stdout)
        if stderr := output[1].decode('utf-8'):
            res.append(stderr)
        res = '\n'.join(res).replace("```", "'''").replace("\n", "¶")
        sanitized_output = shorten(res, width=1992, placeholder='...').replace("¶", "\n")
    except:
        return "Displaying the command result is impossible"
    return f"```\n{sanitized_output}\n```" if sanitized_output else "Command executed correctly"


class Developer(discore.Cog,
                name="developer",
                description="The bot commands"):
    @discore.app_commands.command(
        name="restart",
        description="Restart the bot")
    @discore.app_commands.guilds(discore.config.dev_guild)
    async def restart(self, i: discore.Interaction) -> None:
        i.response.send_message("Restarting...")
        await self.bot.close()
        await execute_command("pm2 restart chibraxx", timeout=60)
        exit(0)

    @discore.app_commands.command(
        name="update",
        description="Update the bot")
    @discore.app_commands.guilds(discore.config.dev_guild)
    async def update(self, i: discore.Interaction) -> None:
        await i.response.defer(thinking=True)
        await i.followup.send(execute_command("git pull"))

    @discore.app_commands.command(
        name="requirements",
        description="Update the bot requirements")
    @discore.app_commands.guilds(discore.config.dev_guild)
    async def requirements(self, i: discore.Interaction) -> None:
        await i.response.defer(thinking=True)
        await i.followup.send(execute_command("pip install --force-reinstall -r requirements.txt", timeout=120))

    @discore.app_commands.command(
        name="shell",
        description="Execute a shell command")
    @discore.app_commands.guilds(discore.config.dev_guild)
    async def shell(self, i: discore.Interaction, command: str, timeout: Optional[int] = 30) -> None:
        await i.response.defer(thinking=True)
        await i.followup.send(execute_command(command, timeout=timeout))

    @discore.app_commands.command(
        name="exec",
        description="Execute python code")
    @discore.app_commands.guilds(discore.config.dev_guild)
    async def _exec(self, i: discore.Interaction, code: str) -> None:
        await i.response.defer(thinking=True)
        code_lines = code.split('\n')
        if len(code_lines) == 1 and ";" not in code:
            code_lines[0] = f"return {code}"
        code = '\n    '.join(code_lines)
        function = f'async def _ex(self, i):\n    {code}'
        try:
            exec(function)
            res = repr(await locals()["_ex"](self, i))
        except Exception as e:
            await i.followup.send(f"```{e}```")
            return
        await i.followup.send(
            f"```py\n{discore.utils.sanitize(res, limit=1990)}\n```")

    @discore.app_commands.command(
        name="log",
        description="Get the bot log")
    @discore.app_commands.guilds(discore.config.dev_guild)
    async def log(self, i: discore.Interaction) -> None:
        with open(discore.config.log.file, encoding='utf-8') as f:
            logs = f.read()
        await i.response.send_message(
            f"```\n{discore.sanitize(logs, 1992, replace_newline=False, crop_at_end=False)}\n```")

    @discore.app_commands.command(
        name="runtime",
        description="Get the bot runtime")
    @discore.app_commands.guilds(discore.config.dev_guild)
    async def runtime(self, i: discore.Interaction) -> None:
        global p

        direct_url = json.loads([p for p in metadata.files('discore') if 'direct_url.json' in str(p)][0].read_text())
        author, repo = direct_url["url"].removeprefix("https://github.com/").split("/")
        discore_commit = direct_url["vcs_info"]["commit_id"]
        discore_commit_api_url = f"https://api.github.com/repos/{author}/{repo}/commits/{discore_commit}"
        raw_commit_date = requests.get(discore_commit_api_url).json()["commit"]["committer"]["date"]
        datetime_commit_date = datetime.datetime.strptime(
            raw_commit_date, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=2)
        commit_date = int(datetime_commit_date.timestamp())

        e = discore.Embed(
            title="Runtime",
            color=discore.config.color or None)
        e.add_field(
            name="Bot Version",
            value=discore.config.version)
        e.add_field(
            name="Bot commit",
            value='`' + subprocess.check_output('git log -1 --pretty=format:"%h"', shell=True, encoding='utf-8') + '`')
        e.add_field(
            name="Bot commit date",
            value="<t:" + subprocess.check_output(
                'git log -1 --pretty=format:"%ct"', shell=True, encoding='utf-8') + ":f>")
        e.add_field(
            name="Discore Version",
            value=metadata.version('discore'))
        e.add_field(
            name="Discore commit",
            value=f"`{discore_commit[:7]}`")
        e.add_field(
            name="Discore commit date",
            value=f"<t:{int(commit_date)}:f>")
        e.add_field(
            name="Discord.py Version",
            value=metadata.version('discord.py'))
        e.add_field(
            name="Python Version",
            value='.'.join(map(str, sys.version_info[:3])))
        e.add_field(
            name="Platform",
            value=sys.platform)
        e.add_field(
            name="Start time",
            value=f"<t:{int(self.bot.start_time.timestamp())}:f>")
        e.add_field(
            name="Uptime",
            value=f"<t:{int(self.bot.start_time.timestamp())}:R>")
        e.add_field(
            name="Current time",
            value=f"<t:{int(datetime.datetime.now().timestamp())}:f>")
        e.add_field(
            name="Memory usage",
            value=f"{p.memory_info().rss / 1024 / 1024:.2f} MB")
        e.add_field(
            name="CPU usage",
            value=f"{p.cpu_percent():.2f} %")
        e.set_footer(
            text=self.bot.user.name + (
                f" | ver. {discore.config.version}" if discore.config.version else ""),
            icon_url=self.bot.user.display_avatar.url
        )
        discore.set_embed_footer(self.bot, e)

        await i.response.send_message(embed=e)
