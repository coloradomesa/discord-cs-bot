import discord
from discord.ext import commands
from csbot import logger_setup, get_dbclient


class ClassManager:

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.logger = logger_setup(self.__class__.__name__)
        self.dbclient = get_dbclient()
        self.class_entries = None  # to be fetched on every run of the \class command
        if self.dbclient is not None:
            self.db = self.dbclient.get_database()

    @commands.group(name='class', pass_context=True)
    async def classmgr(self, ctx):
        """Create/join/manage class channels and roles. Creation/deletion delegated to admins/instructors ONLY."""
        self.logger.info(f"{ctx.invoked_subcommand} command ran by {ctx.message.author.name}")
        self.logger.debug(f"Roles on server: {', '.join([role.name for role in ctx.message.server.roles])}")
        # Fetch the collection every time \class is called
        self.class_entries = self.db.get_collection(f"{ctx.message.server.id}-classmgr")

    @classmgr.command(name='list', pass_context=True)
    async def classlist(self, ctx):
        from tabulate import tabulate
        """List available classes to join"""
        self.logger.info(f"fetched list of classes to channel #{ctx.message.channel.name}")
        self.logger.debug(f"fetched list of classes: {', '.join([entry['id'] for entry in self.class_entries.find()])}")
        msg = tabulate(
            [
                [entry['id'], entry['name'], entry['professor-fullname']] for entry in self.class_entries.find()
            ],
            ['ID', 'Name', 'Professor']
        )
        await self.bot.say(f"Class List ```{msg}```")

    @classmgr.command(name='join', pass_context=True)
    async def classjoin(self, ctx, cid):
        """Join a class. Usage: \class join <classid>"""
        class_entry = self.class_entries.find_one({'id': cid})
        if class_entry is not None:
            role = discord.utils.get(ctx.message.server.roles, id=class_entry['roleid'])
            text_channel = discord.utils.get(ctx.message.server.channels, id=class_entry['text-channel-id'])
            voice_channel = discord.utils.get(ctx.message.server.channels, id=class_entry['voice-channel-id'])
            await self.bot.add_roles(ctx.message.author, role)
            await self.bot.say(f"Class joined! You should now be able to access #{text_channel.name} and #{voice_channel.name}")

    @classmgr.command(name="leave", pass_context=True)
    async def classleave(self, ctx, cid):
        """Leave a class. Usage: \class leave <classid>"""
        class_entry = self.class_entries.find_one({'id': cid})
        if class_entry is not None:
            role = discord.utils.get(ctx.message.server.roles, id=class_entry['roleid'])
            await self.bot.remove_roles(ctx.message.author, role)
            await self.bot.say(f"Class left! You can rejoin at any time with \class join <class-id>")

    @classmgr.command(name="show", pass_context=True)
    async def classshow(self, ctx, cid):
        from tabulate import tabulate
        """Show details about a class. Usage: \class show <classid>"""
        class_entry = self.class_entries.find_one({'id': cid})
        if class_entry is not None:
            msg = tabulate(
                [
                    ["ID", class_entry['id']],
                    ["Name", class_entry['name']],
                    ["Professor", class_entry['professor-fullname']],
                    ["Role", f"@{discord.utils.get(ctx.message.server.roles, id=class_entry['roleid']).name}"],
                    ["Text Channel", f"#{discord.utils.get(ctx.message.server.channels, id=class_entry['text-channel-id']).name}"],
                    ["Voice Channel", f"#{discord.utils.get(ctx.message.server.channels, id=class_entry['voice-channel-id']).name}"]
                ]
            )
            await self.bot.say(f"```{msg}```")

    @commands.has_any_role("Instructors", "Admin")
    @classmgr.command(name="create", pass_context=True)
    async def classcreate(self, ctx, name):
        """Create a class, ID auto-generated. Usage: \class create <class name>"""
        role = await self.bot.create_role(
            ctx.message.server,
            name=f"{ctx.message.author.name}-{name}",
            managed=True,
            mentionable=True
        )
        text_channel = await self.bot.create_channel(
            ctx.message.server,
            f"{ctx.message.author.name}-{name}",
            discord.ChannelPermissions(
                target=ctx.message.server.default_role,
                overwrite=discord.PermissionOverwrite(read_messages=False)
            ),
            discord.ChannelPermissions(
                target=role,
                overwrite=discord.PermissionOverwrite(read_messages=True)
            ),
            type=discord.ChannelType.text
        )
        voice_channel = await self.bot.create_channel(
            ctx.message.server,
            f"{ctx.message.author.name}-{name}-voice",
            discord.ChannelPermissions(
                target=ctx.message.server.default_role,
                overwrite=discord.PermissionOverwrite(read_messages=False)
            ),
            discord.ChannelPermissions(
                target=role,
                overwrite=discord.PermissionOverwrite(read_messages=True)
            ),
            type=discord.ChannelType.voice
        )
        entry = {
            'id': f"{ctx.message.author.name}-{name}",
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
            await self.bot.say("That class already exists!")
        else:
            #Not Duplicate!
            self.class_entries.insert_one(entry)
            await self.bot.say(
                f"Created class `{ctx.message.author.name}-{name}` " +
                f"with text channel `#{text_channel.name}` and voice channel `#{voice_channel.name}`. " +
                f"Mention members with {role.mention}"
            )

    @commands.has_any_role("Instructors", "Admin")
    @classmgr.command(name="delete", pass_context=True)
    async def classdelete(self, ctx, cid):
        """Delete class. Usage: \class delete <classid>"""
        entry = self.class_entries.find_one_and_delete({'id': cid})
        if entry is None:
            await self.bot.say(f"Class {cid} not found.")
        else:
            role = discord.utils.get(ctx.message.server.roles, id=entry['roleid'])
            text_channel = discord.utils.get(ctx.message.server.channels, id=entry['text-channel-id'])
            voice_channel = discord.utils.get(ctx.message.server.channels, id=entry['voice-channel-id'])
            await self.bot.delete_role(ctx.message.server, role)
            await self.bot.delete_channel(text_channel)
            await self.bot.delete_channel(voice_channel)
            await self.bot.say(f"Class {cid} deleted successfully.")

    @classdelete.error
    async def classdelete_handler(self, ctx, e):
        self.bot.send_message(ctx.message.channel, e)


def setup(bot):
    bot.add_cog(ClassManager(bot))
