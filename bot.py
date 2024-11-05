import os
from datetime import date
import re

from dotenv import load_dotenv
import discord as dc


load_dotenv()

intents = dc.Intents().default()
testing_guild = 868754530639171594
client = dc.Client(debug_guilds=[testing_guild,], intents=intents)
tree = dc.app_commands.CommandTree(client)

class DeclarationModal(dc.ui.Modal, title="Uzupełnij deklarkę"):
    def parse_points(self, points: str) -> str:
        points_description = "- PU:\n"
        pattern = r"^\"(.*)\"[ \t]*(0\.[0-9]+)$"
        for line in points.splitlines():
            match_object = re.fullmatch(pattern, line)
            if match_object is None:
                raise ValueError((
                    "**Nie udało się wysłać deklarki**\n\n"
                    "Każda linijka w liście graczy powinna składać "
                    "się z nazwy postaci "
                    "wziętej w cudzysłowie (np \"Brimm Schadenfreude\"), "
                    "odstępu, a potem liczby PU. "
                    "Liczba PU powinna być zapisana jako ułamek dziesiętny "
                    "większa od 0 i mniejsza od 1.0, np 0.45.\n\n"
                    "Przykład poprawnej linijki:\n"
                    "\"Brimm Schadenfreude\" 0.45"
                ))
            nickname = match_object[1]
            points_number = match_object[2]
            points_description += f"\t- {nickname}: {points_number}\n"
        return points_description
    
    def create_declaration(self, name: str, places: str, logs: str,
                           description: str, points: str) -> str:
        current_date = date.today().isoformat()
        points_description = self.parse_points(points)
        declaration = ("```md\n"
                       f"### {current_date}, {name}\n"
                       f"*Lokalizacje: {places}*\n\n"
                       f"Logi: {logs}\n"
                       f"> {description}\n\n"
                       f"{points_description}\n"
                       "```"
        )
        return declaration
        
    name = dc.ui.TextInput(label="Tytuł deklarki",
                            placeholder="Zwykły dzień w Forcie Eder",
                            max_length=100)
    places = dc.ui.TextInput(label="Lokalizacje",
                             placeholder="Fort Eder, Fortyfikacja p.1",
                             max_length=100)
    logs = dc.ui.TextInput(label="Link do logów",
                           placeholder="najlepiej skorzystać z pastebina",
                           max_length=100)
    description = dc.ui.TextInput(label="Opis",
                                  style=dc.TextStyle.long,
                                  placeholder=(
                                    "Anward zwyzywał wory z Fortu"
                                    "oraz popodglądał sparing Rose i Brimm."
                                    ),
                                  max_length=1550)
    points = dc.ui.TextInput(label=(
                                "Lista graczy i sugestia"
                                "ile powinni dostać PU"
                                ),
                             style=dc.TextStyle.long,
                             placeholder=(
                                        "\"Anward\" 0.2\n"
                                        "\"Velrose\" 0.3\n"
                                        "\"Brimm Schadenfreude\" 0.3"))

    async def on_submit(self, interaction: dc.Interaction) -> None:
        declaration = self.create_declaration(self.name.value,
                                              self.places.value,
                                              self.logs.value,
                                              self.description.value,
                                              self.points.value)
        await interaction.response.send_message(declaration)

    async def on_error(self, interaction: dc.Interaction,
                       error: Exception) -> None:
        await interaction.response.send_message(str(error), ephemeral=True)

@client.event
async def on_ready():
    await tree.sync()
    print(f"{client.user} is ready and online!")

@tree.command(
    name="send_declaration",
    description="Stwórz i wyślij deklarkę. Trafi na ten kanał i specjalny kanał Rady."
)
async def send_declaration(interaction: dc.Interaction):
    modal = DeclarationModal()
    await interaction.response.send_modal(modal)


client.run(os.getenv('TOKEN'))
