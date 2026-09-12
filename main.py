import discord
import os
import google.generativeai as genai
from threading import Thread
from flask import Flask
import time
import random

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Discord AI đang online!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web).start()

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

# Gom tất cả các Key có trên Render vào một danh sách
api_keys = []
for key_name in ['GEMINI_KEY_1', 'GEMINI_KEY_2', 'GEMINI_KEY_3', 'GEMINI_API_KEY']:
    key_value = os.environ.get(key_name)
    if key_value:
        api_keys.append(key_value)

instruction = "Bạn là AI hỗ trợ của server Honey Bee Hive. BẮT BUỘC TRẢ LỜI CỰC KỲ NGẮN GỌN (dưới 30 chữ), đi thẳng vào vấn đề, không giải thích dài dòng."

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

user_cooldowns = {}
COOLDOWN_TIME = 60  

@client.event
async def on_ready():
    print(f'Bot {client.user} đã sẵn sàng phục vụ!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        user_id = message.author.id
        current_time = time.time()
        
        if user_id in user_cooldowns:
            time_passed = current_time - user_cooldowns[user_id]
            if time_passed < COOLDOWN_TIME:
                time_left = int(COOLDOWN_TIME - time_passed)
                await message.reply(f"⏳ Chờ chút nha, {time_left} giây nữa mới được gọi mình tiếp!")
                return
        
        prompt = message.content.replace(f'<@{client.user.id}>', '').strip()
        if not prompt:
            await message.reply("Có mình đây!")
            return

        user_cooldowns[user_id] = current_time

        async with message.channel.typing():
            try:
                # Bốc ngẫu nhiên 1 Key trong danh sách để né giới hạn 20 lượt/phút
                if api_keys:
                    selected_key = random.choice(api_keys)
                    genai.configure(api_key=selected_key)
                
                model = genai.GenerativeModel('gemini-3.6-flash', system_instruction=instruction)
                response = await model.generate_content_async(prompt)
                await message.reply(response.text[:1996])
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota" in error_msg:
                    await message.reply("🐝 Ui chà, nhiều bạn gọi cùng lúc quá hệ thống xử lý không kịp! Mọi người đợi khoảng 1 phút rồi nhắn lại cho mình nha.")
                else:
                    await message.reply("🐝 Mình đang khởi động lại dữ liệu một chút, bạn thử lại sau 3 giây nhé!")
                print(f"Error: {e}")

if DISCORD_TOKEN:
    client.run(DISCORD_TOKEN)
