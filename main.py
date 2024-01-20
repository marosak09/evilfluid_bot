import discord
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests
from server import server

server()

# Firebase
# Initialization
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(
  cred, {
    'databaseURL':
    'https://henri-s-bot-default-rtdb.europe-west1.firebasedatabase.app/'
  })

# Realtime database initialization
ref = db.reference('/')
ref_msglog = db.reference('/settings/msglog')
ref_custom_commands = db.reference('/custom_commands')
ref_answers = db.reference('/answers')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=".", intents=intents)
client.remove_command('help')

index = "."
version = "2.6.4"
emico = "https://media.discordapp.net/attachments/1179492325957840926/1190400494699552928/IMG_1124.png?ex=65a1a9da&is=658f34da&hm=cf80c472c2fb38010a58d69c13056a714134bdd590ed9e885a4af64b68126b83&=&format=webp&quality=lossless&width=640&height=662"
name = "Henri's bot"

# Log channel cfg
log_channel = None


def load_config():
  global log_channel
  log_channel_id = ref_msglog.get()
  if log_channel_id:
    log_channel = client.get_channel(int(log_channel_id))


def save_config():
  global log_channel
  if log_channel:
    ref_msglog.set(log_channel.id)


# activity
@client.event
async def on_ready():
  load_config()
  print("Bot running....")
  await client.change_presence(status=discord.Status.idle,
                               activity=discord.Game(f"{index}help"))


# Error handling
@client.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.MissingRequiredArgument):
    await ctx.send(f"Missing arguments, try {index}help")
  else:
    await ctx.send(f"An error occurred: {error}")


# all messages logging
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  save_message_to_db(message)

  if message.content.startswith("."):
    await client.process_commands(message)


def save_message_to_db(message):
  message_content = message.content
  message_channel = message.channel.name
  message_author_name = str(message.author)
  message_author_id = message.author.id
  message_id = message.id

  # Create a dictionary with the user's tag, message content, and other details
  message_data = {
    "msg_content": message_content,
    "msg_channel": message_channel,
    "author_name": message_author_name,
    "author_id": message_author_id
  }

  try:
    messages_ref = db.reference(f'/messages/{message_id}')
    messages_ref.update(message_data)
  except Exception as e:
    print(f"Error saving message to database: {e}")


# Logging deleted messages
@client.event
async def on_message_delete(message):
  global log_channel
  if log_channel is not None:
    deleted_msg_content = message.content
    deleted_msg_author = message.author.name
    deleted_msg_channel = message.channel.name

    embed = discord.Embed(title="Deleted Message Log", color=0xFF0000)
    embed.add_field(name="Author", value=deleted_msg_author, inline=False)
    embed.add_field(name="Channel", value=deleted_msg_channel, inline=False)
    embed.add_field(name="Message", value=deleted_msg_content, inline=False)

    await log_channel.send(embed=embed)


# Help command
@client.group(invoke_without_command=True)
async def help(ctx):
  if ctx.invoked_subcommand is None:
    em = discord.Embed(title="Help",
                       description="Help with categories",
                       color=discord.Color.gold())
    em.set_author(name=name, icon_url=emico)
    em.add_field(name="Moderation", value="`.help moderation`", inline=False)
    em.add_field(name="Setup", value="`.help setup`", inline=False)
    em.add_field(name="Fun", value="`.help fun`", inline=False)
    em.add_field(name="Other", value="`.help other`", inline=False)
    em.set_footer(text=f"{name} v{version}")
    await ctx.send(embed=em)


@help.command()
async def moderation(ctx):
  em = discord.Embed(title="Moderation Help",
                     description="Help with moderation commands",
                     color=discord.Color.blue())
  em.add_field(name="Kick",
               value="Kick a member: `.kick <user> <reason>`",
               inline=False)
  em.add_field(name="Ban",
               value="Ban a member: `.ban <user> <reason>`",
               inline=False)
  em.add_field(name="Add Role",
               value="Add role to member: `.add_role <role> <member>`",
               inline=False)
  em.add_field(name="Clear",
               value="Clear messages: `.clear <msgcount>`",
               inline=False)
  em.add_field(name="Warn",
               value="Warn member: `.warn <member> <reason>`",
               inline=False)
  await ctx.send(embed=em)


