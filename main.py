import openai
import os
from dotenv import load_dotenv, find_dotenv
import discord
from discord.ext import commands
from discord import Interaction
import asyncio

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


@client.tree.command(name="ping_web", description="Shows current latency of bot responses.")
async def ping(interaction: Interaction):
    bot_latency = (client.latency*1000)
    await interaction.response.send_message(f"Pong!...{int(bot_latency)}ms")


@client.tree.command(name="w3dhelper", description="Let me know what you need help with!")
async def helper(interaction: Interaction, user_input: str):
    user_id = interaction.user.id
    await interaction.response.defer()

    thread = openai_client.beta.threads.create()
    message = openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=user_input
    )

    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    while run.status != "completed":
        await asyncio.sleep(2)
        print(run.status)
        run = openai_client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    print("Run completed!")
    messages = openai_client.beta.threads.messages.list(
        thread_id=thread.id
    )

    assistant_response = messages.data[0].content[0].text.value
    await interaction.followup.send(f"{assistant_response} \n {user_id}")

client.run(bot_token)
