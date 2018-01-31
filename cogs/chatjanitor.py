import discord
from discord.ext import commands
from .utils import checks

from os import environ


class ChatJanitor:
    """For admin use only"""
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def clean(self, ctx, count):
        ""


def setup(bot):
    bot.add_cog(ChatJanitor(bot))
