import os

from dotenv import load_dotenv
import discord as dc


load_dotenv()

intents = dc.Intents().default()
intents.message_content = True
testing_guild = 868754530639171594
bot = dc.Bot(debug_guilds=[testing_guild,], intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

def is_player_category(category: dc.CategoryChannel | None) -> bool:
    if category is None:
        return False
    name = str(category)
    if len(name) != 3:
        return False
    left = name[0].lower()
    middle = name[1].lower()
    right = name[2].lower()
    return left.isalpha() and right.isalpha() and left < right and middle == "-"

def get_player_channels(guild: dc.Guild) -> list[dc.abc.GuildChannel]:
    channels = []
    for category, category_channels in guild.by_category():
        if is_player_category(category):
            channels.extend(category_channels)
    return channels

async def send_to_other_players(channels: list[dc.abc.GuildChannel], message: dc.Message, player: str):
    for channel in channels:
        other_player = str(channel)
        if player == other_player:
            continue
        await channel.send(content=message.content, files=[await f.to_file() for f in message.attachments])


@bot.message_command(name="get category")
async def get_category(ctx: dc.ApplicationContext, message: dc.Message):
    channel = ctx.channel
    category = channel.category
    if is_player_category(category):
        await send_to_other_players(get_player_channels(ctx.guild), message, str(channel))
        await ctx.respond("Deklarka skopiowana")
    else:
        await ctx.respond("Nie możesz skopiować wiadomości na kanale innym niż kanał gracza")

bot.run(os.getenv('TOKEN'))
