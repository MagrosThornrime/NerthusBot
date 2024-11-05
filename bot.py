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
        
        title = dc.ui.InputText(label="Tytuł deklarki", placeholder="Zwykły dzień w Forcie Eder", max_length=100)
        places = dc.ui.InputText(label="Lokalizacje", placeholder="Fort Eder, Fortyfikacja p.1", max_length=100)
        logs = dc.ui.InputText(label="Link do logów", placeholder="najlepiej skorzystać z pastebina", max_length=100)
        description = dc.ui.InputText(label="Opis", style=dc.InputTextStyle.long,
                                      placeholder="Anward zwyzywał wory z Fortu oraz popodglądał sparing Rose i Brimm.",
                                      max_length=1550)
        points = dc.ui.InputText(label="Lista graczy i sugestia ile powinni dostać PU", style=dc.InputTextStyle.long,
                                 placeholder="\"Anward\" 0.2\n\"Velrose\" 0.3\n\"Brimm Schadenfreude\" 0.3",
                                 max_length=350)
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

    
@bot.slash_command()
async def send_declaration(ctx: dc.ApplicationContext):
    """Stwórz i wyślij deklarkę. Trafi na ten kanał i specjalny kanał Rady."""
    modal = DeclariationModal(title="Uzupełnij deklarkę")
    await ctx.send_modal(modal)

bot.run(os.getenv('TOKEN'))
