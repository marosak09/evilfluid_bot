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


class remove_warn_role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def remove_warn_role(self, ctx, role: discord.Role):
      second_warn_role_ref = db.reference('/settings/second_warn_role')
      if second_warn_role_ref.get():
        old_second_warn_role_id = second_warn_role_ref.get()
        old_second_warn_role = ctx.guild.get_role(old_second_warn_role_id)
        if old_second_warn_role:
          await ctx.send(
            f"Replacing second warn role from {old_second_warn_role.mention} to {role.mention}"
          )
        else:
          await ctx.send(f"Setting second warn role to {role.mention}")
      second_warn_role_ref.set(role.id)
      await ctx.send(f"Second Warn role set to {role.mention}")


async def setup(bot):
    await bot.add_cog(remove_warn_role(bot))



