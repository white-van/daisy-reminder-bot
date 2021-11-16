import os
import threading
import time
import discord
import math
import asyncio
from dotenv import load_dotenv
import random
import aiocron
import re

### For Dialogflow ###
import dialogflow
from google.api_core.exceptions import InvalidArgument


load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private.json'
TOKEN = os.getenv('DISCORD_TOKEN')
DIALOGFLOW_PROJECT_ID = os.getenv('DIALOGFLOW_PROJECT_ID')
DIALOGFLOW_LANGUAGE_CODE = os.getenv('DIALOGFLOW_LANGUAGE_CODE')
SESSION_ID = os.getenv('SESSION_ID')
PRIME_NUMBER_CAP = os.getenv('PRIME_NUMBER_CAP')

client = discord.Client()
with open('knock-knock.txt') as f:
    jokes = f.readlines()

with open('help-commands.txt') as f:
    help_command = f.read()

with open('pairs.txt') as f:
    pairs = {}
    for line in f:
        line = line.split(', ')
        pairs[int(line[0])] = int(line[1])
        pairs[int(line[1])] = int(line[0])

people_phrases = {}

with open('people-phrases.env') as f:
    for line in f:
        line = line.split('=')
        people_phrases[line[0]] = [line[1].strip(), 0]

cooldown = 3

def is_prime(n):
    if (n % 2 == 0 and n > 2) or n > int(PRIME_NUMBER_CAP):
        return False
    return all(n % i for i in range(3, int(math.sqrt(n)) + 1, 2))
