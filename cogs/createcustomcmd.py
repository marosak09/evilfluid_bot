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

class createcustomcmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="createcmd", help="create ur custom command")
    async def createcmd(self, ctx, command_name: str, response: str):

        custom_command_ref = ref.child('custom_commands').child(command_name)

        # check existence
        if custom_command_ref.get():
            await ctx.send(f"Custom command '{command_name}' already exists!")
        else:
            # create new custom cmd
            custom_command_ref.set(response)
            await ctx.send(f"Custom command '{command_name}' created!")

async def setup(bot):
    await bot.add_cog(createcustomcmd(bot))