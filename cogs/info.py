import discord
from discord.ext import commands

class Info(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("pong!")

    @commands.slash_command()#guild_ids=[927705353850851408])
    async def status(self, ctx):
        servers = len(self.client.guilds)
        members = 0
        for guild in self.client.guilds:
            members += guild.member_count - 1
        embed = discord.Embed(
            title="Status",
            color=discord.Color.blue()
        )
        embed.add_field(name="Servers", value=servers, inline=True)
        embed.add_field(name="Contestants", value=members, inline=True)

        await ctx.respond(embed=embed)

def setup(client):
    client.add_cog(Info(client))