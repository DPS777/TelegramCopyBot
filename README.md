# TelegramCopyBot

TelegramCopyBot is a Python-based bot that automates copying messages from one Telegram chat to another.


## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/DPS777/TelegramCopyBot.git
    ```
2. Navigate to the project directory:
    ```sh
    cd TelegramCopyBot
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration

All the configuration is made during the usage of the bot.

## Get API Key from Telegram

1. Go to https://my.telegram.org
2. Enter your phone number
3. Select <ins>API development tools</ins> option
4. Create an APP, if you don't have one (The configuration of the APP is not important, but to be sure, on Plantform select <ins>Web</ins>)
5. Save **`App api_id`** and **`App api_hash`**
6. And you are ready to go

## Usage

1. Run the Bot:
    ```sh
    python ./TelegramCopyBot.py
    ```
2. If you don't have the ID's of the chat to copy from and the chat to send the messages to, select option 1.
3. After copying the chat ID's, select option 2 and follow the given steps
4. Enjoy your new Bot

## Warnings

### MessageDeleted Event
Occurs whenever a message is deleted. Note that this event isn’t 100% reliable, since Telegram doesn’t always notify the clients that a message was deleted.

    ### Important ###

    Telegram does not send information about where a message was deleted if it occurs in private conversations with other users or in small group chats, because message IDs are unique and you can identify the chat with the message ID alone if you saved it previously.

    Telethon does not save information of where messages occur, so it cannot know in which chat a message was deleted (this will only work in channels, where the channel ID is present).

    This means that the chats= parameter will not work reliably, unless you intend on working with channels and super-groups only.

## Notes

### MessageDeleted Event
Messages deleted by the bot are placed in an event array until manual deletion is carried out. When this manual deletion is carried out, all messages deleted up to this point are returned in the array, but the deleted_id of the event is the first element of the array, which may not match the last deleted message. 

```sh
MessageDeleted.Event(original_update=UpdateDeleteChannelMessages(channel_id=2173968782, messages=[1238, 1239, 1240], pts=1327, pts_count=0), deleted_id=1238, deleted_ids=[1238, 1239, 1240])
```

When messages are deleted manually, the array has only one element that corresponds to the deleted_id.

```sh
MessageDeleted.Event(original_update=UpdateDeleteChannelMessages(channel_id=2173968782, messages=[1249], pts=1348, pts_count=1), deleted_id=1249, deleted_ids=[1249])
```

## Future Features

- Add pin messages
- Add multiple channels to copy from and to send to
- Add keywords option (in code but not working)

## License

This project is licensed under the MIT License.