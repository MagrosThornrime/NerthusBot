import os

from dotenv import load_dotenv
import discord as dc

from declarations import DeclarationPaginator

load_dotenv()

intents = dc.Intents().default()
testing_guild = 868754530639171594
client = dc.Client(debug_guilds=[testing_guild,], intents=intents)
tree = dc.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"{client.user} is ready and online!")

@tree.command(
    name="declaration",
    description="Stwórz i wyślij deklarkę. Trafi na ten kanał i specjalny kanał Rady."
)
@dc.app_commands.describe(players="Liczba graczy")
@dc.app_commands.describe(screenshot="Screenshot z gry")
async def declaration(interaction: dc.Interaction, players: int,
                      screenshot: dc.Attachment):
    paginator = DeclarationPaginator(players, screenshot)
    await paginator.send(interaction, ephemeral=True)

client.run(os.getenv('TOKEN'))