class CustomClient(discord.Client):

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="you :)"))
        self.help_msg = "Send a message with `*task minutes {task-name}` to set a timer"
        self.joke_state = {}
        self.server_map = {}
        for server in self.guilds:
            if server.name == "UTM White Van":
                self.server_map["WV"] = server


    async def on_message(self, message):

        if isinstance(message.channel, discord.channel.DMChannel):
            partner_id = pairs.get(message.author.id, None)
            if partner_id:
                partner = self.get_user(partner_id)
                if not partner:
                    try:
                        partner = await self.fetch_user(partner_id)
                    except:
                        return
                await partner.send(message.content)
                await message.add_reaction("<:pandaLove:649484391801815050>")

        elif message.channel.id == 515333729812742155:
            await message.add_reaction("<:pandaLove:649484391801815050>")


        elif message.author.bot:
            return

        elif message.content.startswith("*help"):
            await self._help(message)

        elif message.content.startswith("*clean"):
            await self._delete_messages(message)

        elif message.content.startswith('*task'):
            await self._task(message)

        elif message.content.startswith('*talk'):
            await self._dialog_response(message)

        elif message.content and message.content[0] == '*' and \
                re.search(r'^\*knock|who.?s there\??', message.content) \
                or message.content.endswith('who?') \
                or message.content.endswith('who'):
            await self._joke(message)

        else:
            await self._misc(message)

    async def _dialog_response(self, message):
        text_to_be_analyzed = message.content
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
        text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.types.QueryInput(text=text_input)
        try:
            response = session_client.detect_intent(session=session, query_input=query_input)
        except InvalidArgument:
            print("intent error")
            return
        response_text = response.query_result.fulfillment_text
        if response_text:
            await message.channel.send(response_text)

    async def _help(self, message):
        embed = discord.Embed(
            title="Daisy Help Centre",
            colour=discord.Colour(0xEB3D34),
            description=help_command,
            author="Blossom the Bully"
        )
        await message.channel.send(embed=embed)

    async def _delete_messages(self, message):
        def is_me(m):
            return m.author == self.user
        deleted = await message.channel.purge(limit=20, check=is_me)
        await message.channel.send('Deleted {} message(s)'.format(len(deleted)), delete_after=3)
        await message.delete(delay=3)

    async def _misc(self, message):
        if message.author == self.user:
            return

        for k in people_phrases:
            if k in message.content.lower().split():
                # hasn't been mentioned since cooldown period
                if not people_phrases[k][1]:
                    await message.channel.send(people_phrases[k][0])
                people_phrases[k][1] = (people_phrases[k][1] + 1) % cooldown

        #check if text has prime
        potential_primes = re.findall(r"\d+", message.content)
        if (len(potential_primes) != 0 and any(is_prime(int(potential_primes)) for potential_prime in potential_primes)):
            await message.add_reaction("\N{REGIONAL INDICATOR SYMBOL LETTER P}")
            await message.add_reaction("\N{REGIONAL INDICATOR SYMBOL LETTER R}")
            await message.add_reaction("\N{REGIONAL INDICATOR SYMBOL LETTER I}")
            await message.add_reaction("\N{REGIONAL INDICATOR SYMBOL LETTER M}")
            await message.add_reaction("\N{REGIONAL INDICATOR SYMBOL LETTER E}")



    async def _joke(self, message):

        # knock knock
        if message.content.startswith("*knock") or \
                self.joke_state.get(message.author, [0])[0] == 0:
            joke = random.choice(jokes).split(' | ')
            self.joke_state[message.author] = [1] + joke
            await message.channel.send("Knock knock")

        # who's there
        elif re.search(r'who.?s there\??', message.content) and self.joke_state.get(message.author, [0])[0] == 1:
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

    def _incorrectly_formatted_time(self, time):
        return not (re.search("^\d+h([0-5]\d|\d)min$", time.replace(".", "")) or time.replace(".", "").isdecimal())

    async def _task(self, message):
        msg = message.content.split()
        using_hrs_format = None
        if len(msg) < 3 or self._incorrectly_formatted_time(msg[1]):
            await message.channel.send(self.help_msg)
        else:
            response = ""
            seconds = None;
            hours = "0"
            mins = ""
            if msg[1].replace(".", "").isdecimal():
                response = "Ok, {}! I will check on you in {} minutes :)".format(message.author.mention, msg[1])
                mins = msg[1]
                self._using_hrs_format = False
            else:
                hours = msg[1][:msg[1].find("h")]
                mins = msg[1][msg[1].find("h") +  1:msg[1].find("min")]
                response = "Ok, {}! I will check on you in {} {} and {} {} :)".format(message.author.mention, hours[:-1].lstrip("0") + hours[-1], "hour" if hours == "1" else "hours", mins[:-1].lstrip("0") + mins[-1], "minute" if mins == "1" else "minutes")
                using_hrs_format = True
            seconds = (float(hours) * 60 + float(mins)) * 60
            await message.channel.send(response)
            await asyncio.sleep(seconds)
            await self.remind(message, ' '.join(msg[2:]), hours, mins, using_hrs_format)

    async def remind(self, message, task, hours, mins, using_hrs_format):
        # check if user completed task:
        if message.reactions and message.reactions[0].emoji == '✅':
            await message.channel.send("Good job on completing the task, {}!".format(message.author))
        # user didn't complete task
        elif message.reactions and message.reactions[0].emoji == '❎':
            return
        elif using_hrs_format:
            await message.channel.send("Hey {}, it's been {} {} and {} {}. Did you make progress on {}?".format(message.author.mention, hours[:-1].lstrip("0") + hours[-1], "hour" if hours == "1" else "hours", mins[:-1].lstrip("0") + mins[-1], "minute" if mins == "1" else "minutes", task))
        else:
            await message.channel.send("Hey {}, it's been {} minutes. Did you make progress on {}?".format(message.author.mention, mins, task))

    async def get_messages(self):
        server = self.server_map['WV']
        channel = server.get_channel(514951629817118732)
        counter = 0
        user_messages = {}
        async for message in channel.history(limit=100000):
            user_messages.setdefault(message.author.mention, []).append(message.content)

        with open('messages.txt', 'w') as f:
            for k, v in user_messages.items():
                f.write('{}: {}\n\n\n'.format(k, '\n'.join(v)))


client = CustomClient()
# every 4 hours get messages
""" @aiocron.crontab('0 */24 * * *')
async def get_messages():
    await client.get_messages() """
client.run(TOKEN)

