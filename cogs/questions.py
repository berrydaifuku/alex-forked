import discord
import requests
import asyncio
import collections
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from discord.ext import commands

class QandA(commands.Cog):
    scores = collections.defaultdict(int)

    def __init__(self, client):
        self.client = client

    def HTMLtoMarkdown(s):
        s = s.replace('<i>', '*')
        s = s.replace('</i>', '*')
        s = s.replace('<b>', '**')
        s = s.replace('</b>', '**')
        return s

    @commands.command(brief="Get a question." ,description="Get a question. Answer within 30 seconds.")
    async def q(self, ctx):
        URL = "http://jservice.io/api/random"
        r = requests.get(url=URL)
        content = r.json()[0]
        while len(content["answer"]) == 0 or len(content["question"]) == 0:
            r = requests.get(url=URL)
            content = r.json()[0]
            
        category = content["category"]["title"]
        value = content["value"]
        question = self.HTMLtoMarkdown(content["question"])
        answer = self.HTMLtoMarkdown(content["answer"])

        embed=discord.Embed(title=f'{category} for ${value}', description=question, color=0x004cff)
        #embed.add_field(name="Question", value=question, inline=False)

        print(f'Category:{category} for ${value}\nQuestion: {question}\nAnswer: {answer}')
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel 
            

        try:
            msg = await self.client.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            timeout = discord.Embed(title="Time's up!", description=f"We were looking for \"{answer}\"", color=0xff0000)
            await  ctx.send(embed=timeout)
            #await ctx.send(f"Sorry! Time's up!\nThe answer was \"{answer}\"")
        else:
            diff = fuzz.WRatio(msg.content, answer)
            print(f'{msg.content} = {answer}\n {diff}% match')
            if diff > 70:
                correct = discord.Embed(title="Correct!", description=f"You got it! The answer was \"{answer}\"", color=0x00ff00)
                await ctx.send(embed=correct)
                #await ctx.send('Correct!')
                self.scores[msg.author] += value
            else:
                incorrect = discord.Embed(title="Incorrect!", description=f"We were looking for \"{answer}\"", color=0xff0000)
                await ctx.send(embed=incorrect)
                #await ctx.send(f"Incorrect.\nThe answer was {answer}")

    @commands.command()
    async def score(self, ctx):
        print(self.scores)
        #create scoreboard embed
        embed=discord.Embed(title="Scoreboard", color=0x004cff)
        for key, value in self.scores.items():
            embed.add_field(name=key.name, value=value, inline=False)
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(QandA(client))