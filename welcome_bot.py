import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os

intents = discord.Intents.default()
intents.members = True  # Quan trọng để nhận sự kiện thành viên mới

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is ready as {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        # Lấy avatar người dùng (hoặc avatar mặc định)
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).resize((150, 150)).convert("RGBA")

        # Tạo avatar tròn
        mask = Image.new("L", (150, 150), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 150, 150), fill=255)
        avatar_circle = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
        avatar_circle.paste(avatar, (0, 0), mask=mask)

        # Mở ảnh nền chào mừng
        background = Image.open("welcome_template.png").convert("RGBA")
        background.paste(avatar_circle, (50, 50), avatar_circle)  # Dán avatar lên

        # Ghi tên người dùng
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("antonio.ttf", 28)  # Bạn có thể thay font
        draw.text((220, 80), f"Welcome {member.name}!", font=font, fill=(255, 255, 255))

        # Xuất ảnh kết quả
        output = BytesIO()
        background.save(output, format="PNG")
        output.seek(0)

        # Gửi ảnh chào mừng vào kênh tên "welcome"
        channel = discord.utils.get(member.guild.text_channels, name="welcome")
        if channel:
            await channel.send(
                content=f"🎉 Welcome {member.mention} to **{member.guild.name}**!",
                file=discord.File(output, "welcome.png")
            )
        else:
            print("⚠️ Không tìm thấy kênh #welcome")
    except Exception as e:
        print(f"❌ Lỗi khi gửi ảnh chào mừng: {e}")

bot.run(os.getenv("BOT_TOKEN"))
