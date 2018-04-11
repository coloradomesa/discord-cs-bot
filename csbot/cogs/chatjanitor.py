import discord
from discord.ext import commands
from csbot import logger_setup


class ChatJanitor:
    """For admin use only"""
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.logger = logger_setup(self.__class__.__name__)

    @commands.command(hidden=True, pass_context=True)
    async def clean(self, ctx, count):
        """Clear a chat channel of X lines"""
        count = int(count)
        await self.bot.purge_from(ctx.message.channel, limit=count)


def setup(bot):
    bot.add_cog(ChatJanitor(bot))
