import time
import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values, set_key
from enum import Enum
import re
import asyncio
from telethon.sync import TelegramClient, events
from collections import deque
from datetime import datetime
from telethon.tl.types import (Message, PeerChannel, MessageReplyHeader, 
                               MessageMediaPhoto, Photo, PhotoStrippedSize, 
                               PhotoSize, PhotoSizeProgressive, MessageEntityCustomEmoji, 
                               MessageEntityBold, MessageEntityCashtag, MessageEntityTextUrl)

# Define the required fields and their default values
required_fields = {
    'DESTINATION_CHAT_ID': '',
    'SOURCE_CHAT_ID': '',
    'NUMBER_OF_MESSAGES_TO_TRACK': '10',
    'KEYWORDS': '',
}

CONFIG_FOLDER = 'config'
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'config.txt')

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient(os.path.join(CONFIG_FOLDER, 'session_' + phone_number), api_id, api_hash)

    async def list_chats(self):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        # Get a list of all the dialogs (chats)
        dialogs = await self.client.get_dialogs()
        chats_file = open(str(os.path.join(CONFIG_FOLDER,f"chats_of_{self.phone_number}.txt")), "w", encoding="utf-8")
        # Print information about each chat
        for dialog in dialogs:
            print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
            chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")
          
        print("List of groups printed successfully!")

    async def forward_messages_to_channel(self, number_of_messages_to_track, source_chat_id, destination_channel_id, keywords):

        async def convert_msg_id(self, source_message_id, message_pairs):
        
            for source_message, dest_message in list(message_pairs):
                if source_message.id == source_message_id:
                    return dest_message.id
        
            return None
        
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        message_pairs = deque(maxlen=number_of_messages_to_track)

        @self.client.on(events.NewMessage([source_chat_id]))
        async def newMessage(event):

            message = event.message

            if type(message) != Message:
                return

            print("New Message")

            if message.media:
                print(" Media")
                if message.reply_to and (converted_msg_id := await convert_msg_id(self, message.reply_to.reply_to_msg_id, message_pairs)):
                    print("  Reply")
                    forwarded_message = await self.client.send_file(destination_channel_id, message.media, caption=message.text, reply_to=converted_msg_id)
                elif not message.reply_to:
                    print("  No Reply")
                    forwarded_message = await self.client.send_file(destination_channel_id, message.media, caption=message.text)
            else:
                print(" No Media")
                if message.reply_to and (converted_msg_id := await convert_msg_id(self, message.reply_to.reply_to_msg_id, message_pairs)):
                    print("  Reply")
                    forwarded_message = await self.client.send_message(destination_channel_id, message.text, reply_to=converted_msg_id)
                elif not message.reply_to:
                    print("  No Reply")
                    forwarded_message = await self.client.send_message(destination_channel_id, message.text)
        
            if forwarded_message is not None:
                message_pairs.append((message, forwarded_message))

        @self.client.on(events.MessageDeleted([source_chat_id]))
        async def deleteMessage(event):

            
            message = event.message

            if type(message) != Message:
                return

            print("Delete Message")

            for source_message, dest_message in list(message_pairs):
                if source_message.id == message.id:
                    await self.client.delete_messages(destination_channel_id, dest_message.id)
                    message_pairs.remove((source_message, dest_message))
                    return

        @self.client.on(events.MessageEdited([source_chat_id]))
        async def editMessage(event):

            message = event.message
            
            if type(message) != Message:
                return
            
            print("Edit Message")

            for source_message, dest_message in list(message_pairs):
                if source_message.id == message.id:
                    if dest_message.text != message.text:
                        await self.client.edit_message(destination_channel_id, dest_message.id, message.text)
                        message_pairs.remove((source_message, dest_message))
                        message_pairs.append((message, dest_message))
                    return

        await self.client.run_until_disconnected()


# Function to read credentials from .env file
def read_credentials():
    try:
        load_dotenv(Path(os.path.join(CONFIG_FOLDER, ".env")))
        api_id = os.getenv('API_ID')
        api_hash = os.getenv('API_HASH')
        phone_number = os.getenv('PHONE_NUMBER')
        return api_id, api_hash, phone_number
    except Exception as e:
        print("Error reading .env file:", str(e))
        return None, None, None
    
# Function to write credentials to .env file
def write_credentials(api_id, api_hash, phone_number):
    env_file_path = Path(os.path.join(CONFIG_FOLDER, ".env"))
    env_file_path.touch(mode=0o600, exist_ok=False)
    set_key(dotenv_path=env_file_path, key_to_set="API_ID", value_to_set=api_id)
    set_key(dotenv_path=env_file_path, key_to_set="API_HASH", value_to_set=api_hash)
    set_key(dotenv_path=env_file_path, key_to_set="PHONE_NUMBER", value_to_set=phone_number)

def read_config():
    config = {}
    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            key, value = line.strip().split('=', 1)
            config[key] = value
    return config

def write_config(config):
    with open(CONFIG_FILE, 'w') as f:
        for key, value in config.items():
            f.write(f'{key}={value}\n')

def validate_config(config):
    for key in required_fields:
        if key not in config:
            return False
    return True

def setup_config():
    config = {}
    for key in required_fields:
        value = input(f'Enter value for {key} (default: {required_fields[key]}): ') or required_fields[key]
        config[key] = value
    write_config(config)
    return config

async def main():

    # Create config folder if it doesn't exist
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    # Attempt to read credentials from .env file
    api_id, api_hash, phone_number = read_credentials()

    # If credentials not found in .env file, prompt the user to input them
    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")
        # Write credentials to .env file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    print("Choose an option:")
    print("1. List Chats")
    print("2. Forward Messages")
    print("3. Exit")
    
    choice = input("Enter your choice: ")
    
    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
            # Check if config file exists
            if not os.path.exists(CONFIG_FILE):
                print(f'{CONFIG_FILE} not found. Creating a new one...')
                config = setup_config()
            else:
                config = read_config()
                if not validate_config(config):
                    print(f'{CONFIG_FILE} is missing required fields. Recreating...')
                    config = setup_config()

            # Extract variables
            destination_channel_id = int(config['DESTINATION_CHAT_ID'])
            source_chat_id = int(config['SOURCE_CHAT_ID'])
            number_of_messages_to_track = int(config['NUMBER_OF_MESSAGES_TO_TRACK'])
            keywords = config['KEYWORDS'].split(',') if config['KEYWORDS'] else []

            await forwarder.forward_messages_to_channel(number_of_messages_to_track, source_chat_id, destination_channel_id, keywords)
    elif choice == "3":
        print("Exiting...")
    else:
        print("Invalid choice")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())


## NAO TEM AFIXAR
## ADICIONAR VÁRIOS CANAIS PARA COPIAR E DE DESTINO
## ADICIONAR KEYWORDS