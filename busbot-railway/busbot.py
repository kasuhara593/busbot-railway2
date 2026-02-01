import os
import discord
from discord import app_commands


# ==================== ここだけ書き換える ====================
TOKEN = os.getenv("TOKEN")   # ← ここを変更！
LIST_CHANNEL_ID = 1467378072079827065
# ==========================================================

class BusBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()  # スラッシュコマンドを登録

client = BusBot()

@client.event
async def on_ready():
    print(f"✅ Bot 起動: {client.user}")

@client.tree.command(name="bus", description="車両番号からバスロケリンクを取得")
@app_commands.describe(number="例: 15-0658")
async def bus(interaction: discord.Interaction, number: str):

    channel = client.get_channel(LIST_CHANNEL_ID)

    if channel is None:
        await interaction.response.send_message(
            "❌ 車番リストチャンネルが見つかりません。\n"
            "・チャンネルID\n"
            "・ボットの権限\n"
            "をもう一度確認してください。",
            ephemeral=True
        )
        return

    found_info = None

    async for msg in channel.history(limit=2000):

        lines = msg.content.splitlines()

        for line in lines:
            text = line.strip()
            if not text:
                continue

            parts = text.split()

            # 「282 15-0658 井」形式を想定
            if len(parts) < 2:
                continue

            seiri_no = parts[0]       # ← これが“バスロケ用”
            official_no = parts[1]    # ← これが“公式車番”
            place = parts[2] if len(parts) >= 3 else ""

            if official_no == number:
                found_info = (seiri_no, official_no, place)
                break

        if found_info:
            break

    if not found_info:
        await interaction.response.send_message(
            f"❌ `{number}` はリストに見つかりませんでした。",
            ephemeral=True
        )
        return

    seiri_no, official_no, place = found_info

    # ★★★★ ここが“あなたの指摘どおり”に修正済み ★★★★
    url = (
        "https://oc.bus-vision.jp/osakacitybus/view/"
        f"mapApproachVehicle.html?siteConf=2&vehicleCorpCd=1&vehicleCd={seiri_no}"
    )

    embed = discord.Embed(
        title=f"🚍 {official_no}",
        description="大阪シティバス 位置情報",
        color=0x1E90FF
    )
    embed.add_field(name="バスロケURL", value=url, inline=False)
    embed.add_field(name="整理番号", value=seiri_no, inline=True)
    embed.add_field(name="所属", value=place if place else "不明", inline=True)

    await interaction.response.send_message(embed=embed)

client.run(TOKEN)
