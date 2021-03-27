import discord
import os
from dotenv import load_dotenv
load_dotenv() #Loads .env variables from the same directory
from controllers.commands import CommandsController
from controllers.linkProvider import LinkController
from models.linkInfo import LinkInfo

#Private variables
CLIENT_KEY = os.getenv("CLIENT_KEY")

#Public variables
timeZone = "US/Pacific"
emoji = ":WaitWhat:754104719554772994" #Wait What

#Start the Discord Client
client = discord.Client()


#Load the class information to memory
link_controller = LinkController('models\classes.json', timeZone)
cmd = CommandsController()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    """
    On a message begin processing the request
    """
    if message.author == client.user:
        return #To avoid responding to itself
    pure_content = message.content.strip().lower()

    if "tyty" in pure_content \
    or "ty ty" in pure_content \
    or "ok ty" in pure_content \
    or "thanks ty" in pure_content:
        await message.add_reaction(emoji) #Gotta add them emotes first
    
    if "link pl" in pure_content:
        await link_controller.link_provider(message, pure_content)
    
    elif pure_content.startswith('!') and message.author.id == 190974605895270400: ####REMOVE THIS! CHECKS TO SEE IF AUTHOR IS UNKNOWN
        text = pure_content[1:].split(' ')
        command = text[0]
        args = tuple(text[1:])
        if len(command) > 0:
            await cmd.exec(message, command, args)



client.run(CLIENT_KEY)