import os
import threading
import time
import discord
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()




class CustomClient(discord.Client):
    
    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="you :)"))

    async def on_message(self, message):
        help_msg = "Send a message with `*task minutes {task-name}` to set a timer"

        if message.content.startswith('*task'):
            msg = message.content.split()
            if len(msg) < 3 or not msg[1].replace(".", "").isdecimal():
                await message.channel.send(help_msg)
            else: 
                response = "Ok, {}! I will check on you in {} minutes :)".format(message.author.mention, msg[1])
                await message.channel.send(response)
                seconds = float(msg[1]) * 60
                await asyncio.sleep(seconds)
                await self.remind(message, msg[2], msg[1])
        
        if message.content.startswith('*help'):
            await message.channel.send(help_msg)

    async def remind(self, message, task, mins):
        server = message.channel.guild
        if server.name == "UTM White Van":
            channel = server.get_channel(760858471817150464)

        elif server.name == "WV Girls":
            channel = server.get_channel(758718542740455476)

        # personal    
        else: 
            channel = server.get_channel(453417214591238166)


        curr_message = message # await channel.fetch_message(message.id)

         # check if user completed task:
        if curr_message.reactions and curr_message.reactions[0].emoji == '✅':
            await channel.send("Good job on completing the task, {}!".format(message.author.mention))
        # user didn't complete task
        else:
            await channel.send("Hey {}, it's been {} minutes. Did you make progress on {}?".format(message.author.mention, mins, task))

client = CustomClient()
client.run(TOKEN)