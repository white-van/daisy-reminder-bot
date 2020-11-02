import os
import threading
import time
import discord
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = discord.Client()




class CustomClient(discord.Client):
    
    async def on_ready(self):
        for guild in client.guilds:
            if guild.name == GUILD:
                break

        self.client = guild

    async def on_message(self, message):
        help_msg = "Send a message with `*task seconds {task-name}` to set a timer"

        if message.content.startswith('*task'):
            msg = message.content.split()
            if len(msg) < 3 or not msg[1].isdigit():
                await message.channel.send(help_msg)
            else: 
                await message.channel.send('Timer set')
                seconds = int(msg[1])
                await asyncio.sleep(seconds)
                await self.remind(message, msg[2])
        
        if message.content.startswith('*help'):
            await message.channel.send(help_msg)

    async def remind(self, message, task):
        # check if user completed task:
        channel = self.client.get_channel(453417214591238166)
        curr_message = await channel.fetch_message(message.id)
        if curr_message.reactions and curr_message.reactions[0].emoji == '✅':
            await channel.send("Good job on completing the task, {}!".format(message.author.mention))
        else:
            await channel.send("Hey {}, it's been 2 hours. Did you make progress on {}?".format(message.author.mention, task))

client = CustomClient()
client.run(TOKEN)