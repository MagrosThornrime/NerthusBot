import discord
import os # default module
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file

intents = discord.Intents.default()
# intents.members = True
bot = discord.Bot(debug_guilds=[868754530639171594,], intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.message_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext, message: discord.Message):
    await ctx.respond("Hey!")

bot.run(os.getenv('TOKEN')) # run the bot with the token