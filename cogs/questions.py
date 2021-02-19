import discord
import requests
import asyncio
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from discord.ext import commands

class QandA(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def q(self, ctx):
        URL = "http://jservice.io/api/random"
        r = requests.get(url=URL)
        content = r.json()[0]
        category = content["category"]["title"]
        value = content["value"]
        question = content["question"]
        answer = content["answer"]

        embed=discord.Embed(title=f'{category} for ${value}', description=question, color=0x004cff)
        #embed.add_field(name="Question", value=question, inline=False)

        print(f'Question: {question}\nAnswer: {answer}')
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel 
            

        try:
            msg = await self.client.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send("Sorry! Time's up!")
        else:
            diff = fuzz.WRatio(msg.content, answer)
            print(f'{msg.content} = {answer}\n {diff}% match')
            if diff > 70:
                await ctx.send('Correct!')
            else:
                await ctx.send("Incorrect.")


def setup(client):
    client.add_cog(QandA(client))