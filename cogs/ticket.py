import disnake
import os
import json

from datetime import timezone,timedelta
from disnake.ext import commands
from disnake import ApplicationCommandInteraction,Option,Colour,OptionType,Member
from typing import Optional

class View(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.channel = None
        self.ticket_channel = None
    
    @disnake.ui.button(label="點我創建",style=disnake.ButtonStyle.green,custom_id="create_ticket")
    async def create_ticket(self, button: disnake.ui.Button, interaction: ApplicationCommandInteraction):
        with open("blacklist.json","r",encoding='utf-8') as f: #先讀取黑名單的名單
                data = json.load(f)
        print(data)
        try: #調用json的數據
            author = data[f"{interaction.author.name}"] 
        except KeyError: #如果沒有這個人就將字串設為空
            author = ""
        if interaction.author.id == author:
            embed = disnake.Embed(title="❌ | 你因遭到了封禁而無法使用此功能!",colour=Colour.red())
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            self.channel = interaction.channel #按按鈕的頻道
            try:
                self.ticket_channel = disnake.utils.get(interaction.guild.text_channels,id=self.ticket_channel.id)
            except AttributeError:
                pass
            if self.ticket_channel is not None: #如果已經創建過了,即跳出此訊息
                failed_embed = disnake.Embed(title="<:x_mark:1033955039615664199> | 你已經有這個頻道了!",description=f"你的頻道在 {self.ticket_channel.mention}",colour=disnake.Colour.red())
                await interaction.response.send_message(embed=failed_embed,ephemeral=True)
            else:
                loading_embed = disnake.Embed(title="<a:Loading:1059806500241027157> | 正在創建中...",colour=disnake.Colour.light_grey())
                await interaction.response.send_message(embed=loading_embed,ephemeral=True)
                overwrites = { #複寫對於客服單頻道的權限 (只讓創建者可看到這頻道的權限)
                    interaction.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                    interaction.guild.me: disnake.PermissionOverwrite(view_channel=True,send_messages=True,attach_files=True,embed_links=True),
                    interaction.user: disnake.PermissionOverwrite(view_channel=True)
                }
                self.ticket_channel = await interaction.guild.create_text_channel(f"客服單-{interaction.user.name}",overwrites=overwrites,category=self.channel.category) #創立頻道時繼承複寫權限和類別
                success_embed = disnake.Embed(title="✅ | 成功創建!",description=f"你的頻道在 {self.ticket_channel.mention}",colour=Colour.green())
                await interaction.edit_original_message(embed=success_embed) #編輯讀取訊息
                channel_embed = disnake.Embed(title=f"{interaction.user.name} 的客服單",description="請等待人員處理您的問題",colour=Colour.random())
                view = TicketView()
                member = interaction.user #用戶
                message = await self.ticket_channel.send(content=f"{member.mention}") #傳送一則tag創建者的訊息
                await message.delete() #刪除訊息
                await self.ticket_channel.send(embed=channel_embed,view=view)
                
class TicketView(disnake.ui.View): #客
    def __init__(self):
        super().__init__(timeout=None)
        self.lock = True
        self.channel = None
    
    @disnake.ui.button(label="鎖定客服單",style=disnake.ButtonStyle.blurple,custom_id="lock_ticket")
    async def lock_ticket(self, button: disnake.ui.Button, interaction: ApplicationCommandInteraction):
        if interaction.guild.get_member(interaction.user.id).guild_permissions.manage_channels == True:
            self.channel = interaction.channel #按按鈕的頻道
            if self.lock == True: #偵測是否已經鎖定
                try:
                    conversation_record = await self.channel.history(limit=None).flatten() #讀取頻道的歷史訊息
                    text = "" #將字串變為空
                except NameError: #如果遇到錯誤
                    ticket_channel = disnake.utils.get(interaction.guild.text_channels,id=self.channel.id) #抓取客服單的頻道
                    conversation_record = await ticket_channel.history(limit=None).flatten() #讀取頻道的歷史訊息
                    text = "" #將字串變為空
                for message in conversation_record: #利用迴圈讀取歷史訊息
                    if message.author.id != interaction.guild.me.id and message.content != "": #排除機器人的訊息和內容空白
                        now = message.created_at.astimezone(timezone(offset = timedelta(hours = 8))) #將時區變為台灣時區
                        text = f"{now.year}/{now.month}/{now.day} {now.hour}:{now.minute} - {message.author.display_name}: {message.content}\n{text}"
                with open(f"chat.txt",'w',encoding='UTF-8') as chat:
                    chat.write(text) #將訊息寫入至chat.txt
                ticket_channel = disnake.utils.get(interaction.guild.text_channels,id=self.channel.id)
                overwrites = { #複寫對於客服單頻道的權限 (將創建者移出可看到這頻道的權限)
                        interaction.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                        interaction.guild.me: disnake.PermissionOverwrite(view_channel=False),
                        interaction.user: disnake.PermissionOverwrite(view_channel=False)
                    } 
                await ticket_channel.edit(overwrites=overwrites) #編輯頻道權限以複寫權限
                await interaction.response.send_message(f"客服單已被 {interaction.user.name} 鎖定!")
                await interaction.followup.send(f"本次對話紀錄檔案:",file=disnake.File(f"chat.txt")) #傳送一則帶有對話紀錄檔案的訊息
                os.remove(f"chat.txt") #移除檔案
                self.lock = None
            else:
                await interaction.response.send_message(f"此頻道已經被鎖定了!",ephemeral=True)
        else:
            await interaction.response.send_message("你無法鎖定客服單! 請聯繫管理人員以鎖定此克服單",ephemeral=True)
        



    @disnake.ui.button(label="刪除客服單",style=disnake.ButtonStyle.red,custom_id="del_ticket")
    async def delete_ticket(self, button: disnake.ui.Button, interaction: ApplicationCommandInteraction):
        if interaction.guild.get_member(interaction.user.id).guild_permissions.manage_channels == True:
                ticket_channel = disnake.utils.get(interaction.guild.text_channels,id=self.channel.id)
                loading_embed = disnake.Embed(title="<a:Loading:1059806500241027157> | 正在刪除...",colour=disnake.Colour.light_grey())
                await interaction.response.send_message(embed=loading_embed)
                await ticket_channel.delete()
        else:
            await interaction.response.send_message("你無法刪除客服單! 請聯繫管理人員以刪除此客服單",ephemeral=True)


class ticket(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.list = []
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(View())
        self.bot.add_view(TicketView())
    
    @commands.slash_command(name="ticket")
    async def ticket(self, interaction: ApplicationCommandInteraction):
        pass
    
    @ticket.sub_command(name="create",description="創建一個可供你和管理員聯繫的頻道",options=[Option(name="text",description="設定您想給大家知道用途的介紹文字 (留空自動生成)",required=False)])
    @commands.has_permissions(manage_messages=True)
    async def create(self, interaction: ApplicationCommandInteraction, text:str):
        if text != None: #偵測是否留空
            embed = disnake.Embed(title="開啟客服單的系統",description=f"{text}",colour=disnake.Colour.orange()) 
        else:
            embed = disnake.Embed(title="開啟客服單的系統",description="如果你需要和服務人員聯絡\n請點擊下方按鈕開啟客服單",colour=disnake.Colour.orange())
            view = View()
            await interaction.response.send_message(embed=embed,view=view)

    @ticket.sub_command(name="ban",description="封禁一位使用者使用ticket系統",options=[Option(name="member",description="選擇禁止使用ticket的用戶",type=OptionType.user,required=True)])
    @commands.has_permissions(manage_messages=True)
    async def ban(self, interaction: ApplicationCommandInteraction, member:Optional[Member]):
        with open("blacklist.json","r",encoding='utf-8') as f:
            data = json.load(f) #讀取黑名單
        if member.name not in data: #偵測用戶在不在名單中
            with open("blacklist.json","r",encoding='utf-8') as f:
                data = json.load(f)
            data[f"{member.name}"] = member.id #沒有則加入
            with open("blacklist.json","w",encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False)
            embed = disnake.Embed(title="✅ | 成功!",description=f"已封鎖了 {member.mention}",colour=Colour.green())
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else: #有則顯示
            embed = disnake.Embed(title="❌ | 你已經封禁過這位使用者了!",colour=Colour.red())
            await interaction.response.send_message(embed=embed,ephemeral=True) 

    @ticket.sub_command(name="unban",description="解封一位使用者使用ticket系統",options=[Option(name="member",description="選擇解封使用ticket的用戶",type=OptionType.user,required=True)])
    @commands.has_permissions(manage_messages=True)
    async def unban(self, interaction: ApplicationCommandInteraction, member:Optional[Member]):
        with open("blacklist.json","r",encoding='utf-8') as f:
            data = json.load(f)
        if member.name in data:
            del data[f"{member.name}"]
            with open("blacklist.json","w",encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False)                  
            embed = disnake.Embed(title="✅ | 成功!",description=f"已解封了 {member.mention}",colour=Colour.green())
            await interaction.response.send_message(embed=embed,ephemeral=True) 
        else:
            embed = disnake.Embed(title="❌ | 你先前並沒有封禁過這位使用者喔!",colour=Colour.red())
            await interaction.response.send_message(embed=embed,ephemeral=True)   
    @ticket.sub_command(name="blacklist",description="查看遭到封禁的名單")
    async def blacklist(self, interaction: ApplicationCommandInteraction):
        with open("blacklist.json","r",encoding='utf-8') as f:
            data = json.load(f)
        for i in data:
            self.list.append(i) #將用戶名稱寫入至list
        if self.list == []: #如果list為空時
            embed = disnake.Embed(title="🔨 | 沒有被封禁的使用者",colour=Colour.red())
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            embed = disnake.Embed(title="🔨 | 遭到封禁的名單",description=",".join(self.list),colour=Colour.random()) #顯示名單
            await interaction.response.send_message(embed=embed,ephemeral=True)

def setup(bot):
    bot.add_cog(ticket(bot))