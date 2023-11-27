import openai
import os
from dotenv import load_dotenv, find_dotenv
import discord
from discord.ext import commands
from discord import Interaction
import asyncio
from utils import *

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=commands.when_mentioned_or("!helper"), intents=intents)

openai_client = openai
_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.getenv('OPENAI_API_KEY')
bot_token = os.getenv('BOT_TOKEN')
assistant_id = os.getenv('ASST_ID')
assistant = openai_client.beta.assistants.retrieve(assistant_id)


@client.event
async def on_ready():
    await client.tree.sync()
    await client.change_presence(activity=discord.CustomActivity("Helping members!"))
    print(f'{client.user.name} is logged in.')


@client.tree.command(name="w3dhelper", description="Let me know what you need help with!")
async def helper(interaction: Interaction, user_input: str):
    user = interaction.user
    user_id = interaction.user.id
    user_name = interaction.user.name
    await interaction.response.defer()

    response = generate_response(user_input, user_id, user_name)

    if len(response) > 1500:
        messages = split_message(response)
        for i, msg in enumerate(messages):
            await interaction.followup.send(f"Question: {user_input}\n\nAnswer Part {i+1}: {msg}")
    else:
        await interaction.followup.send(f"Question: {user_input}\n\nAnswer: {response}")

client.run(bot_token)
