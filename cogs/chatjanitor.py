import discord
from discord.ext import commands
from .utils import checks

from os import environ


class ChatJanitor:
    """For admin use only"""
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command(hidden=True, pass_context=True)
    async def clean(self, ctx, count):
        """Clear a chat channel of X lines"""
        count = int(count)
        await self.bot.purge_from(ctx.message.channel, limit=count)

def setup(bot):
    bot.add_cog(ChatJanitor(bot))
