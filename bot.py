import os
from datetime import date
import re

from dotenv import load_dotenv
import discord as dc


load_dotenv()

intents = dc.Intents().default()
intents.message_content = True
testing_guild = 868754530639171594
bot = dc.Bot(debug_guilds=[testing_guild,], intents=intents)

class DeclariationModal(dc.ui.Modal):
    
    def parse_points(self, points: str) -> str:
        points_description = "- PU:\n"
        pattern = r"^\"(.*)\"[ \t]*(0\.[0-9]+)$"
        for line in points.splitlines():
            match_object = re.fullmatch(pattern, line)
            if match_object is None:
                raise ValueError("Wrong line")
            nickname = match_object[1]
            points_number = match_object[2]
            points_description += f"\t- {nickname}: {points_number}\n"
        return points_description
            
        
    
    def create_declaration(self, title: str, places: str, logs: str, description: str, points: str) -> str:
        current_date = date.today().isoformat()
        points_description = self.parse_points(points)
        declaration = f"```md\n### {current_date}, {title}\n*Lokalizacje: {places}*\n\
            \nLogi: {logs}\n> {description}\n\n{points_description}\n```"
        return declaration


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        title = dc.ui.InputText(label="Tytuł deklarki", placeholder="Zwykły dzień w Forcie Eder")
        places = dc.ui.InputText(label="Lokalizacje", placeholder="Fort Eder, Fortyfikacja p.1")
        logs = dc.ui.InputText(label="Link do logów", placeholder="najlepiej skorzystać z pastebina")
        description = dc.ui.InputText(label="Opis", style=dc.InputTextStyle.long,
                                      placeholder="Anward zwyzywał wory z Fortu oraz popodglądał sparing Rose i Brimm.")
        points = dc.ui.InputText(label="Lista graczy i sugestia ile powinni dostać PU", style=dc.InputTextStyle.long,
                                 placeholder="\"Anward\" 0.2\n\"Velrose\" 0.3\n\"Brimm Schadenfreude\" 0.3")
        for input_text in (title, places, logs, description, points):
            self.add_item(input_text)

    async def callback(self, interaction: dc.Interaction):
        title = self.children[0].value
        places = self.children[1].value
        logs = self.children[2].value
        description = self.children[3].value
        points = self.children[4].value
        declaration = self.create_declaration(title, places, logs, description, points)
        await interaction.response.send_message(declaration)

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

    
@bot.slash_command()
async def send_declaration(ctx: dc.ApplicationContext):
    """Shows an example of a modal dialog being invoked from a slash command."""
    modal = DeclariationModal(title="Uzupełnij deklarkę")
    await ctx.send_modal(modal)

@bot.message_command(name="Wyślij do pozostałych")
async def send_to_others(ctx: dc.ApplicationContext, message: dc.Message):
    channel = ctx.channel
    category = channel.category
    if is_player_category(category):
        await send_to_other_players(get_player_channels(ctx.guild), message, str(channel))
        await ctx.respond("Deklarka skopiowana")
    else:
        await ctx.respond("Nie możesz skopiować wiadomości na kanale innym niż kanał gracza")

bot.run(os.getenv('TOKEN'))
