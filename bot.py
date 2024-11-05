import os
from datetime import date
import re

from dotenv import load_dotenv
import discord as dc
from discord.ext.modal_paginator import ModalPaginator, PaginatorModal


load_dotenv()

intents = dc.Intents().default()
testing_guild = 868754530639171594
client = dc.Client(debug_guilds=[testing_guild,], intents=intents)
tree = dc.app_commands.CommandTree(client)

class DeclarationPaginator(ModalPaginator):
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
        # points_description = self.parse_points(points)
        points_description = "\n".join([f"\t- {nick}" for nick in points])
        declaration = ("```md\n"
                       f"### {current_date}, {name}\n"
                       f"*Lokalizacje: {places}*\n\n"
                       f"Logi: {logs}\n"
                       f"> {description}\n\n"
                       f"{points_description}\n"
                       "```"
        )
        return declaration

    def create_main_modal(self) -> PaginatorModal:
        modal = PaginatorModal(title="Uzupełnij deklarkę")
        modal.add_input(
            label="Tytuł deklarki",
            placeholder="Zwykły dzień w Forcie Eder",
            max_length=100
        )
        modal.add_input(
            label="Lokalizacje",
            placeholder="Fort Eder, Fortyfikacja p.1",
            max_length=100
        )
        modal.add_input(
            label="Link do logów",
            placeholder="najlepiej skorzystać z pastebina",
            max_length=100
        )
        modal.add_input(
            label="Opis",
            style=dc.TextStyle.long,
            placeholder=(
                "Anward zwyzywał wory z Fortu"
                "oraz popodglądał sparing Rose i Brimm."
            ),
            max_length=1400
        )
        return modal

    def create_players_modal(self, first_player: int, rows: int) -> PaginatorModal:
        modal = PaginatorModal(title="Dodaj graczy")
        for row in range(rows):
            modal.add_input(
                label=f"Gracz nr {first_player + row}",
                max_length=30
            )
        return modal

    def __init__(self, players: int):
        super().__init__()
        if players <= 0:
            raise ValueError("Musi być conajmniej jeden gracz")
        if players > 16:
            raise ValueError("Ale że aż tyle graczy?")
        self.add_modal(self.create_main_modal())
        for i in range(0, players, 5):
            modal = self.create_players_modal(i, min(players - i, 5))
            self.add_modal(modal)

    async def on_finish(self, interaction: dc.Interaction) -> None:
        players = []
        main_modal = self.modals[0]
        name = main_modal.children[0].value
        places = main_modal.children[1].value
        logs = main_modal.children[2].value
        description = main_modal.children[3].value
        for modal in self.modals[1:]:
            for field in modal.children:
                players.append(field.value)
        declaration = self.create_declaration(name, places, logs,
                                              description, players)
        await interaction.response.send_message(declaration)

@client.event
async def on_ready():
    await tree.sync()
    print(f"{client.user} is ready and online!")

@tree.command(
    name="declaration",
    description="Stwórz i wyślij deklarkę. Trafi na ten kanał i specjalny kanał Rady."
)
@dc.app_commands.describe(players="Liczba graczy")
async def declaration(interaction: dc.Interaction, players: int):
    paginator = DeclarationPaginator(players)
    await paginator.send(interaction)

client.run(os.getenv('TOKEN'))
