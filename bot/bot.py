import asyncio
import logging
import os
import urllib.parse

import confuse
from izihawa_loglib import configure_logging
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename
from trident.client import TridentClient

app_id = int(os.environ.get('APP_ID'))
app_hash = os.environ.get('APP_HASH')
bot_token = os.environ.get('BOT_TOKEN')


async def main():
    config = confuse.Configuration('bot')
    config.set({'application': {'debug': True}})
    configure_logging(config)
    telegram_client = TelegramClient('bot', app_id, app_hash)
    await telegram_client.start(bot_token=bot_token)

    trident_client = TridentClient("http://localhost:7080")
    await trident_client.start()

    @telegram_client.on(events.NewMessage)
    async def file_handler(event):
        maybe_doi = event.raw_text.strip()
        file_name = urllib.parse.quote_plus(f'{maybe_doi}.pdf')
        logging.info(f"received request {maybe_doi}")
        content = await trident_client.table_get('science', file_name)
        if not content:
            return await event.reply(f"`{maybe_doi}` not found!")
        await telegram_client.send_file(
            entity=event.chat_id,
            file=content,
            attributes=[DocumentAttributeFilename(file_name)],
        )

    await telegram_client.run_until_disconnected()
    await trident_client.stop()

asyncio.run(main())
