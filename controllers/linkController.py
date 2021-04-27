import discord
from pytz import timezone
from datetime import datetime
from models.linkInfo import LinkInfo
import asyncio
class LinkController():
    def __init__(self, links_path, tz_):
        self._links_path = links_path
        self._links = LinkInfo.read_from_json(links_path)
        self._timeZone = timezone(tz_)


    async def get_classes(self, id):
        return self._links.get(id, False)

    def compare_time(self, comp_time, comp_day) -> bool:
        """
        Compares the time given to the current day

        :param comp_time: The time of day to be set as the base for the range
        :type comp_time: str as formated H:M

        :param comp_day: The day to compare against
        :type comp_day: str

        :return: True if current time is in range, false otherwise
        :rtype: bool
        """
        day = datetime.now(tz=self._timeZone).strftime("%A") #Current Day
        now = datetime.now(tz=self._timeZone)
        if day in comp_day: #First check if today matches the day to save computation time
            comp_time = list(map(int, comp_time))
            timeToCompB = now.replace(hour=(comp_time[0]-1), minute=comp_time[1], second=0, microsecond=0)
            timeToCompA = now.replace(hour=(comp_time[0]+2), minute=comp_time[1], second=0, microsecond=0)
            if now < timeToCompA and now > timeToCompB:
                return True #Return true if within range
        
        return False #False otherwise

    async def list_links(self, ctx, args):
        """
        Lists the links available in an embedded format

        :param ctx: Context - The message the started the request
        :type ctx: MESSAGE

        :param args: Arguments provided
        :type args: list

        :raises ValueError: If the set provided in args does not exist

        :return: An embed of the list of classes
        :rtype: embed
        """
        if len(args) > 0:
            set_ = int(args[0])
        else:
            set_ = ctx.channel.id
        if not set_:
            raise ValueError("No set by that ID")
        embed = discord.Embed(
            title= f"{set_} class list",
            description="A list of currently available classes, and their IDs",
            color = 16316171
            )
        for class_ in self._links[set_]:
            embed.add_field(
                name= class_.name,
                value= class_.id,
                inline= True
            )
        return embed

    async def link_updater(self, ctx, args):
        """
        Updates a link for a given class. Class identified by ID

        :param ctx: Context - The message the started the request
        :type ctx: MESSAGE

        :param args: Arguments provided
        :type args: list

        :return: Result, the classes ID, the classes name
        :rtype: tuple (Bool, int, str)
        """
        if len(args) < 2 or len(args) > 3:
            return False, None, None
        id = int(args[0])
        link = args[1]
        if len(args) == 2:
            set = ctx.channel.id
        elif len(args) == 3:
            set = int(args[2])
        try:
            for class_ in self._links[set]:
                if class_.id == id:
                    class_.url = link
                    LinkInfo.save_to_json(self._links_path, self._links)
                    return True, class_.id, class_.name
        except KeyError:
            return False, None, None


    async def link_provider(self, ctx, content):
        """
        Provides a zoom link for a speicific class when asked
        Gotta ask politely, with the exception for 'pleb'

        :param ctx: Context - The message the started the request
        :type ctx: MESSAGE

        :param content: The content of the message that began the request
        :type content: str
        """
        classes = await self.get_classes(ctx.channel.id)
        if classes:
            if content == "link pleb": #An exception for those who are rude.
                await ctx.channel.send("Dude. Rude.")

            none=True #By default assumes we find none
            for class_ in classes:
                #For each link in the list check if in range of start time.

                if self.compare_time(class_.time.split(":"), class_.day.split(",")):
                    time = datetime.now(tz=self._timeZone).strftime("%H:%M:%S") #Current time
                    embed = discord.Embed(
                        title= f"Time for {class_.name}",
                        colour=  0xF1C40F,
                        url= class_.url
                        )
                    embed.add_field(
                        name="Start:",
                        value=f"It's currently {time}. Class begins at {class_.time}")
                    #Respond with the link
                    await ctx.channel.send(embed=embed)
                    none = False
                    break

            if none:
                #If no classes are in range, let the requester know
                await ctx.channel.send("I don't believe there's any classes right now.")


    async def link_add(self, ctx, args):
        """
        Adds a link to the bot's collection of classes

        :param ctx: Context - The message the started the request
        :type ctx: MESSAGE

        :param args: Arguments provided with the message
        :type args: list

        :return: An embed letting the user know if the class was added.
        :rtype: Embed
        """
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        complete = True
        embed = discord.Embed(
            title= f"Adding a new class",
            description="!add CLASS_NAME CLASS_LINK CLASS_TIME CLASS_DAY [SET_ID]",
        )

        ##Name checker
        if len(args) > 0:
            if args[0].startswith("\"") or args[0].startswith("'"):
                args[0] = args[0][1:]
                checkEnd = True
                for i in range(len(args)):
                    if args[i].endswith("\"") or args[i].endswith("'"):
                        checkEnd = False
                        args[i] = args[i][:-1]
                        args[0 : i+1] = [" ".join(args[0 : i+1])]
                        break
                if checkEnd:
                    embed.add_field(
                    name= "Name",
                    value= "Invalid name. Could not find end of string",
                    inline= False
                )
                    embed.set_footer(text="Failed")
                    embed.color = 0xa30721
                    return embed
        
        if len(args) < 4 or len(args) > 5:
            embed.add_field(
                name= "Unrecognized Arguments",
                value= "This command requires 4 arguments, with an optional 5th",
                inline= False
            )
            complete = False
            embed.set_footer(text="Failed")
            embed.color = 0xa30721
            return embed
        try:
            set_ = int(args[4])
        except IndexError:
            set_ = ctx.channel.id
        
        #Name
        name = args[0]
        embed.add_field(
                name= "Name",
                value= name,
                inline= True
            )
        
        ##Link checker
        if len(args[1]) < 15:
            complete = False
            embed.add_field(
                name= "Link",
                value= f"Invalid link: {args[1]}",
                inline= False
            )
        else:
            link = args[1]
            embed.add_field(
                name= "Link",
                value= link,
                inline= True
            )
        
        ##Time Checker
        time = args[2]
        try:
            checkTime = list(map(int, time.split(":")))
            if len(checkTime) != 2:
                raise ValueError("Invalid time")
            elif checkTime[0] < 0 or checkTime[0] > 23:
                raise ValueError("Invalid time")
            elif checkTime[1] < 0 or checkTime[1] > 59:
                raise ValueError("Invalid time")
            embed.add_field(
                name= "Time",
                value= time,
                inline= True
            )
        except ValueError:
            complete = False
            embed.add_field(
                name= "Time",
                value= f"Invalid time: {time}",
                inline= False
            )

        ##Day checker
        days = args[3].split(",")
        days = [x.capitalize() for x in days]
        for day in days:
            if day not in valid_days:
                complete = False
                embed.add_field(
                    name= "Day",
                    value= f"Invalid day: {day}",
                    inline= False
                )
        if complete:
            day = ",".join(days)
            embed.add_field(
                name= "Day",
                value= day,
                inline= True
            )
            embed.set_footer(text="Success")
            embed.color = 0x00ff2f
            try:
                id_ = len(self._links[set_]) + 1
                self._links[set_].append(LinkInfo(name, link, day, time, id_))
            except KeyError:
                id_ = 1
                self._links[set_] = [LinkInfo(name, link, day, time, id_)]
            embed.add_field(
                name= "ID",
                value= id_,
                inline= True
            )
            LinkInfo.save_to_json(self._links_path, self._links)
            return embed
        else:
            embed.color = 0xa30721
            embed.set_footer(text="Failed")
            return embed


    async def link_del(self, ctx, args, client):
        """
        Delete links from the bot's collection of classes

        :param ctx: Context - The message the started the request
        :type ctx: MESSAGE

        :param args: Arguments provided with the message
        :type args: list

        :param client: The bot client (For awaiting messages)
        :type client: Client

        :return: An embed with a response to the user's request
        :rtype: embed
        """
        embed = discord.Embed(
            title= f"Deleting a class",
            description="!del CLASS_ID [SET_ID]",
        )
        #Make sure the correct arguments are provided
        if len(args) < 1 or len(args) > 2:
            embed.color = 0xa30721
            embed.set_footer(text="Failed")
            return embed.add_field(name="Error", value="Invalid Arguments")
        id = int(args[0])

        try:
            set_ = int(args[1])
        except IndexError:
            set_ = ctx.channel.id

        def check(m):
            #Check the original author is the one to respond
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            for class_ in self._links[set_]:
                if class_.id == id:
                    try:
                        #Ask the user if they're sure they want to delete the speicific class
                        embed.add_field(name=class_.name, value=class_.id)
                        embed.add_field(name="Are you sure?", value="Reply Y to delete")
                        await ctx.channel.send(embed=embed, delete_after=9.99)

                        embed.clear_fields()
                        msg = await client.wait_for("message", timeout=10, check=check)
                    except asyncio.TimeoutError:
                        #User did not respond in time
                        embed.color = 0xa30721
                        embed.set_footer(text="Failed")
                        embed.add_field(name="Error", value="You didn't reply in time!")

                        return embed
                    else:
                        #Only require the first letter, as it's either a Y or not.
                        res = msg.content[0:1]
                        if res.lower() == "y":
                            self._links[set_].remove(class_)
                            if len(self._links[set_]) == 0:
                                del self._links[set_]
                            else:
                                for count, _class in enumerate(self._links[set_]):
                                    _class.id = count + 1
                            LinkInfo.save_to_json(self._links_path, self._links)

                            #Sucessfully deleted items, so send back success
                            embed.add_field(name=class_.name, value="Deleted")
                            embed.color = 0x00ff2f
                            embed.set_footer(text="Success")
                            return embed

                        else:
                            #User did not reply with a Y, so respond with a fail
                            embed.add_field(name=class_.name, value="Not Deleted")
                            embed.color = 0xa30721
                            embed.set_footer(text="Failed")
                            return embed

            raise ValueError #ID speicifed not in list
        except KeyError:
            #Could not find the speicied set, so respond with error
            embed.color = 0xa30721
            embed.set_footer(text="Failed")
            embed.add_field(name="Error", value=f"I don't info on set {set_}")
            return embed
        except ValueError:
            #Could not find the speicied ID, so respond with error
            embed.color = 0xa30721
            embed.set_footer(text="Failed")
            embed.add_field(name="Error", value=f"I don't have a class with the ID {id}")
            return embed