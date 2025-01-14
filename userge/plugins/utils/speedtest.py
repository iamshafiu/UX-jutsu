# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.

import os

import speedtest
import asyncio
from userge import Message, userge
from userge.utils import humanbytes

CHANNEL = userge.getCLogger(__name__)


@userge.on_cmd("speedtest", about={"header": "test your server speed"})
async def speedtst(message: Message):
    me = await userge.get_me()
    user = " ".join([me.first_name, me.last_name or ""])
    reply = message.reply_to_message
    if reply:
        reply_to = reply.message_id
    else:
        reply_to = message.message_id
    await message.edit("`Running speed test . . .`")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        await message.try_to_edit("`Performing download test . . .`")
        test.download()
        await message.try_to_edit("`Performing upload test . . .`")
        test.upload()
        result = test.results.dict()
        url = test.results.share()
    except Exception as e:
        await message.err(text=e)
        return
    download = await asyncio.create_subprocess_shell(f"wget {url}")
    await download.communicate()
    file = os.path.basename(url)
    if os.path.isfile(file):
        path = file
    else:
        path = url
    output = f"""**--Started at {result['timestamp']}--

Client: {user}

ISP: `{result['client']['isp']}`
Country: `{result['client']['country']}`

Server: `NASA`

Name: `{result['server']['name']}`
Country: `{result['server']['country']}, {result['server']['cc']}`
Sponsor: `{result['server']['sponsor']}`
Latency: `{result['server']['latency']}`

Ping: `{result['ping']}`
Sent: `{humanbytes(result['bytes_sent'])}`
Received: `{humanbytes(result['bytes_received'])}`
Download: `{humanbytes(result['download'] / 8)}/s`
Upload: `{humanbytes(result['upload'] / 8)}/s`**"""
    msg = await message.client.send_photo(
        chat_id=message.chat.id,
        photo=path,
        caption=output,
        reply_to_message_id=reply_to,
    )
    await CHANNEL.fwd_msg(msg)
    os.remove(path)
    await message.delete()
