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

class warn_role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def warn_role(self, ctx, role: discord.Role):
      warn_role_ref = db.reference('/settings/warn_role')
      if warn_role_ref.get():
        old_warn_role_id = warn_role_ref.get()
        old_warn_role = ctx.guild.get_role(old_warn_role_id)
        if old_warn_role:
          await ctx.send(
            f"Replacing warn role from {old_warn_role.mention} to {role.mention}")
        else:
          await ctx.send(f"Setting warn role to {role.mention}")
      warn_role_ref.set(role.id)
      await ctx.send(f"Warn role set to {role.mention}")

async def setup(bot):
    await bot.add_cog(warn_role(bot))




