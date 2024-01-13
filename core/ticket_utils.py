from .models import Ticket

from .database import create_session

from typing import Optional

from disnake import Member, Webhook, TextChannel, File, ButtonStyle
from disnake.ui import Button

from core.embeds import LogEmbed

import aiohttp
import chat_exporter
import io


def add_ticket(ticket: Ticket):
    session = create_session()
    result = session.query(Ticket).filter_by(guild_id=ticket.guild_id)

    if result.first() is None:
        session.add(ticket)
    else:
        ticket.__dict__.pop("_sa_instance_state")
        result.update(ticket.__dict__)

    session.commit()
    session.close()


def export_setting(guild_id: int):
    session = create_session()

    setting = session.query(Ticket).filter_by(guild_id=guild_id)

    return setting


def parse_name(name: str, user: Member, subject: str):
    return (
        name.replace("{username}", user.name)
        .replace("{display_name}", user.display_name)
        .replace("{subject}", subject)
    )


async def generate_history(channel: TextChannel):
    transcript = await chat_exporter.export(channel, tz_info="Asia/Taipei")

    transcript_file = File(
        io.BytesIO(transcript.encode()),
        filename=f"transcript-{channel.name}.html",
    )

    return transcript_file


async def log_send(
    name: str,
    avatar_url: str,
    created: str,
    subject: Optional[str],
    guild_id: int,
    mode: str,
    closer: str = None,
    channel: TextChannel = None,
):
    reuslt = export_setting(guild_id).first()

    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(reuslt.webhook_url, session=session)

        if subject is None:
            subject = name.split("-")[1]

        match mode:
            case "create":
                await webhook.send(
                    username="紀錄",
                    avatar_url=avatar_url,
                    embed=LogEmbed(
                        name=name, created=created, subject=subject, mode=mode
                    ),
                )
            case "close":
                file = await generate_history(channel)
                message = await webhook.send(
                    username="紀錄",
                    avatar_url=avatar_url,
                    embed=LogEmbed(
                        name=name,
                        created=created,
                        subject=subject,
                        mode=mode,
                        closer=closer,
                    ),
                    file=file,
                    wait=True,
                )
                compoents = [
                    Button(
                        label="點我查看對話紀錄",
                        style=ButtonStyle.url,
                        url="https://allen.asallenshih.tw/api/?type=view&ver=v2&url="
                        + message.attachments[0].url,
                    )
                ]
                await message.edit(components=compoents)
