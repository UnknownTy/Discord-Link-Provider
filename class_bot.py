import discord
import json
from dotenv import load_dotenv
load_dotenv() #Loads .env variables from the same directory
import os
from datetime import datetime
from pytz import timezone

#Private variables
CLIENT_KEY = os.getenv("CLIENT_KEY")

#Public variables
timeZone = timezone("US/Pacific")

class LinkInfo():
    """
    Stores information on class links. 
    Data can be loaded via a JSON File using `.read_from_json`

    Args:
        name_ (str): The class' name
        link_ (str): Zoom (or other) link for the class
        day_ (str): What day the class takes place
        time_ (str): What time the class starts (Format as HH:MM 24hr)
    """
    @staticmethod
    def read_from_json(filepath) -> dict:
        """
        Load class data from a JSON file. See reference file for formatting

        Args:
            filepath (str): Path to the JSON file

        Returns:
            dict: Dictionary of all sets' class information
        """
        complete_list = []
        with open(filepath) as json_file:
            json_data = json.loads(json_file.read())
        for set_ in json_data:
            tmp_dict = {}
            tmp_list = []
            tmp_dict["set"] = set_["set"]
            for class_ in set_["classes"]:
                tmp_list.append(LinkInfo(
                    class_["name"],
                    class_["link"],
                    class_["day"],
                    class_["time"],
                ))
            tmp_dict["classes"] = tmp_list
            complete_list.append(tmp_dict)

        return complete_list

    def __init__(self, name_, link_, day_, time_):
        self.name = name_
        self.url = link_
        self.day = day_
        self.time = time_

#Load the class information to memory
classLinks = LinkInfo.read_from_json("./classes.json") 

#Start the Discord Client
client = discord.Client()

#The emoji that the bot reacts to tyty messages with
emoji = ":WaitWhat:754104719554772994" #Wait What

def compare_time(comp_time, comp_day) -> bool:
    """
    Compares the time given to the current day

    :param comp_time: [The time of day to be set as the base for the range]
    :type comp_time: [str] as formated H:M

    :param comp_day: [The day to compare against]
    :type comp_day: [str]

    :return: [True if current time is in range, false otherwise]
    :rtype: [bool]
    """
    day = datetime.now(tz=timeZone).strftime("%A") #Current Day
    now = datetime.now(tz=timeZone)
    if comp_day == day: #First check if today matches the day to save computation time
        comp_time = list(map(int, comp_time))
        timeToCompB = now.replace(hour=(comp_time[0]-1), minute=comp_time[1], second=0, microsecond=0)
        timeToCompA = now.replace(hour=(comp_time[0]+2), minute=comp_time[1], second=0, microsecond=0)
        if now < timeToCompA and now > timeToCompB:
            return True #Return true if within range
    
    return False #False otherwise

async def link_provider(ctx, content):
    """
    Provides a zoom link for a speicific class when asked
    Gotta ask politely, with the exception for 'pleb'

    :param ctx: [Context - The message the started the request]
    :type ctx: [MESSAGE]
    :param content: [The content of the message that began the request]
    :type content: [str]
    """
    if "link pl".lower() in content:
        for set_ in classLinks:
            if ctx.channel.id == set_["set"]:
                if content == "link pleb": #An exception for those who are rude.
                    await ctx.channel.send("Dude. Rude.")

                none=True #By default assumes we find none
                for link in set_["classes"]:
                    #For each link in the list check if in range of start time.

                    if compare_time(link.time.split(":"), link.day):
                        time = datetime.now(tz=timeZone).strftime("%H:%M:%S") #Current time
                        #Respond with the link
                        await ctx.channel.send(
                            f"It's currently {time}. Time for {link.name}!\n"\
                            f"Class begins at {link.time}\n{link.url}")

                        none = False
                        break

                if none:
                    #If no classes are in range, let the requester know
                    await ctx.channel.send("I don't believe there's any classes right now.")

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    """
    On a message begin processing the request
    """
    if message.author == client.user:
        return
    pure_content = message.content.strip().lower()

    if "tyty" in pure_content \
    or "ty ty" in pure_content \
    or "ok ty" in pure_content \
    or "thanks ty" in pure_content:
        await message.add_reaction(emoji)
    
    await link_provider(message, pure_content)
                    

client.run(CLIENT_KEY)
