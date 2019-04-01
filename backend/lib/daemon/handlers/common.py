from lib.daemon import context
from lib.daemon.core import repost_message, get_client

def handle_ping():
    return {'clients': len(context.accounts)}

async def handle_repost_message(vk_user_id: int, vk_group_id: int, tg_channel_id: int, msg_id: int):
    vk_user_id = int(vk_user_id)
    vk_group_id = int(vk_group_id)
    tg_channel_id = int(tg_channel_id)
    msg_id = int(msg_id)

    client = await get_client(vk_user_id)
    await client.get_dialogs()
    message = await client.get_messages(client.get_entity(tg_channel_id), ids=msg_id)

    await repost_message(vk_user_id, vk_group_id, message)
    return True
