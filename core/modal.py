from disnake import TextInputStyle, ModalInteraction, Embed, Colour
from disnake.ui import Modal, TextInput, Button

from core.ticket_utils import export_setting
from core.embeds import SuccessEmbed

class TicketModal(Modal):
    def __init__(self) -> None:
        components = [
            TextInput(
                label="標題",
                placeholder="客服單訊息標題",
                custom_id="title",
                style=TextInputStyle.short,
                max_length=20,
            ),
            TextInput(
                label="內文",
                placeholder="客服單訊息內文",
                custom_id="description",
                style=TextInputStyle.paragraph,
            ),
            TextInput(
                label="客服單名稱",
                placeholder="可選參數：\n{subject} -> 開啟主題\n{username} -> 開啟者用戶名稱\n{display_name} -> 開啟者顯示名稱",
                custom_id="ticket_name",
                style=TextInputStyle.paragraph,
                max_length=50,
            ),
        ]
        super().__init__(title="客服單設定", components=components)

    async def callback(self, inter: ModalInteraction):
        embed = Embed(title=inter.text_values['title'], description=f"""{inter.text_values['description']}""", colour=Colour.random())
        result = export_setting(guild_id=inter.guild_id).first()
        
        channel = inter.guild.get_channel(result.ticket_channel_id)
        message = await channel.send(embed=embed)
        
        result = export_setting(guild_id=inter.guild_id)
        result.update({"ticket_message_id": message.id, "ticket_name": inter.text_values['ticket_name']})
        result.session.commit()
        result.session.close()
        
        embed = SuccessEmbed(title="客服單設定成功!")
        await inter.response.send_message(embed=embed)