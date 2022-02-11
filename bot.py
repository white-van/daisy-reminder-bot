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



PEN_PALS = False
ANON_COMPLIMENT = True

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


if PEN_PALS:
    with open('pairs.txt') as f:
        pairs = {}
        for line in f:
            line = line.split(',')[:2]
            line = [int(x) for x in line]
            if(len(line) > 4):
                for i in range(3):
                    pairs[int(line[i])] = line[:i] + line[i + 1:4]
            else:
                pairs[line[0]] = line[1]
                pairs[line[1]] = line[0]

if ANON_COMPLIMENT:
    with open('names.txt') as f:
        people = {}
        for line in f:
            line = line.split(',')
            people[line[0]] = line[1]
    
    with open('banned_names.txt') as f:
        banned = []
        for line in f:
            banned.append(line.strip())
    
    with open('comp_log.txt') as f:
        num_compliments = len(f.readlines())

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

        if message.author.bot:
            return 

        if isinstance(message.channel, discord.channel.DMChannel):
            if PEN_PALS:
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
            
            elif ANON_COMPLIMENT:
                if message.content.startswith('!help'):
                    await self._help_compliments(message)
                    return
                if message.content.startswith('!add') and message.author.id == 414980016435232778:
                    await self._add_user(message)
                    return
                if message.content.startswith('!ban') and message.author.id == 414980016435232778:
                    await self._ban_user(message)
                    return
                if message.content.startswith('!reply'):
                    await self._send_comp_reply(message)
                    return
                await self._send_compliment(message)


            

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

    async def _help_compliments(self, message):
        help_command = open('help-compliments.txt').read()
        embed = discord.Embed(
            title="Daisy Help Centre",
            colour=discord.Colour(0xEB3D34),
            description=help_command,
            author="Blossom the Bully"
        )
        await message.channel.send(embed=embed)

    async def _add_user(self, message):
        user = message.content.replace('!add', '').strip()
        name, user_id = user.split(',')
        people[name] = user_id
        with open('names.txt', 'a') as f:
            f.write(f'{name},{user_id}\n')
            await message.channel.send('Added, Blossom.')    


    async def _ban_user(self, message):
        user = message.content.replace('!ban', '').strip()
        banned.append(user)
        with open('banned_names.txt', 'a') as f:
            f.write(f'{user}\n')
            await message.channel.send('Donezo, Blossom.')
    
    async def _send_comp_reply(self, message):
        if str(message.author.id) in banned:
            await message.channel.send('You\'ve been banned from using this service.')
            return

        # find last person who messaged this person
        user_id = message.author.id
        content = ' '.join(message.content.split(' ')[2:])
        num = message.content.split(' ')[1]
        reply_id = None
        with open('comp_log.txt') as f:
            for line in f:
                line = line.strip().split(',')
                # find reply num in messages sent to person
                if int(line[1]) == user_id and line[0] == num:
                    reply_id = int(line[2])
        if reply_id is None:
            await message.channel.send('Sorry, I couldn\'t find who sent the message to you.\n\n'+
                                       'Use !help to check the formatting syntax!')
        else:
            person = self.get_user(reply_id)
            if not person:
                try:
                    person = await self.fetch_user(reply_id)
                except:
                    print(f'Couldn\'t find {person}')
                    return
            embed = discord.Embed(
            title=f"{message.author.name} 🌸",
            colour=discord.Colour(0xEB3D34),
            description=content,
            author=f'Anon. Mystery'
        )
            await person.send(embed=embed)
            await message.add_reaction("<:pandaLove:649484391801815050>")
        

    async def _send_compliment(self, message):
        global num_compliments
        if str(message.author.id) in banned:
            await message.channel.send('You\'ve been banned from using this service.')
            return

        message_lst = message.content.split(' ')
        if len(message_lst) <= 1:
            print(f'Unable to send message')
            return
        person = message_lst[0]
        person_id = people.get(person, None)
        if person_id:
            partner = self.get_user(person_id)
            if not partner:
                try:
                    partner = await self.fetch_user(person_id)
                except:
                    print(f'Couldn\'t find {person}')
                    return
            embed = discord.Embed(
            title="Anon. Complimenter 🌸",
            colour=discord.Colour(0xEB3D34),
            description=' '.join(message_lst[1:]) + f'\n\n#{num_compliments}',
            author=f'Anon. Mystery'
        )
            await partner.send(embed=embed)
            await message.add_reaction("<:pandaLove:649484391801815050>")
            with open('comp_log.txt', 'a') as f:
                f.write(f'{num_compliments},{partner.id},{message.author.id}\n')
                num_compliments += 1



        else:
            await message.channel.send(f'Sending the message failed. Either user {person} did not ' + 
                                f'consent to get messages, or your message is formatted incorrectly.'+
                                'Use !help to check the formatting syntax!')
    
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
        if (len(potential_primes) != 0 and any(is_prime(int(potential_prime)) for potential_prime in potential_primes)):
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
client.run(TOKEN)
