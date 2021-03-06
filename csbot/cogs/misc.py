import discord
from discord.ext import commands
from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
from csbot import logger_setup


class Misc:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.logger = logger_setup(self.__class__.__name__)
        self.packturl = "https://www.packtpub.com/packt/offers/free-learning"

    def __str__(self):
        return "Miscellaneous"

    @commands.command()
    @commands.has_any_role("Instructors", "Admins")
    async def clear(self, ctx, count):
        """Clear a chat channel of N lines"""
        async with ctx.message.channel.typing():
            count = int(count)
            await ctx.message.channel.purge(limit=count)
            logging.debug(f"Cleared {count} messages from channel {ctx.message.channel} in server {ctx.message.guild}")
            outmsg = await ctx.message.channel.send(f"✅Cleared {count} messages")
        await self.del_msgs(outmsg)

    @commands.command()
    async def git(self, ctx):
        """Show the url for the github repository"""
        await ctx.send("View my github at https://github.com/coloradomesa/discord-cs-bot")
        self.logger.info(f"Sent git info to channel #{ctx.message.channel.name} in {ctx.message.server.name}")

    @commands.command()
    async def packt(self, ctx):
        """Show the free book of the day from Packtpub publishing"""
        info = await self.scrape_packt()
        embedout = discord.Embed()
        embedout.title = str(info['title'])
        timeleft = datetime.datetime.fromtimestamp(int(info['expire_timestamp'])) - datetime.datetime.now()
        embedout.url = self.packturl
        imgurl = "http:{}".format(info['img_src'].replace(" ", "%20"))
        embedout.set_image(url=imgurl)
        embedout.set_footer(text=f"Time Left: {str(timeleft)} (expires at {datetime.datetime.fromtimestamp(int(info['expire_timestamp']), tz=datetime.timezone.utc)} UTC)")
        await ctx.send(embed=embedout)
        self.logger.info(f"Sent git info to channel #{ctx.message.channel.name} in {ctx.message.server.name}")

    async def scrape_packt(self):
        info = {}
        sock = urlopen(self.packturl)
        htmlSource = sock.read()
        soup = BeautifulSoup(htmlSource, "html.parser")
        content = soup.find('div', id='content')
        info['expire_timestamp'] = content.find("span", class_="packt-js-countdown")['data-countdown-to']
        info['title'] = " ".join(content.find("div", class_="dotd-title").text.split())
        info['img_src'] = content.find(
            "div", class_="dotd-main-book-image float-left").find("img").attrs['src']
        return info


def setup(bot: discord.ext.commands.Bot):
    bot.add_cog(Misc(bot))
    print(bot.help_attrs)

