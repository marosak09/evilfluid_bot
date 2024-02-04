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

def save_config():
  global log_channel
  if log_channel:
    ref_msglog.set(log_channel.id)

class log_setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def log_room(self, ctx, channel: discord.TextChannel):
      global log_channel
      if log_channel:
        await ctx.send(
          f"Replacing log room from {log_channel.mention} to {channel.mention}")
        await log_channel.send("This channel has been unassigned as the log room.")
        await log_channel.send(embed=discord.Embed(description="Thank you!",
                                                  color=discord.Color.green()))
      log_channel = channel
      save_config()
      await ctx.send(f"Log room is set to: {channel.mention}")

async def setup(bot):
    await bot.add_cog(log_setup(bot))

