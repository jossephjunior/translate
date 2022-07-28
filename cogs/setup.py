import discord
from discord.ext import commands
import pymongo
from dotenv import load_dotenv
import os
import time
import asyncio

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
mongodb_client = pymongo.MongoClient(MONGO_URI)
db = mongodb_client["translatordb"]
col = db["api_keys"]

#select menu for choosing a target language
class SelectLanguage(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="english", emoji="🇺🇸", description="english"),
            discord.SelectOption(label="spanish", emoji="🇪🇸", description="spanish"),
            discord.SelectOption(label="french", emoji="🇫🇷", description="french"),
            discord.SelectOption(label="bulgarian", emoji="🇧🇬", description="bulgarian"),
            discord.SelectOption(label="czech", emoji="🇨🇿", description="czech"),
            discord.SelectOption(label="danish", emoji="🇩🇰", description="danish"),
            discord.SelectOption(label="german", emoji="🇩🇪", description="german"),
            discord.SelectOption(label="greek", emoji="🇬🇷", description="greek"),
            discord.SelectOption(label="estonian", emoji="🇪🇪", description="estonian"),
            discord.SelectOption(label="finnish", emoji="🇫🇮", description="finnish"),
            discord.SelectOption(label="hungarian", emoji="🇭🇺", description="hungarian"),
            discord.SelectOption(label="indonesian", emoji="🇮🇩", description="indonesian"),
            discord.SelectOption(label="italian", emoji="🇮🇹", description="italian"),
            discord.SelectOption(label="japanese", emoji="🇯🇵", description="japanese"),

        ]
        super().__init__(placeholder="Languages",
            max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        #get server id to store specific target languages for multiple servers
        chosen_lang = self.values[0]
        user_id = interaction.user.id
        user_choice =  {"lang": chosen_lang}


        server_id = interaction.guild.id
        specs = {
            "server_id" : server_id,
            "target_lang" : chosen_lang,
        }

        server_key = {"server_id" : server_id}
        #update server info
        result = col.update_one(server_key, {'$set':specs}, True)
        result = col.update_one(server_key, {'$set': {f"user_langs.{user_id}": user_choice}}, True)


        ## retrieve a user's lang
        user_lang = col.find_one(server_key)
        user_lang = user_lang['user_langs'][f'{user_id}']['lang']

        await interaction.response.send_message(content=f"Your choice is {chosen_lang}", ephemeral=True)
        self.stop()

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 10):
        super().__init__(timeout=timeout)
        self.add_item(SelectLanguage())

class Setup(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        #need to implement setup that lets users configure target lang
        #select = Select()

        #load initial settings here
        #########
        print('SetupCog loaded')

    @commands.command()
    #@commands.has_permissions(administrator = True)
    async def trconfig(self, ctx, *args):
        #get user id
        argCount = len(args)
        if argCount > 0:
            for arg in args:
                #need to check if valid user
                user = int(arg[2:-1])
                user_object = ctx.guild.get_member(int(user))
                print(user)
                print(ctx.guild.members)
                print(user_object)
        #send select menu to user
        select_view = SelectView()
        msg = await ctx.send("Select what language you would like to translate text to: \nThis message will delete in 10 seconds.", view=select_view, delete_after=10)

async def setup(client):
    await client.add_cog(Setup(client))
