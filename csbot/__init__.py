from discord.ext import commands
import discord
import pkgutil
from os import listdir, environ
from os.path import isfile, join
from pymongo import MongoClient
import pymongo.errors
import pymongo.uri_parser
import urllib.parse
import logging
import sys
import csbot.cogs

description = '''Chat Bot For The CMU CS Discord Server
There are a number of utility commands being showcased here.'''

# this specifies what extensions to load when the bot starts up (from this directory)
cogs_dir = "cogs"
DISABLED_COGS_LIST = [
    "csbot.cogs.roledirector",
    "csbot.cogs.misc",
    "csbot.cogs.chatjanitor"
]

bot = commands.Bot(command_prefix='\\', description=description)


def package_contents(package):
    prefix = package.__name__ + "."
    return set(modname for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix))


@bot.event
async def on_ready():
    logger = get_logger()
    logger.debug(f"active log handlers: {', '.join([handler.__class__.__name__ for handler in logger.handlers])}")
    app_info = await bot.application_info()
    owner: discord.User = app_info.owner
    logger.info(f"Logged in as {bot.user.name} with id: '{bot.user.id}'.")
    logger.info(f"Owner of {bot.user.name} is {owner.name} with id: '{owner.id}'.")
    joinlink = f"https://discordapp.com/oauth2/authorize?client_id={app_info.id}&scope=bot&permissions=0"
    joinmsg = f"This bot is currently not joined to any servers. Join me to a server by following this link: {joinlink}"
    logger.debug(f"Invite bot to servers using this link: {joinlink}")
    if len(bot.servers) < 1:
        logger.warning(joinmsg)


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


def logger_setup(cog_name="csbot", log_level=logging.INFO):
    logger = logging.getLogger(cog_name)
    loghandler = logging.StreamHandler(stream=sys.stdout)
    logfilehandler = logging.FileHandler(f"{cog_name}.log", mode="a", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    loghandler.setFormatter(formatter)
    logfilehandler.setFormatter(formatter)
    if len(logger.handlers) < 1:
        logger.addHandler(loghandler)
        logger.addHandler(logfilehandler)
    loglevels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "WARN": logging.WARN,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }
    loglevel = loglevels.get(environ.get("CSBOT_LOGLEVEL", "INFO").upper(), log_level)
    logger.setLevel(loglevel)
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            logger.info(f"Logfile location: {handler.baseFilename}")
    return logger


def get_logger(cog_name="nsabot"):
    return logging.getLogger(cog_name)


def get_dbclient():
    logger = get_logger()
    try:
        mongodb_url = environ['CSMS_DISCORD_MONGODB_URL']
        dbclient = MongoClient(mongodb_url)
    except KeyError or TypeError or pymongo.errors.ConfigurationError as e:
        logger.error(f"Unable to setup database, missing MongoDB URL. Use env var 'CSMS_DISCORD_MONGODB_URL' with the format 'mongodb://username:password@hostname:27017/database'.")
        return None
    return dbclient


def run(token=""):
    logger = logger_setup()
    for package in package_contents(csbot.cogs):
        if str(package) not in DISABLED_COGS_LIST:
            try:
                bot.load_extension(package)
            except Exception as e:
                logger.error(f"Failed to load extension {package}.", e)
    try:
        token = environ['DISCORD_API_TOKEN']
    except KeyError as e:
        logger.error("API token required for discord api. Use 'DISCORD_API_TOKEN' to set the token.")
    bot.run(token)
