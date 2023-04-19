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
    question_running = False

    QUESTION_WORD_REGEX = "^(what is|what are|whats|what's|where is|where are|wheres|where's|who is|who are|whos|who's|when is|when are|whens|when's|why is|why are|whys|why's)"
    SIMILARITY_THRESHOLD = 80
    QUESTION_ANSWER_TIME = 30

    def __init__(self, client):
        self.client = client

    def HTMLtoMarkdown(self, s):
        s = s.replace('<i>', '*')
        s = s.replace('</i>', '*')
        s = s.replace('<b>', '**')
        s = s.replace('</b>', '**')
        return s

    def isQuestionFormat(self, s):
        return re.match(self.QUESTION_WORD_REGEX, s, re.IGNORECASE)

    def isAnswerCorrect(self, answer, correct_answer):
        # strip question words and punctuation 
        answer = re.sub("[^a-zA-Z0-9 ]", "", re.sub(self.QUESTION_WORD_REGEX, "", answer, flags=re.IGNORECASE)).lower()
        correct_answer = re.sub("[^a-zA-Z0-9 ]", "", correct_answer).lower()

        # there's a space at the beginning
        answer = answer[1:]
        print(f'stripped answer: {answer}')
        print(f'stripped correct answer: {correct_answer}')

        # if there are alternative answers, test for substring
        # parentheses_regex = "\(([^)]+)\)"

        # otherwise calculate diff 
        diff = fuzz.ratio(answer, correct_answer)
        print(f'{correct_answer} = {answer}\n {diff}% match')
        if (diff > self.SIMILARITY_THRESHOLD):
            return True

        if (diff > 20): 
            diff_substring = fuzz.partial_ratio(answer, correct_answer)
            if (diff_substring > 95):
                return True

        return False

    @commands.slash_command(brief="get a question." ,description="get a question, answer within 30 seconds.")
    async def q(self, ctx):
        if (self.question_running):
            return

        await ctx.defer()
        self.question_running = True
        URL = "http://jservice.io/api/random"
        r = requests.get(url=URL)
        content = r.json()[0]
        while len(content["answer"]) == 0 or len(content["question"]) == 0:
            try:
                r = requests.get(url=URL)
                content = r.json()[0]
            except requests.exceptions.RequestException as e:
                self.question_running = False
                embed = discord.Embed(title="request raised exception", color=0xff0000)
                return
            
        category = content["category"]["title"]
        value = content["value"]
        final_jeopardy = False
        if value is None:
            final_jeopardy = True
        question = self.HTMLtoMarkdown(content["question"])
        answer = self.HTMLtoMarkdown(content["answer"])

        embed=discord.Embed(title=f'{category} for ${value}', description=question, color=0x004cff)
        if (final_jeopardy):
            embed.add_field(name="CAUTION", value="this is a final jeopardy question! getting it correct will double your score, and getting it incorrect will reset your score to 0")
        #embed.add_field(name="Question", value=question, inline=False)

        print(f'Category:{category} for ${value}\nQuestion: {question}\nAnswer: {answer}')
        await ctx.respond(embed=embed)

        def check(m):
            return m.channel == ctx.channel 
            
        start = time.time()
        while (time.time() - start < self.QUESTION_ANSWER_TIME):
            remaining_time = self.QUESTION_ANSWER_TIME- (time.time() - start)
            if (remaining_time > 1):
                try:
                    msg = await self.client.wait_for('message', check=check, timeout=remaining_time)
                except asyncio.TimeoutError:
                    timeout = discord.Embed(title="time's up!", description=f"we were looking for \"{answer}\"", color=0xff0000)
                    await  ctx.respond(embed=timeout)
                else:
                    if (msg.content.lower() == "skip"):
                        skipped = discord.Embed(title="skipped", description=f"the answer was \"{answer}\"", color=0xff0000)
                        await ctx.respond(embed=skipped)
                        self.question_running = False
                        break
                    elif self.isQuestionFormat(msg.content) is None:
                        # not_question = discord.Embed(title="not a question!", description="the answer must be formatted as a question", color=0xff0000)
                        # await ctx.respond(embed=not_question)
                        continue
                    elif self.isAnswerCorrect(msg.content, answer):
                        correct = discord.Embed(title="correct!", description=f"you got it! the answer was \"{answer}\"", color=0x00ff00)
                        await ctx.respond(embed=correct)
                        #await ctx.send('Correct!')
                        self.question_running = False
                        if (final_jeopardy):
                            if (self.scores[msg.author] < 0):
                                self.scores[msg.author] = 0
                            else:
                                self.scores[msg.author] *= 2
                        else:
                            self.scores[msg.author] += value
                        break
                    else:
                        incorrect = discord.Embed(title="incorrect!", description=f"any other guesses?", color=0xff0000)
                        await ctx.respond(embed=incorrect)
                        #await ctx.send(f"Incorrect.\nThe answer was {answer}")
                        self.question_running = False
                        if (final_jeopardy):
                            if self.scores[msg.author] > 0:
                                self.scores[msg.author] = 0
                        else:
                            self.scores[msg.author] -= value

        self.question_running = False

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