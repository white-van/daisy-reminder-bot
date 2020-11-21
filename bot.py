import os
import threading
import time
import discord
import asyncio
from dotenv import load_dotenv
import random
import re
from MLP_classifier import NLPSpamDetector

a = NLPSpamDetector()
a.train_test()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

with open('knock-knock.txt') as f:
    jokes = f.readlines()

people_phrases = {}

with open('people-phrases.env') as f:
    for line in f:
        line = line.split('=')
        people_phrases[line[0]] = line[1].strip()


class CustomClient(discord.Client):
    
    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="you :)"))
        self.help_msg = "Send a message with `*task minutes {task-name}` to set a timer"
        self.joke_state = {}


    async def on_message(self, message):
        
        is_troll = a.predict(message)
        if is_troll == "spam":
            await self._is_spam(message)

        if message.content.startswith('*task'):
            await self._task(message)
        
        if message.content.startswith('*help'):
            await message.channel.send(self.help_msg)
        
        if message.content[0] == '*' and \
            re.search(r'^\*knock|who\'?s there?', message.content) \
            or message.content.endswith('who?') \
            or message.content.endswith('who'):
            await self._joke(message)
        
        else:
            await self._misc(message)

    async def _is_spam(self, message):
        await message.channel.send("DO NOT TROLL")

    async def _misc(self, message):
        if message.author == self.user:
            return 

        for k in people_phrases:
            if k in message.content.lower().split():
                await message.channel.send(people_phrases[k])



    async def _joke(self, message):

        # knock knock
        if message.content.startswith("*knock") or \
            self.joke_state.get(message.author, [0])[0] == 0:
            joke = random.choice(jokes).split(' | ')
            self.joke_state[message.author] = [1] + joke
            await message.channel.send("Knock knock")

        # who's there
        elif "who's there" in message.content and self.joke_state.get(message.author, [0])[0] == 1:
            joke_pre = self.joke_state[message.author][1]
            self.joke_state[message.author][0] = 2
            await message.channel.send(joke_pre)
        
        elif message.content[1:].lower().replace('?', '') == \
            self.joke_state[message.author][1].lower() + " who":
            joke_end = self.joke_state[message.author][2]
            self.joke_state[message.author][0] = 0
            await message.channel.send(joke_end)
        
        elif self.joke_state.get(message.author, [0])[0] == 2:
            joke_pre = self.joke_state[message.author][1]
            msg = 'You\'re supposed to ask `{} who?`'.format(joke_pre)
            await message.channel.send(msg)
        else:
            msg = "hmm, can you start over with `*knock`? I forgot the joke... oopsie daisy"
            await message.channel.send(msg)
    
    async def _task(self, message):
        msg = message.content.split()
        if len(msg) < 3 or not msg[1].replace(".", "").isdecimal():
            await message.channel.send(self.help_msg)
        else: 
            response = "Ok, {}! I will check on you in {} minutes :)".format(message.author.mention, msg[1])
            await message.channel.send(response)
            seconds = float(msg[1]) * 60
            await asyncio.sleep(seconds)
            await self.remind(message, ' '.join(msg[2:]), msg[1])

    async def remind(self, message, task, mins):
         # check if user completed task:
        if message.reactions and message.reactions[0].emoji == '✅':
            await message.channel.send("Good job on completing the task, {}!".format(message.author.mention))
        # user didn't complete task
        else:
            await message.channel.send("Hey {}, it's been {} minutes. Did you make progress on {}?".format(message.author.mention, mins, task))

client = CustomClient()
client.run(TOKEN)
