from datetime import date
import random

import discord as dc
from discord.ext.modal_paginator import ModalPaginator, PaginatorModal, CustomButton


class OpenButton(CustomButton):
    def __init__(self) -> None:
        super().__init__(style=dc.ButtonStyle.gray, label="Uzupełnij dane", row=0)

    def on_optional_modal(self, button: dc.ui.Button[ModalPaginator]) -> None:
        button.style = dc.ButtonStyle.blurple

    def on_required_modal(self, button: dc.ui.Button[ModalPaginator]) -> None:
        button.style = dc.ButtonStyle.gray

class NextButton(CustomButton):
    def __init__(self) -> None:
        super().__init__(style=dc.ButtonStyle.green, label="Następny formularz", row=1)

class PreviousButton(CustomButton):
    def __init__(self) -> None:
        super().__init__(style=dc.ButtonStyle.green, label="Poprzedni formularz", row=1)

class CancelButton(CustomButton):
    def __init__(self) -> None:
        super().__init__(style=dc.ButtonStyle.red, label="Anuluj", row=2)

class FinishButton(CustomButton):
    def __init__(self) -> None:
        super().__init__(style=dc.ButtonStyle.green, label="Wyślij deklarkę", row=2)

class DeclarationPaginator(ModalPaginator):
    buttons = {
        "OPEN": OpenButton(),
        "NEXT": NextButton(),
        "PREVIOUS": PreviousButton(),
        "CANCEL": CancelButton(),
        "FINISH": FinishButton()
    }

    def parse_players(self, players: list[tuple[str]]) -> str:
        players_description = "- PU:\n"
        for player, points in players:
            players_description += f"\t- {player}: {points}\n"
        return players_description

    def create_declaration(self, name: str, places: str, logs: str,
                           description: str, players: list[tuple[str]]) -> str:
        current_date = date.today().isoformat()
        players_description = self.parse_players(players)
        declaration = ("```md\n"
                       f"### {current_date}, {name}\n"
                       f"*Lokalizacje: {places}*\n\n"
                       f"Logi: {logs}\n"
                       f"> {description}\n\n"
                       f"{players_description}\n"
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
                "Anward zwyzywał wory z Fortu "
                "oraz popodglądał sparing Rose i Brimm."
            ),
            max_length=1400
        )
        return modal

    def create_players_modal(self, first_player: int, rows: int) -> PaginatorModal:
        modal = PaginatorModal(title=f"Dodaj graczy - część {first_player // 2 + 1}")
        for row in range(rows):
            player_number = first_player + rows + 1
            modal.add_input(
                label=f"Nick gracza nr. {player_number}",
                max_length=30,
                placeholder=random.choice(("Velrose", "Anward", "Brimm Schadenfreude"))
            )
            modal.add_input(
                label=f"Sugerowana liczba PU dla gracza nr. {player_number}",
                max_length=5,
                placeholder=str(round(random.random(), 2))
            )
        return modal

    def __init__(self, players: int, screenshot: dc.Attachment):
        super().__init__(buttons=self.buttons)
        if players <= 0:
            raise ValueError("Musi być conajmniej jeden gracz")
        if players > 16:
            raise ValueError("Ale że aż tyle graczy?")
        self.screenshot = screenshot
        self.add_modal(self.create_main_modal())
        for i in range(0, players, 2):
            modal = self.create_players_modal(i, min(players - i, 2))
            self.add_modal(modal)

    async def on_finish(self, interaction: dc.Interaction) -> None:
        players = []
        main_modal = self.modals[0]
        name = main_modal.children[0].value
        places = main_modal.children[1].value
        logs = main_modal.children[2].value
        description = main_modal.children[3].value
        for modal in self.modals[1:]:
            player = ""
            for index, field in enumerate(modal.children):
                if index % 2 == 0:
                    player = field.value
                else:
                    points = field.value
                    players.append((player, points))
        declaration = self.create_declaration(name, places, logs,
                                              description, players)
        await interaction.response.send_message(declaration, file=await self.screenshot.to_file())