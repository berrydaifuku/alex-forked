import discord
from discord.ext import commands

class Info(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.slash_command(description="Pong!")
    async def ping(self, ctx):
        await ctx.send("pong!")

    @commands.slash_command(description="See # of servers and # of users.")
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