import discord
import os
import deepl
import json
from discord.ext import commands
from dotenv import load_dotenv
from lingua import LanguageDetectorBuilder
import pymongo
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

from .authenticate import auth_apikey
from .languages import basic_languages, lingua_languages

detector = LanguageDetectorBuilder.from_languages(*lingua_languages).build()

load_dotenv()
#deepl credentials
DEEPL_AUTH = os.getenv('DEEPL_AUTH')

#mongodb credentials
MONGO_URI = os.getenv('MONGO_URI')

#google translate credentials
GOOGLE_AUTH = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
GOOGLE_AUTH['private_key'] = GOOGLE_AUTH['private_key'].replace('\\n', '\n')
CREDENTIALS = service_account.Credentials.from_service_account_info(GOOGLE_AUTH)
gtranslate_client = translate.Client(credentials=CREDENTIALS)

mongodb_client = pymongo.MongoClient(MONGO_URI)

db = mongodb_client["translatordb"]
col = db["api_keys"]

class Translate(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):

        print('TranslatorCog loaded')

    @commands.Cog.listener()
    async def on_message(self, message):
        #prevent bot from replying to self
        if message.author == self.client.user:
            return

        if message.author.bot:
            return

        server_id = message.guild.id

        #authenticate server
        if auth_apikey(server_id) == False:
            return

        #take users information to display in embedded message
        user_message = str(message.content)

        #ignore commands
        if user_message[0] == '.':
            return

        #ignore emojis
        if user_message[0] == ':':
            return

        #ignore custom emojis
        if user_message[0] == '<':
            return

        #ignore urls
        if user_message[:4] == 'http':
            return

        channel = message.channel
        server_key = {'server_id': server_id}
        lang = col.find_one(server_key)
        server_sub = col.find_one(server_key)
        server_credits = server_sub['credits']
        server_lang = lang['target_lang']

        if 'Translate' in str(message.author.roles):

            lingua_result = detector.detect_language_of(user_message)
            #hard coded target language, need to move to variable
            lingua_lang = lingua_result.name
            print(lingua_lang)

            if lingua_lang.lower() == server_lang.lower():
                return

            len_chars = len(user_message)
            if lingua_lang.lower() not in basic_languages:
                google_target_lang = basic_languages[server_lang]

                if server_lang == 'english':
                    google_target_lang = 'en'

                credit_result = col.update_one(server_key, {'$inc': {'credits': -1*len_chars}})
                #enter code for google translate
                result = gtranslate_client.translate(user_message, target_language=google_target_lang.lower())
                google_detected_lang = result['detectedSourceLanguage']

                #if google doesnt find a translation, return
                if str(user_message) == google_result:
                    print(f"No translation found. ---- {result}")
                    return
                #if translating - start typing
                await channel.typing()
                #refactor this into a function
                embed=discord.Embed(description=google_result)
                #displays user avatar
                embed.set_author(name=message.author.display_name, icon_url=message.author.avatar)
                await message.channel.send(embed=embed)
                return


            #increment counter
            credit_result = col.update_one(server_key, {'$inc': {'credits': -1*len_chars}})

            translator = deepl.Translator(DEEPL_AUTH)
            #translate message into target language
            result = translator.translate_text(user_message, target_lang=basic_languages[server_lang])
            #if translation results in same message
            if str(user_message) == str(result):
                print(f"No translation found. ---- {result}")
                return
            #if translating - start typing
            await channel.typing()
            #embedded message with op name and avatar
            #--# TODO: Custom color based on Language? Channel?
            embed=discord.Embed(description=result)
            #displays user avatar
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar)
            await message.channel.send(embed=embed)
            return


    @commands.command()
    async def trstats(self, ctx):
        server_key = {'server_id': ctx.guild.id}
        lang = col.find_one(server_key)
        result = lang['target_lang']
        server_credits = col.find_one(server_key)
        current_credits = server_credits['credits']
        await ctx.send(f'Current target language: {result.upper()} Credits: {current_credits}')

async def setup(client):
    await client.add_cog(Translate(client))
