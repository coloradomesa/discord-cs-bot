import discord
from discord.ext import commands
from .utils import checks

from os import environ


class ChatJanitor:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command()
    async def clean(self, ctx, count):
        ""


def setup(bot):
    bot.add_cog(ChatJanitor(bot))
