import discord
import os
import google.generativeai as genai
from threading import Thread
from flask import Flask

# Tạo web server nhỏ để Render kiểm tra bot còn sống
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Discord AI đang online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Khởi chạy web server chạy nền
Thread(target=run_web).start()

# Lấy Token và API Key từ biến môi trường
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
instruction = "Bạn là trợ lý ảo thân thiện của server Honey Bee Hive. Hãy trả lời ngắn gọn, nhiệt tình, có icon sinh động bằng tiếng Việt."
model = genai.GenerativeModel('gemini-pro')

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

    # Trả lời khi được tag hoặc khi nhắn tin riêng (DM)
    if client.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        if not prompt:
            await message.reply("Chào bạn! Bạn cần mình giúp gì nào?")
            return

        async with message.channel.typing():
            try:
                response = model.generate_content(prompt)
                reply_text = response.text
                if len(reply_text) > 2000:
                    reply_text = reply_text[:1996] + "..."
                await message.reply(reply_text)
                        except Exception as e:
                await message.reply(f"Lỗi AI: {e}")
                print(f"Error: {e}")

if DISCORD_TOKEN:
    client.run(DISCORD_TOKEN)