@help.command()
async def setup(ctx):
  em = discord.Embed(title="Setup Help",
                     description="Help with setup commands",
                     color=discord.Color.blue())
  em.add_field(name="Server Info",
               value="Display server info: `.server_info`",
               inline=False)
  em.add_field(name="Log Room",
               value="Set log room: `.log_room <#text_channel>`",
               inline=False)
  em.add_field(
    name="Warn roles",
    value=
    "Set warn role: `.warn_role <role>`\nRemove role after warn: `.second_warn_role <role>`",
    inline=False)
  await ctx.send(embed=em)


@help.command()
async def fun(ctx):
  em = discord.Embed(title="Fun Help",
                     description="Help with fun commands",
                     color=discord.Color.blue())
  em.add_field(name="Ping", value="Ping the bot: `.ping`", inline=False)
  em.add_field(name="Meme", value="Fetch a meme: `.meme`", inline=False)
  em.add_field(name="Reddit",
               value="Get a Reddit post: `.reddit <subreddit>`",
               inline=False)
  em.add_field(
    name="Custom Command",
    value=
    "Create custom command: `.createcmd <question> <answer>`\nUse custom command: `.cmd <custom cmd name>`",
    inline=False)
  await ctx.send(embed=em)


@help.command()
async def other(ctx):
  em = discord.Embed(title="Other Help",
                     description="Help with other commands",
                     color=discord.Color.blue())
  em.add_field(name="About", value="Show bot info: `.about`", inline=False)
  em.add_field(name="Changelog",
               value="Show bot changelog: `.changelog`",
               inline=False)
  await ctx.send(embed=em)


# About
@client.command(invoke_without_command=True)
async def about(ctx):
  em = discord.Embed(title="About",
                     description="Bot info",
                     color=discord.colour.Color.yellow())
  em.set_author(name=name, icon_url=emico)
  em.add_field(name="Created by Marosak09", value="© Marosak09 2022/23")
  em.set_footer(text=f"{name} v{version}")
  await ctx.send(embed=em)


# Changelog
@client.command(invoke_without_command=True)
async def changelog(ctx):
  em = discord.Embed(title="Changelog",
                     description=f"{name} v{version}",
                     color=discord.colour.Color.yellow())
  em.set_author(name=name, icon_url=emico)
  em.add_field(name="Moderation", value="`Message logs`")
  em.add_field(
    name="Bot",
    value=
    "`Better error handling, some small improvements, message logs, connection to database, new commands`"
  )
  em.set_footer(text=f"{name} v{version}")
  await ctx.send(embed=em)


# server info
@client.command()
async def server_info(ctx):
  guild = ctx.guild
  member_count = guild.member_count
  channels = len(guild.channels)
  em = discord.Embed(title=f"Server Info - {guild.name}",
                     color=discord.Color.blue())
  em.add_field(name="Member Count", value=member_count)
  em.add_field(name="Channel Count", value=channels)
  await ctx.send(embed=em)


# Fun commands


# Ping
@client.command()
async def ping(ctx):
  await ctx.send("Pong!")


# create custom cmd
@client.command()
#@commands.has_role('role')  # specify rule
async def createcmd(ctx, command_name: str, response: str):

  custom_command_ref = ref.child('custom_commands').child(command_name)

  # check existence
  if custom_command_ref.get():
    await ctx.send(f"Custom command '{command_name}' already exists!")
  else:
    # create new custom cmd
    custom_command_ref.set(response)
    await ctx.send(f"Custom command '{command_name}' created!")


# use custom cmd
@client.command()
async def cmd(ctx, command_name: str):

  response = ref_custom_commands.child(command_name).get()

  if response:
    await ctx.send(response)
  else:
    await ctx.send("Custom command not found!")


