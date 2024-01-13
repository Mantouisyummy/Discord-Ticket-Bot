from disnake import (
    ApplicationCommandInteraction,
    Embed,
    Option,
    TextChannel,
    ChannelType,
    CategoryChannel,
    Colour,
    PartialEmoji,
    ButtonStyle,
    OptionChoice,
    OptionType,
    Member,
)

from disnake.ext import commands
from disnake.ext.commands import Param
from disnake.ui import Button

from core.bot import Bot

from core.database import create_table
from core.ticket_utils import add_ticket, export_setting
from core.models import Ticket
from core.embeds import SuccessEmbed, ErrorEmbed
from core.modal import TicketModal
from core.view import TicketView

# pylint: disable=C0116
# pylint: disable=C0115


class Ticket_Cog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.button_list = []
        create_table()

    @commands.slash_command(name="ticket")
    async def ticket(self, interaction):
        pass

    @commands.slash_command(
        name="grab_button",
        description="搶按鈕",
        options=[Option(name="prize", required=True, type=OptionType.string)],
    )
    async def grab_button(self, interaction: ApplicationCommandInteraction, prize: str):
        embed = Embed(
            title="搶按鈕",
            description=f"獎品：{prize}\n想辦法成為最快點擊按鈕的吧！",
            colour=Colour.random(),
        )

        components = [Button(label=prize, style=ButtonStyle.green, custom_id=f"click")]

        await interaction.response.send_message(embed=embed, components=components)

    @ticket.sub_command(name="setup", description="基礎客服單設定，指令執行後將會帶入到輸入客服單資訊表單部分")
    async def setup(
        self,
        interaction: ApplicationCommandInteraction,
        ticket_channel: TextChannel = Param(
            name="傳送訊息頻道", description="開啟客服單訊息傳送頻道", channel_types=[ChannelType.text]
        ),
        log_channel: TextChannel = Param(
            name="紀錄傳送頻道",
            description="客服單紀錄傳送頻道，留空則不建立",
            channel_types=[ChannelType.text],
        ),
    ):
        for webhook in await log_channel.webhooks():
            if webhook.name == "ticket_logging":
                break
        else:
            webhook = await log_channel.create_webhook(name="ticket_logging")

        ticket = Ticket(
            guild_id=interaction.guild_id,
            ticket_channel_id=ticket_channel.id,
            log_channel_id=log_channel.id,
            ticket_message_id=0,
            ticket_name="ticket-{user}",
            webhook_url=webhook.url,
        )

        add_ticket(ticket)
        modal = TicketModal()
        await interaction.response.send_modal(modal=modal)

    @ticket.sub_command(name="settings", description="查看目前客服單的設定")
    async def settings(
        self,
        interaction: ApplicationCommandInteraction,
    ):
        result = export_setting(guild_id=interaction.guild_id).first()

        ticket_channel = self.bot.get_channel(result.ticket_channel_id)
        log_channel = self.bot.get_channel(result.log_channel_id)

        embed = Embed(title="客服單設定檢視", colour=Colour.random())
        embed.add_field(name="客服單頻道", value=ticket_channel.mention, inline=False)
        embed.add_field(name="紀錄頻道", value=log_channel.mention, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ticket.sub_command(name="add_button", description="新增一個對應類別的按鈕")
    async def button(
        self,
        interaction: ApplicationCommandInteraction,
        name: str = Param(name="按鈕名稱"),
        style: int = Param(
            name="按鈕顏色",
            choices=[
                OptionChoice(name="綠色", value=3),
                OptionChoice(name="紫藍色", value=1),
                OptionChoice(name="灰色", value=2),
                OptionChoice(name="紅色", value=4),
            ],
        ),
        emoji_str: str = Param(name="按鈕表情符號", description="擺在按鈕文字旁的表情符號"),
        category: CategoryChannel = Param(
            name="類別", description="選定的按鈕綁定類別", channel_types=[ChannelType.category]
        ),
    ):
        match style:
            case 3:
                style = ButtonStyle.green
            case 1:
                style = ButtonStyle.blurple
            case 2:
                style = ButtonStyle.gray
            case 4:
                style = ButtonStyle.red

        emoji = None
        if not isinstance(emoji_str, Option):
            emoji = PartialEmoji.from_str(emoji_str)

        view = TicketView()

        setting = export_setting(guild_id=interaction.guild_id)

        result = setting.first()

        self.button_list.append(
            Button(label=name, emoji=emoji, custom_id=f"{category.id}", style=style)
        )

        for button in self.button_list:
            view.add_item(button)

        channel = interaction.guild.get_channel(result.ticket_channel_id)
        message = await channel.fetch_message(result.ticket_message_id)

        await message.edit(view=view)
        await interaction.response.send_message(
            embed=SuccessEmbed(title="新增成功!"), ephemeral=True
        )

    @ticket.sub_command(name="add_user", description="新增一個使用者至客服單中")
    async def add_user(
        self,
        interaction: ApplicationCommandInteraction,
        user: Member = Param(name="使用者"),
        channel: TextChannel = Param(name="客服單頻道"),
    ):
        if channel.name.startswith("ticket-") and len(channel.name.split("-")) == 3:
            overwrites = await channel.overwrites_for(user)
            overwrites.read_messages = True
            overwrites.view_channel = True
            await channel.set_permissions(target=user, overwrite=overwrites)
            await interaction.response.send_message(
                embed=SuccessEmbed(
                    title=f"操作成功",
                    description=f"已將 {user.mention} 加入至 {channel.mention}!",
                )
            )
        else:
            return await interaction.response.send_message(
                embed=ErrorEmbed(title="操作失敗", description="這並不是一個客服單頻道!")
            )

    @ticket.sub_command(name="remove_user", description="將使用者從客服單中移除")
    async def remove_user(
        self,
        interaction: ApplicationCommandInteraction,
        user: Member = Param(name="使用者"),
        channel: TextChannel = Param(name="客服單頻道"),
    ):
        if channel.name.startswith("ticket-") and len(channel.name.split("-")) == 3:
            overwrites = await channel.overwrites_for(user)
            overwrites.read_messages = False
            overwrites.view_channel = False
            await channel.set_permissions(target=user, overwrite=overwrites)
            await interaction.response.send_message(
                embed=SuccessEmbed(
                    title=f"操作成功",
                    description=f"已將 {user.mention} 從 {channel.mention} 移除!",
                )
            )
        else:
            return await interaction.response.send_message(
                embed=ErrorEmbed(title="操作失敗", description="這並不是一個客服單頻道!")
            )


def setup(bot: commands.Bot):
    bot.add_cog(Ticket_Cog(bot))
