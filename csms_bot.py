from discord.ext import commands

from os import listdir, environ
from os.path import isfile, join

description = '''Chat Bot For The CMU CS Discord Server
There are a number of utility commands being showcased here.'''

# this specifies what extensions to load when the bot starts up (from this directory)
cogs_dir = "cogs"

bot = commands.Bot(command_prefix='\\', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    for server in bot.connection.servers:
        print("Roles for server '", server.name, "'")
        for role in server.roles:
            print("    ", role.name, ":", role.id)

@bot.command(hidden=True)
async def load(extension_name : str):
    """Loads an extension."""
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await bot.say("{} loaded.".format(extension_name))

@bot.command(hidden=True)
async def unload(extension_name : str):
    """Unloads an extension."""
    bot.unload_extension(extension_name)
    await bot.say("{} unloaded.".format(extension_name))

if __name__ == "__main__":
    for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
        try:
            bot.load_extension(cogs_dir + "." + extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.')
            print(e)
    token = ""
    try:
        token = environ['DISCORD_API_TOKEN']
    except KeyError as e:
        print("ERR: API token required for discord api via env var 'DISCORD_API_TOKEN'")
    bot.run(token)
