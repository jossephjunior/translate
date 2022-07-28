import discord
import asyncio
import pymongo
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
MONGO_URI = os.getenv('MONGO_URI')

intents = discord.Intents.default()
intents.message_content = True

#start discord client
client = commands.Bot(command_prefix = '.', intents=intents)

#start mongodb client
mongodb_client = pymongo.MongoClient(MONGO_URI)

@client.event
async def on_ready():
    print('Bot is online')

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with client:
        await load()
        await client.start(TOKEN)

asyncio.run(main())
