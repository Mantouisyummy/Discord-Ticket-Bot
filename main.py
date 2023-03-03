import asyncio
import json
import logging
from os import getenv
import os

from dotenv import load_dotenv
from disnake import Intents
from disnake.ext.commands import CommandSyncFlags

from disnake.ext.commands import Bot 

logging.basicConfig(level=logging.INFO)



loop = asyncio.new_event_loop()

bot = Bot(
    command_prefix=None, intents=Intents.all(), loop=loop,
    command_sync_flags=CommandSyncFlags.default()
)

@bot.event
async def on_ready():
    print("###此開源由Man頭(´・ω・)#8870製作,使用請註明來源###")
    print(f"-----------------{bot.user.name} 啟動成功!----------------")
    load_extensions(bot)
    load_dotenv()
    
def load_extensions(bot: Bot) -> Bot:
    """
    Load extensions.
    """
for file in os.listdir('./cogs'):  # 抓取所有cog資料夾裡的檔案
    if file.endswith('.py'):  # 判斷檔案是否是python檔
        try:
            # 載入cog,[:-3]是字串切片,為了把.py消除
            bot.load_extension(f'cogs.{file[:-3]}')
            print(f'✅ 已加載 {file}')
        except Exception as error:  # 如果cog未正確載入
            print(f'❌ {file} 發生錯誤  {error}')


if __name__ == "__main__":
    with open("config.json","r") as f: #讀取config.json
        data = json.load(f)
    token = data["TOKEN"]
    bot.run(token)
    
