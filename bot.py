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
async def declaration(interaction: dc.Interaction, players: int):
    paginator = DeclarationPaginator(players)
    await paginator.send(interaction)

client.run(os.getenv('TOKEN'))
