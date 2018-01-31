import discord
from discord.ext import commands
from .utils import checks

from os import environ


class RoleDirector():
    """Adjust your account and change roles"""

    def __str__(self):
        return "AccountManagement"

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.student_roleid = environ.get('CSMS_DISCORD_STUDENT_ROLE_ID')
        self.alumni_roleid = environ.get('CSMS_DISCORD_ALUMNI_ROLE_ID')
        self.admin_roleid = environ.get('CSMS_DISCORD_ADMIN_ROLE_ID')
        self.student_role = None
        self.alumni_role = None
        self.admin_role = None


    @commands.command(name='namechange', pass_context=True)
    async def namechange(self, ctx):
        """Set your nickname and choose a role"""
        server = await self.bot.get_server(environ.get('CSMS_DISCORD_SERVER_ID'))
        await self._namechange(ctx.message.author, server if server is not None else ctx.message.server)

    async def _namechange(self, member: discord.Member, server: discord.Server):
        for role in server.roles:
            if self.student_roleid == role.id:
                self.student_role = role
            if self.alumni_roleid == role.id:
                self.alumni_role = role
            if self.admin_roleid == role.id:
                self.admin_role = role
        initmsg: discord.Message = await self.bot.send_message(member, "What is your first name?")
        firstnamemsg = await self.bot.wait_for_message(author=member, channel=initmsg.channel)
        await self.bot.send_message(member, "What is your last name?")
        lastnamemsg = await self.bot.wait_for_message(author=member, channel=initmsg.channel)
        if self.student_role not in member.roles and self.alumni_role not in member.roles:
            role_options = {
                '🇦': ("Student", self.student_role),
                '🇧': ("Alumni", self.alumni_role),
            }
            role_menu_format = """
What are you?
{}
                        """
            role_menu = await self.bot.send_message(member, role_menu_format.format(
                '\n'.join([f"{str(option)}: {str(role_options[option][0])}" for option in role_options.keys()])))
            for option in role_options.keys():
                await self.bot.add_reaction(role_menu, option)
            res = await self.bot.wait_for_reaction(user=member, message=role_menu)
            await self.bot.add_roles(member, role_options[res.reaction.emoji][1])
        name_options = {
            '🇦': f"{firstnamemsg.content} {lastnamemsg.content[0]}",
            '🇧': f"{firstnamemsg.content} {lastnamemsg.content}"
        }
        name_menu_format = """
How would you like your name displayed?
{}
                    """
        name_menu = await self.bot.send_message(member, name_menu_format.format(
            '\n'.join([f"{str(option)}: {str(name_options[option])}" for option in name_options.keys()])))
        for option in name_options.keys():
            await self.bot.add_reaction(name_menu, option)
        res = await self.bot.wait_for_reaction(user=member, message=name_menu)
        await self.bot.change_nickname(member, name_options[res.reaction.emoji])
        await self.bot.send_message(member,
                                    "Thank you! You should now be able to access all chat channels on the server.")
        default_channel: discord.Channel = None
        for channel in server.channels:
            if channel.type is discord.ChannelType.text:
                default_channel = channel
                break
        print("Server id: ", server.id)
        print("Channel id: ", default_channel.id)
        print("Channel type: ", default_channel.type)
        await self.bot.send_message(default_channel, f"{member.name} is now known as {member.nick}. Welcome, {member.mention}!")

    async def on_member_join(self, member: discord.Member):
        """Says when a member joined."""
        if member.server.id == environ.get('CSMS_DISCORD_SERVER_ID'):
            await self._namechange(member, member.server)

    @commands.command(pass_context=True, hidden=True)
    async def _menutest(self, ctx):
        template = """
Vote an option:
🇦 this one ({})
🇧 this one ({})
🇨 this one ({})
"""
        menu: discord.Message = await self.bot.send_message(ctx.message.channel, template.format(0, 0, 0))
        await self.bot.add_reaction(menu, '🇦')
        await self.bot.add_reaction(menu, '🇧')
        await self.bot.add_reaction(menu, '🇨')
        while True:
            res = await self.bot.wait_for_reaction(message=menu)
            menu = await self.bot.get_message(menu.channel, menu.id)
            await self.bot.edit_message(
                menu,
                template.format(
                    menu.reactions[0].count,
                    menu.reactions[1].count,
                    menu.reactions[2].count
                )
            )
            if res.user != self.bot.connection.user:
                await self.bot.remove_reaction(menu, res.reaction.emoji, res.user)

    @commands.group(pass_context=True, hidden=True)
    async def _cool(self, ctx):
        """Says if a user is cool.
        In reality this just checks if a subcommand is being invoked.
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

    @_cool.command(name='bot')
    async def _bot(self):
        """Is the bot cool?"""
        await self.bot.say('Yes, the bot is cool.')


def setup(bot):
    bot.add_cog(RoleDirector(bot))