# Meme
@client.command()
async def meme(ctx):
  response = requests.get("https://meme-api.com/gimme")
  data = response.json()

  memeUrl = data["url"]
  memeName = data["title"]
  memePoster = data["author"]
  memeSub = data["subreddit"]
  memeLink = data["postLink"]

  em = discord.Embed(title=memeName, color=discord.colour.Color.yellow())
  em.set_image(url=memeUrl)
  em.set_footer(
    text=f"Created by: {memePoster}, subreddit: {memeSub}, post: {memeLink}")
  await ctx.send(embed=em)


# Reddit
@client.command()
async def reddit(ctx, sub):
  response = requests.get(f"https://meme-api.com/gimme/{sub}")
  data = response.json()

  redditURL = data["url"]
  redditName = data["title"]
  redditPoster = data["author"]
  subreddit = data["subreddit"]
  postLink = data["postLink"]
  nsfw = data.get("nsfw", False)

  if nsfw and not ctx.channel.is_nsfw():
    await ctx.send("This post is NSFW and can only be sent in an NSFW channel."
                   )
  else:
    em = discord.Embed(title=redditName, color=discord.colour.Color.yellow())
    em.set_image(url=redditURL)
    em.set_footer(
      text=
      f"Created by: {redditPoster}, subreddit: {subreddit}, post: {postLink}")
    await ctx.send(embed=em)


# Moderation commands


# Warn role setup
@client.command()
async def warn_role(ctx, role: discord.Role):
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


# remove warn role setup
@client.command()
async def remove_warn_role(ctx, role: discord.Role):
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


# Warn command
@client.command()
async def warn(ctx, member: discord.Member, *, reason: str):
  if ctx.author.guild_permissions.kick_members:
    user_warns_ref = db.reference(f'/users/{member.id}/warns')
    user_warns = user_warns_ref.get()

    if user_warns:
      warns_count = len(user_warns)
      new_warn_number = warns_count + 1
    else:
      new_warn_number = 1

    warn_data = {"reason": reason, "warned_by": ctx.author.id}
    user_warns_ref.update({f"warn{new_warn_number}": warn_data})

    total_warns = len(user_warns_ref.get() or {})

    embed = discord.Embed(
      title=f"{member} has been warned",
      description=f"Reason: {reason}\nTotal Warns: {total_warns}",
      color=discord.Color.red())
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

    warn_role_threshold_ref = db.reference('/settings/warn_role_threshold')
    warn_role_ref = db.reference('/settings/warn_role')
    second_warn_role_ref = db.reference('/settings/second_warn_role')
    warn_role_id = warn_role_ref.get()
    second_warn_role_id = second_warn_role_ref.get()

    if warn_role_id and second_warn_role_id:
      warn_role_threshold = warn_role_threshold_ref.get() or 3
      if total_warns >= warn_role_threshold:
        try:
          role = ctx.guild.get_role(warn_role_id)
          await member.add_roles(role)
          await ctx.send(
            f"{member.mention} has been given the {role.name} role due to reaching {warn_role_threshold} warns."
          )
          user_warns_ref.delete()

          role_to_remove = ctx.guild.get_role(second_warn_role_id)
          if role_to_remove in member.roles:
            await member.remove_roles(role_to_remove)
            await ctx.send(
              f"{member.mention} has been removed from {role_to_remove.name} role."
            )
        except Exception as e:
          print(f"An error occurred while adding or removing the roles: {e}")
  else:
    await ctx.send("You don't have permissions to warn members.")


# role giver
@client.command()
async def add_role(ctx, role: discord.Role, member: discord.Member):
  await member.add_roles(role)
  await ctx.send(f"{member.mention} has been given the {role.name} role!")


# Log setup
# Log setup
@client.command()
async def log_room(ctx, channel: discord.TextChannel):
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


# Kick
@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, reason: str):
  await member.kick(reason=reason)


# Ban
@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, reason: str):
  await member.ban(reason=reason)
  await ctx.send(f"User {member.mention} has been banned.")


# Clear
@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
  await ctx.channel.purge(limit=amount + 1)
  await ctx.send("Messages deleted.")


client.run('')
