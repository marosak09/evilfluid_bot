import discord
from discord.ext import commands
from firebase_admin import credentials, db

# firebase setup
cred = credentials.Certificate("key.json")

# Realtime database initialization
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=".", intents=intents)
client.remove_command('help')

index = "."

def get_guild_ref(guild_id):
    return db.reference(f'servers/{guild_id}')

class RemoveWarnRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_to_remove = None  # Přidáváme globální proměnnou pro uchování nastavené role

    @commands.command()
    async def role_to_remove(self, ctx, role: discord.Role):
        guild_id = ctx.guild.id
        guild_ref = get_guild_ref(guild_id)

        role_to_remove_ref = guild_ref.child('settings/role_to_remove')

        if role_to_remove_ref.get():
            old_role_to_remove_id = role_to_remove_ref.get()
            old_role_to_remove = ctx.guild.get_role(old_role_to_remove_id)

            if old_role_to_remove:
                await ctx.send(
                    f"Replacing second warn role from {old_role_to_remove.mention} to {role.mention}"
                )
            else:
                await ctx.send(f"Setting second warn role to {role.mention}")

        self.role_to_remove = role
        save_config(guild_id, self.role_to_remove)

        await ctx.send(f"Second Warn role set to {role.mention}")

def save_config(guild_id, role_to_remove):
    if role_to_remove:
        guild_ref = get_guild_ref(guild_id)
        ref_role_to_remove = guild_ref.child('settings/role_to_remove')
        ref_role_to_remove.set(role_to_remove.id)

async def setup(bot):
    await bot.add_cog(RemoveWarnRole(bot))
