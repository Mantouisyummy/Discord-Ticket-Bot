from disnake import (
    ApplicationCommandInteraction,
    MessageInteraction,
    PermissionOverwrite,
    Embed,
    Colour,
    ButtonStyle,
)

from disnake.ext import commands
from disnake.ext.commands import CommandInvokeError
from disnake.utils import get
from disnake.ui import Button

from core.bot import Bot
from core.embeds import ErrorEmbed, SuccessEmbed, CloseEmbed
from core.view import TicketView
from core.ticket_utils import export_setting, parse_name, log_send, generate_history

import asyncio


class Ticket_Events(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_slash_command_error(self, interaction: ApplicationCommandInteraction, error: CommandInvokeError):
    # embed = ErrorEmbed(title="啊喔，出現了個錯誤：(", description=f"```{error.original}```")
    # await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView())

    @commands.Cog.listener()
    async def on_message_interaction(self, interaction: MessageInteraction):
        match interaction.data.custom_id:
            case "click":
                embed = Embed(
                    title="最快的人出爐！",
                    description=f"恭喜 {interaction.user.mention} 🎉🎉🎉\n獲得 **{interaction.component.label}** !",
                    colour=Colour.green(),
                )
                await interaction.message.edit(embed=embed, components=None)
            case "control_close":
                await interaction.response.defer()

                channel = interaction.channel

                overwrites = {
                    interaction.guild.default_role: PermissionOverwrite(
                        view_channel=False
                    ),
                    interaction.guild.me: PermissionOverwrite(view_channel=True),
                }

                await log_send(
                    name=channel.name,
                    avatar_url=self.bot.user.avatar.url,
                    created=interaction.author.mention,
                    guild_id=interaction.guild_id,
                    subject=None,
                    mode="close",
                    closer=interaction.user.mention,
                    channel=channel,
                )

                await channel.edit(overwrites=overwrites)

                await interaction.edit_original_response(
                    embed=CloseEmbed(title="已關閉客服單，頻道將會在五秒後刪除..."), components=None
                )
                await asyncio.sleep(5)
                await channel.delete(reason="客服單關閉")
            case _:
                if not interaction.data.custom_id.startswith("control"):
                    await interaction.response.defer()

                    if channel := get(
                        interaction.guild.text_channels, topic=str(interaction.user.id)
                    ):
                        return await interaction.response.send_message(
                            embed=ErrorEmbed(
                                title="你已經有客服單了!", description=f"在這 {channel.mention}"
                            ),
                            ephemeral=True,
                        )

                    category = get(
                        interaction.guild.categories, id=int(interaction.data.custom_id)
                    )

                    overwrites = {
                        interaction.guild.default_role: PermissionOverwrite(
                            view_channel=False
                        ),
                        interaction.guild.me: PermissionOverwrite(view_channel=True),
                        interaction.author: PermissionOverwrite(view_channel=True),
                    }

                    result = export_setting(interaction.guild_id).first()

                    name = parse_name(
                        result.ticket_name,
                        interaction.user,
                        interaction.component.label,
                    )

                    channel = await category.create_text_channel(
                        name=name, overwrites=overwrites, topic=str(interaction.user.id)
                    )

                    components = [
                        Button(
                            label="關閉客服單",
                            style=ButtonStyle.red,
                            custom_id="control_close",
                            emoji="❌",
                        )
                    ]

                    await channel.send(
                        embed=Embed(
                            title="控制面板",
                            description=f"開啟者： {interaction.user.mention}",
                            colour=Colour.random(),
                        ),
                        components=components,
                    )

                    await log_send(
                        name=name,
                        avatar_url=self.bot.user.avatar.url,
                        created=interaction.author.mention,
                        guild_id=interaction.guild_id,
                        subject=interaction.component.label,
                        mode="create",
                    )

                    await interaction.edit_original_response(
                        embed=SuccessEmbed(
                            title="創建客服單成功！", description=f"你的客服單在 {channel.mention}"
                        ),
                        ephemeral=True,
                    )


def setup(bot: commands.Bot):
    bot.add_cog(Ticket_Events(bot))
