import discord
from discord.ext import commands

# Variables
version = "2.6.4"
emico = "https://media.discordapp.net/attachments/1179492325957840926/1190400494699552928/IMG_1124.png?ex=65a1a9da&is=658f34da&hm=cf80c472c2fb38010a58d69c13056a714134bdd590ed9e885a4af64b68126b83&=&format=webp&quality=lossless&width=640&height=662"
name = "Henri's bot"


class about(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="about", help="Display information about the bot.")
    async def about(self, ctx):
        em = discord.Embed(title="About",
                           description="Bot info",
                           color=discord.Colour.yellow())
        em.set_author(name=name, icon_url=emico)
        em.add_field(name="Created by Marosak09", value="© Marosak09 2022/23")
        em.set_footer(text=f"{name} v{version}")
        await ctx.send(embed=em)

async def setup(bot):
    await bot.add_cog(about(bot))

