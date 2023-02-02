import discord
import os
from discord.ext import commands
import logging
from dotenv import load_dotenv

load_dotenv()
#logging.basicConfig(level=logging.DEBUG)
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(intents=intents)

@client.event
async def on_ready():
    servers = len(client.guilds)
    members = 0
    for guild in client.guilds:
        members += guild.member_count - 1

    await client.change_presence(activity = discord.Activity(
        type = discord.ActivityType.playing,
        name = f'with /q! | {servers} servers | {members} members'
    ))
    print("Ready!")
    

@client.slash_command(description="Load Cog")
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.respond(f'Loaded module {extension}')

@client.slash_command(description="Unload Cog")
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.respond(f'Unloaded module {extension}')

@client.slash_command(description="Reload Cog")
@commands.is_owner()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.respond(f'Reloaded module {extension}')

@client.slash_command(description="Update Status")
@commands.is_owner()
async def status(ctx, content = "with /q! | {servers} servers | {members} members"):
    namespace = {'servers': len(client.guilds),
    'members': 0}
    for guild in client.guilds:
        namespace['members'] += guild.member_count - 1
    await client.change_presence(activity = discord.Activity(
        type = discord.ActivityType.playing,
        name = content.format(**namespace)
    ))
    await ctx.respond(f'Updated status to `'+content.format(**namespace)+'`')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

TOKEN = os.getenv('TOKEN')
client.run(TOKEN)
