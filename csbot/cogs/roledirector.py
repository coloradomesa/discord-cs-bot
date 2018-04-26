import discord
from discord.ext import commands
from csbot import logger_setup
from os import environ


class RoleDirector:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.logger = logger_setup(self.__class__.__name__)
        self.student_role = None
        self.alumni_role = None
        self.admin_role = None

    @commands.command(name='namechange', pass_context=True)
    async def namechange(self, ctx):
        """Set your nickname and choose a role"""
        self.logger.info(f"{ctx.message.author.nick} asked for namechange")
        self.student_role = discord.utils.get(ctx.guild.roles, name="Students")
        self.alumni_role = discord.utils.get(ctx.guild.roles, name="Alumni")
        self.admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
        await self._namechange(ctx.message.author, ctx.message.guild)

    async def _namechange(self, member: discord.Member, server: discord.Guild):
        initmsg: discord.Message = await member.send("What is your first name?")
        dm_channel: discord.DMChannel = initmsg.channel
        firstnamemsg = await self.bot.wait_for('message', check=lambda m: m.channel == dm_channel and m.author == dm_channel.recipient)
        await member.send("What is your last name?")
        lastnamemsg = await self.bot.wait_for('message', check=lambda m: m.channel == dm_channel and m.author == dm_channel.recipient)
        if self.student_role not in member.roles and self.alumni_role not in member.roles:
            role_options = {
                '🇦': ("Student", self.student_role),
                '🇧': ("Alumni", self.alumni_role),
            }
            role_menu_format = """
What are you?
{}
                        """
            role_menu: discord.Message = await member.send(role_menu_format.format(
                '\n'.join([f"{str(option)}: {str(role_options[option][0])}" for option in role_options.keys()])))
            for option in role_options.keys():
                await role_menu.add_reaction(option)
            reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: u == dm_channel.recipient)
            await member.add_roles(role_options[reaction.emoji][1])
        name_options = {
            '🇦': f"{firstnamemsg.content} {lastnamemsg.content[0]}",
            '🇧': f"{firstnamemsg.content} {lastnamemsg.content}"
        }
        name_menu_format = """
How would you like your name displayed?
{}
                    """
        name_menu = await member.send(name_menu_format.format(
            '\n'.join([f"{str(option)}: {str(name_options[option])}" for option in name_options.keys()])))
        for option in name_options.keys():
            await name_menu.add_reaction(option)
        reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: u == dm_channel.recipient)
        member.nick = name_options[reaction.emoji]
        await member.send("Thank you! You should now be able to access all chat channels on the server.")
        default_channel: discord.TextChannel = None
        for channel in server.channels:
            if isinstance(channel, discord.TextChannel) and channel.name == "general":
                default_channel = channel
                break
        self.logger.info(f"{member.name} is now known as {member.nick}. Name change successful.")
        await default_channel.send(f"{member.name} is now known as {member.nick}. Welcome, {member.mention}!")

    async def on_member_join(self, member: discord.Member):
        """Says when a member joined."""
        if member.guild.id == environ.get('CSMS_DISCORD_SERVER_ID'):
            self.logger.info(f"{member.name} joined {member.guild.name}")
            await self._namechange(member, member.server)


def setup(bot):
    bot.add_cog(RoleDirector(bot))
