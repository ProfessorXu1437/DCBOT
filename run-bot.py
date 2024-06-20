import discord
from discord.ext import commands
import requests
import zipfile
import io
from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

# 获取 Discord 令牌
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if DISCORD_TOKEN is None:
    raise ValueError("No Discord token found. Please set it in the .env file.")


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

import random
import string

def request_list(username):
    url = 'https://professorxu.pythonanywhere.com/requestlist'
    data = {
        "username": username
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=data, headers=headers)
    return response

def generate_strong_password(length=16):

    characters = string.ascii_letters + string.digits + string.punctuation
    

    password = [
        random.choice(string.ascii_letters),
        random.choice(string.digits),
        random.choice(string.punctuation)
    ]
    

    password += random.choices(characters, k=length-3)
    

    random.shuffle(password)

    return ''.join(password)

BASE_URL = 'https://professorxu.pythonanywhere.com'
VALID_ADMIN_PASSWORD = 'nekonekonyannyan'
HEADERS = {'Content-Type': 'application/json'}

def register(username, password, VALID_ADMIN_PASSWORD1):
    payload = {
        "username": username,
        "password": password,
        "admin_password": VALID_ADMIN_PASSWORD1
    }
    response = requests.post(f'{BASE_URL}/register', json=payload, headers=HEADERS)
    return response

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.guild is None and message.author != bot.user:  # 检查消息是否是私信
        username = message.author.name
        discriminator = message.author.discriminator
        full_name = f"{username}#{discriminator}"

        if message.content.lower() == "注册":
            
            newpassword = generate_strong_password()

            response = register(full_name, newpassword, VALID_ADMIN_PASSWORD)
            response_data = response.json()
            if response_data["status"] == "success":
                await message.author.send(f"已成功注册用户：{full_name}，  默认密码: {newpassword}  使用以上信息登录程序即可。")
            
            elif response_data["status"] == "failed":
                await message.author.send(f"该用户已经注册过：{full_name}")

        
        elif message.content.lower() == "获取list":
            response = request_list(full_name)
            response_data = response.json()
            json_content = response_data["message"]

            temp_file = io.StringIO(json_content)
            temp_file.seek(0)

            # 创建一个字节流来保存zip文件
            zip_buffer = io.BytesIO()
            # 创建zip文件
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                temp_file.seek(0)
                zip_file.writestr("list.json", temp_file.read())

            # 重置缓冲区位置到开始
            zip_buffer.seek(0)

            await message.author.send("你的配置文件：", file=discord.File(zip_buffer, filename="files.zip"))

        else:
            await message.author.send("无效的选项，请输入 '注册' 或 '获取list'。")
    await bot.process_commands(message)

@bot.command()
async def start(ctx):
    await ctx.send("请私信我 '注册' 或 '获取list' 来选择一个选项。")

bot.run(DISCORD_TOKEN)
