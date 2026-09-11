import discord
import os
import google.generativeai as genai
from threading import Thread
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Discord AI đang online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web).start()

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# 1. ÉP TRẢ LỜI NGẮN: Chỉnh sửa lại yêu cầu cốt lõi của bot
instruction = "Bạn là AI hỗ trợ của server Honey Bee Hive. BẮT BUỘC TRẢ LỜI CỰC KỲ NGẮN GỌN (dưới 30 chữ), đi thẳng vào vấn đề, không giải thích dài dòng."
model = genai.GenerativeModel('gemini-3.6-flash', system_instruction=instruction)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot {client.user} đã sẵn sàng phục vụ!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        if not prompt:
            await message.reply("Có mình đây!")
            return

        async with message.channel.typing():
            try:
                # 2. XỬ LÝ ĐA LUỒNG: Dùng hàm async để bot không bị treo khi nhiều người tag
                response = await model.generate_content_async(prompt)
                await message.reply(response.text[:1996])
            except Exception as e:
                await message.reply("Đang bận xử lý dữ liệu, bạn thử lại sau 3 giây nhé!")
                print(f"Error: {e}")

if DISCORD_TOKEN:
    client.run(DISCORD_TOKEN)
