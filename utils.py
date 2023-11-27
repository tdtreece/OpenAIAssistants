import shelve
import openai
from dotenv import load_dotenv, find_dotenv
import os
import time

openai_client = openai
_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.getenv('OPENAI_API_KEY')
bot_token = os.getenv('BOT_TOKEN')
assistant_id = os.getenv('ASST_ID')
assistant = openai_client.beta.assistants.retrieve(assistant_id)


# ---------------------------------
# Thread Management
# ---------------------------------
def check_if_thread_exists(user_id):
    user_id = str(user_id)
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(user_id, None)


def store_thread(user_id, thread_id):
    user_id = str(user_id)
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[user_id] = thread_id


# ---------------------------------
# Running assistant from OpenAI
# ---------------------------------
def run_assistant(thread):
    # Retrieve the Assistant
    assistant = openai_client.beta.assistants.retrieve(assistant_id)

    # Run the assistant
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Wait for completion
    while run.status != "completed":
        time.sleep(2)
        print(run.status)
        run = openai_client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    return new_message


# ---------------------------------
# Generating responses
# ---------------------------------
def generate_response(message_body, user_id, name):
    # Check if thread exists for user_id
    thread_id = check_if_thread_exists(user_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        print(f"Creating new thread for {name} with user_id {user_id}")
        thread = openai_client.beta.threads.create()
        store_thread(user_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        print(f"Retrieving existing thread for {name} with user_id {user_id}.")
        thread = openai_client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    new_message = run_assistant(thread)
    return new_message
