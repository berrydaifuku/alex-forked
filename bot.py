import discord
import os
from discord.ext import commands
import logging

logging.basicConfig(level=logging.DEBUG)
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

@client.event
async def on_ready():
    servers = len(client.guilds)
    members = 0
    for guild in client.guilds:
        members += guild.member_count - 1

    await client.change_presence(activity = discord.Activity(
        type = discord.ActivityType.playing,
        name = f'in {servers} servers with {members} contestants'
    ))
    print("Ready!")

@client.command(brief="Load Cog")
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded module {extension}')

@client.command(brief="Unload Cog")
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Unloaded module {extension}')

@client.command(brief="Reload Cog")
@commands.is_owner()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'Reloaded module {extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

TOKEN = os.getenv('TOKEN')

# set testing bot token here
# TOKEN = 'TOKEN'
client.run(TOKEN)
