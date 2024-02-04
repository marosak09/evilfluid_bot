import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


# firebase setup
cred = credentials.Certificate("key.json")


# Realtime database initialization
ref = db.reference('/')
ref_msglog = db.reference('/settings/msglog')
ref_custom_commands = db.reference('/custom_commands')
ref_answers = db.reference('/answers')

class use_custom_cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cmd(self, ctx, command_name: str):

        response = ref_custom_commands.child(command_name).get()

        if response:
            await ctx.send(response)
        else:
            await ctx.send("Custom command not found!")

async def setup(bot):
    await bot.add_cog(use_custom_cmd(bot))



