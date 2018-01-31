import discord
from discord.ext import commands
from .utils import checks

from os import environ


class Misc:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    def __str__(self):
        return "Miscellaneous"

    @commands.command()
    async def git(self):
        """Show the url for the github repository"""
        await self.bot.say("View my github at https://github.com/coloradomesa/discord-cs-bot")



def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(Misc(bot))
    print(bot.help_attrs)

