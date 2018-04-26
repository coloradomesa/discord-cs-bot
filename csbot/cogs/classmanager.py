import discord
from discord.ext import commands
from csbot import logger_setup, get_dbclient
import string
from tabulate import tabulate
import asyncio


class ClassManager:

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.logger = logger_setup(self.__class__.__name__)
        self.dbclient = get_dbclient()
        self.class_entries = None  # to be fetched on every run of the \class command
        if self.dbclient is not None:
            self.db = self.dbclient.get_database()

    @commands.group(name="class")
    async def classmgr(self, ctx):
        """Create/join/manage class channels and roles."""
        self.logger.info(f"{ctx.invoked_subcommand} command ran by {ctx.message.author.name}")
        self.logger.debug(f"Roles on server: {', '.join([role.name for role in ctx.message.guild.roles])}")
        # Fetch the collection every time \class is called
        self.class_entries = self.db.get_collection(f"{ctx.message.guild.id}-classmgr")

    @classmgr.command()
    async def list(self, ctx):
        """List available classes to join"""
        print("test")
        async with ctx.message.channel.typing():
            msg = tabulate(
                [
                    [entry['id'], entry['name'], entry['professor-fullname']] for entry in self.class_entries.find()
                ],
                ['ID', 'Name', 'Professor']
            )
            await ctx.send(f"Class List ```{msg}```")

    @classmgr.command()
    async def join(self, ctx, cid):
        """Join a class."""
        async with ctx.message.channel.typing():
            class_entry = self.class_entries.find_one({'id': cid})
            if class_entry is not None:
                role = discord.utils.get(ctx.message.guild.roles, id=class_entry['roleid'])
                text_channel = discord.utils.get(ctx.message.guild.channels, id=class_entry['text-channel-id'])
                voice_channel = discord.utils.get(ctx.message.guild.channels, id=class_entry['voice-channel-id'])
                await ctx.author.add_roles(role)
                await self.del_msgs(
                    ctx.message,
                    await ctx.send(
                        f"Class joined! You should now be able to access #{text_channel.name} and #{voice_channel.name}")
                )

    @classmgr.command()
    async def leave(self, ctx, cid):
        """Leave a class."""
        async with ctx.message.channel.typing():
            class_entry = self.class_entries.find_one({'id': cid})
            if class_entry is not None:
                role = discord.utils.get(ctx.guild.roles, id=class_entry['roleid'])
                await ctx.author.remove_roles(role)
                await self.del_msgs(
                    ctx.message,
                    await ctx.send(f"Class left! You can rejoin at any time with \class join <class-id>")
                )

    @classmgr.command()
    async def show(self, ctx, cid):
        """Show details about a class"""
        async with ctx.message.channel.typing():
            class_entry = self.class_entries.find_one({'id': cid})
            if class_entry is not None:
                msg = tabulate(
                    [
                        ["ID", class_entry['id']],
                        ["Name", class_entry['name']],
                        ["Professor", class_entry['professor-fullname']],
                        ["Role", f"@{discord.utils.get(ctx.message.guild.roles, id=class_entry['roleid']).name}"],
                        ["Text Channel", f"#{discord.utils.get(ctx.message.guild.channels, id=class_entry['text-channel-id']).name}"],
                        ["Voice Channel", f"#{discord.utils.get(ctx.message.guild.channels, id=class_entry['voice-channel-id']).name}"]
                    ]
                )
                await ctx.send(f"```{msg}```")

    @commands.has_any_role("Instructors", "Admin")
    @classmgr.command()
    async def create(self, ctx: commands.Context, name: str):
        """Create a class, ID auto-generated"""
        async with ctx.message.channel.typing():
            guild: discord.Guild = ctx.guild
            classes_text_category = discord.utils.get(guild.categories, name="Classes-text")
            classes_text_category = await guild.create_category(
                "Classes-text") if not classes_text_category else classes_text_category
            classes_voice_category = discord.utils.get(guild.categories, name="Classes-voice")
            classes_voice_category = await guild.create_category(
                "Classes-voice") if not classes_voice_category else classes_voice_category
            ID = f"{''.join(filter(lambda x: x in set(string.printable), ctx.author.name)).strip()}-{name.replace(' ', '')}"
            role = await guild.create_role(
                name=ID,
                mentionable=True
            )
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True)
            }
            text_channel = await guild.create_text_channel(
                ID,
                overwrites=overwrites,
                category=classes_text_category
            )
            voice_channel = await guild.create_voice_channel(
                ID,
                overwrites=overwrites,
                category=classes_voice_category
            )
            entry = {
                'id': ID,
                'name': name,
                'roleid': role.id,
                'creatorid': ctx.message.author.id,
                'professor-uname': ctx.message.author.name,
                'professor-fullname': ctx.message.author.nick,
                'text-channel-id': text_channel.id,
                'voice-channel-id': voice_channel.id,
            }
            if self.class_entries.find_one({'id': entry['id']}) is not None:
                #Duplicate!
                await self.del_msgs(
                    ctx.message,
                    await ctx.send("That class already exists!")
                )
            else:
                #Not Duplicate!
                self.class_entries.insert_one(entry)
                await self.del_msgs(
                    ctx.message,
                    await ctx.send(
                        f"Created class `{ctx.message.author.name}-{name}` " +
                        f"with text channel `#{text_channel.name}` and voice channel `#{voice_channel.name}`. " +
                        f"Mention members with {role.mention}"
                    )
                )

    @commands.has_any_role("Instructors", "Admin")
    @classmgr.command()
    async def delete(self, ctx, cid):
        """Delete class"""
        async with ctx.message.channel.typing():
            guild: discord.Guild = ctx.guild
            entry = self.class_entries.find_one_and_delete({'id': cid})
            if entry is None:
                await self.del_msgs(
                    ctx.message,
                    await ctx.send(f"Class {cid} not found.")
                )
            else:
                role: discord.Role = discord.utils.get(guild.roles, id=entry['roleid'])
                text_channel = discord.utils.get(guild.channels, id=entry['text-channel-id'])
                voice_channel = discord.utils.get(guild.channels, id=entry['voice-channel-id'])
                await role.delete()
                await text_channel.delete()
                await voice_channel.delete()
                await self.del_msgs(
                    ctx.message,
                    await ctx.send(f"Class {cid} deleted successfully.")
                )

    @delete.error
    async def delete_handler(self, ctx, e):
        ctx.send(e)

    async def del_msgs(self, *args: discord.Message, delay: int = 3):
        """
        Delete messages with 5 second delay
        :param args: discord.Message objects to be deleted
        :param delay: Delay in seconds (int)
        :return: None
        """
        await asyncio.sleep(
            delay
        )
        for msg in args:
            try:
                await msg.delete()
            except AttributeError:  # handle msg == None
                pass

def setup(bot):
    bot.add_cog(ClassManager(bot))
