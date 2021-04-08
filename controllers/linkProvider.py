import discord
from pytz import timezone
from datetime import datetime
from models.linkInfo import LinkInfo
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

        :param comp_time: [The time of day to be set as the base for the range]
        :type comp_time: [str] as formated H:M

        :param comp_day: [The day to compare against]
        :type comp_day: [str]

        :return: [True if current time is in range, false otherwise]
        :rtype: [bool]
        """
        day = datetime.now(tz=self._timeZone).strftime("%A") #Current Day
        now = datetime.now(tz=self._timeZone)
        if comp_day == day: #First check if today matches the day to save computation time
            comp_time = list(map(int, comp_time))
            timeToCompB = now.replace(hour=(comp_time[0]-1), minute=comp_time[1], second=0, microsecond=0)
            timeToCompA = now.replace(hour=(comp_time[0]+2), minute=comp_time[1], second=0, microsecond=0)
            if now < timeToCompA and now > timeToCompB:
                return True #Return true if within range
        
        return False #False otherwise

    async def link_updater(self, ctx, args):
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

        :param ctx: [Context - The message the started the request]
        :type ctx: [MESSAGE]
        :param content: [The content of the message that began the request]
        :type content: [str]
        """

        classes = await self.get_classes(ctx.channel.id)
        if classes:
            if content == "link pleb": #An exception for those who are rude.
                await ctx.channel.send("Dude. Rude.")

            none=True #By default assumes we find none
            for class_ in classes:
                #For each link in the list check if in range of start time.

                if self.compare_time(class_.time.split(":"), class_.day):
                    time = datetime.now(tz=self._timeZone).strftime("%H:%M:%S") #Current time
                    #Respond with the link
                    await ctx.channel.send(
                        f"It's currently {time}. Time for {class_.name}!\n"\
                        f"Class begins at {class_.time}\n{class_.url}")

                    none = False
                    break

            if none:
                #If no classes are in range, let the requester know
                await ctx.channel.send("I don't believe there's any classes right now.")