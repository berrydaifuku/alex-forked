import discord
import requests
import asyncio
import collections
import re
import time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from discord.ext import commands

class QandA(commands.Cog):
    scores = collections.defaultdict(int)

    QUESTION_WORD_REGEX = "/^(what is|what are|whats|what's|where is|where are|wheres|where's|who is|who are|whos|who's|when is|when are|whens|when's|why is|why are|whys|why's) /i"
    SIMILARITY_THRESHOLD = 0.85
    QUESTION_ANSWER_TIME = 45

    def __init__(self, client):
        self.client = client

    def HTMLtoMarkdown(self, s):
        s = s.replace('<i>', '*')
        s = s.replace('</i>', '*')
        s = s.replace('<b>', '**')
        s = s.replace('</b>', '**')
        return s

    def isQuestionFormat(self, s):
        return re.search(self.QUESTION_WORD_REGEX, re.sub("/[^\w\s]/i", "", s))

    def isAnswerCorrect(self, answer, correct_answer):
        # strip question words and punctuation 
        answer = re.sub("/[^a-zA-Z0-9 ]/g", "", re.sub(self.QUESTION_WORD_REGEX, "", answer))

        # if there are alternative answers, test for substring
        parentheses_regex = "/\(([^)]+)\)/"
        if (re.search(parentheses_regex, answer)):
            diff_alt = fuzz.partial_ratio(answer, correct_answer)
            if (diff_alt > 0.95):
                return True

        # otherwise calculate diff 
        diff = fuzz.ratio(answer, correct_answer)
        print(f'{correct_answer} = {answer}\n {diff}% match')
        if (diff > self.SIMILARITY_THRESHOLD):
            return True

        return False

    @commands.slash_command(brief="get a question." ,description="get a question, answer within 30 seconds.")
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
        await ctx.respond(embed=embed)

        def check(m):
            m.channel == ctx.channel 
            
        start = time.time()
        while (time.time() - start < self.QUESTION_ANSWER_TIME):
            remaining_time = self.QUESTION_ANSWER_TIME- (time.time - start())
            if (remaining_time > 1):
                try:
                    msg = await self.client.wait_for('message', check=check, timeout=remaining_time)
                except asyncio.TimeoutError:
                    timeout = discord.Embed(title="Time's up!", description=f"We were looking for \"{answer}\"", color=0xff0000)
                    await  ctx.respond(embed=timeout)
                else:
                    if (msg.content.lower() == "skip"):
                        skipped = discord.Embed(title="Skipped", description=f"The ansewr was \"{answer}\"", color=0xff0000)
                        await ctx.respond(embed=skipped)
                        break
                    if self.isQuestionFormat(msg.content):
                        not_question = discord.Embed(title="Not a question!", description="The answer must be formatted as a question", color=0xff0000)
                        await ctx.respond(embed=not_question)
                    elif self.isAnswerCorrect(msg.content, answer):
                        correct = discord.Embed(title="Correct!", description=f"You got it! The answer was \"{answer}\"", color=0x00ff00)
                        await ctx.respond(embed=correct)
                        #await ctx.send('Correct!')
                        self.scores[msg.author] += value
                        break
                    else:
                        incorrect = discord.Embed(title="Incorrect!", description=f"Any other guesses?", color=0xff0000)
                        await ctx.respond(embed=incorrect)
                        #await ctx.send(f"Incorrect.\nThe answer was {answer}")

    @commands.slash_command(description="see your score.")
    async def score(self, ctx):
        embed=discord.Embed(title="your score", color=0x004cff)
        if ctx.author in self.scores:
            embed.add_field(name=ctx.author.name, value=self.scores[ctx.author], inline=False)
        else:
            embed.add_field(name=ctx.author.name, value=0, inline=False)

        await ctx.respond(embed=embed)

    @commands.slash_command(description="see leaderboard.")
    async def leaderboard(self, ctx):
        embed=discord.Embed(title="leaderboard", color=0x004cff)

        num_entries = min(5, len(self.scores))
        i = 0
        for author in sorted(self.scores, key=self.scores.get, reverse=True):
            if (i < num_entries):
                embed.add_field(name=author, value=self.scores[author], inline=False)
            else:
                break
        
        await ctx.respond(embed=embed)

    @commands.slash_command(description="clear leaderboard.") 
    async def clearboard(self, ctx):
        self.scores = collections.defaultdict(int)
        embed = discord.Embed(title="leaderboard cleared", color=0x004cff)
        await ctx.respond(embed=embed)


def setup(client):
    client.add_cog(QandA(client))