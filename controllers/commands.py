import discord
from controllers import linkController
from os import path
class CommandsController():
    def __init__(self):
        self._cmdList = {
            "update": self.updateFunc,
            "list"  : self.listFunc,
            "save"  : self.saveFunc,
            "add"   : self.addFunc,
            "del"   : self.delFunc
        }

    @property
    def valid_commands(self):
        return self._cmdList.keys()

    @classmethod
    async def attempt_command(self, ctx, args, command):
        result = False
        cID = None
        cName = None
        try:
            result, cId, cName = await command(ctx, args)
        except KeyError:
            await ctx.channel.send("I don't have any data on that channel ID")
        except:
            await ctx.channel.send("AN ERROR OCCURED")
        return result, cID, cName
    
    async def updateFunc(self, ctx, args, kwargs):
        controller = kwargs["controller"]
        result, cID, cName = await self.attempt_command(ctx, args, controller.link_updater)
        if result: #Check if true
            await ctx.channel.send(f"Updated the link for {cName} ({cId})")

    async def listFunc(self, ctx, args, kwargs):
        controller = kwargs["controller"]
        msg = await controller.list_links(ctx, args)
        await ctx.channel.send(embed=msg)

    async def addFunc(self, ctx, args, kwargs):
        controller = kwargs["controller"]
        msg = await controller.link_add(ctx, args)
        await ctx.channel.send(embed=msg)

    async def delFunc(self, ctx, args, kwargs):
        controller = kwargs["controller"]
        client = kwargs["client"]
        msg = await controller.link_del(ctx, args, client)
        await ctx.channel.send(embed=msg)
    
    async def saveFunc(self, ctx, args, kwargs):
        fileName = discord.File(path.join("models", "classes.json"), filename="classes.json")
        dTime = 25 #Time until message is deleted in seconds
        
        msg = "I currently have the following classes in memory.\n"\
        f"This msg will self destruct in {dTime} seconds"
        await ctx.channel.send(msg, file=fileName, delete_after=dTime)


    async def invalidCommand(self, ctx, args, kwargs):
        msg = f"Invalid command. Valid commands are:\n"
        print(self.valid_commands)
        for cmd in self.valid_commands:
            print(cmd)
            msg = msg + f"\t\t!{cmd}\n"
        await ctx.channel.send(msg)
    
    async def exec(self, ctx, command, args, **kwargs):
        func = self._cmdList.get(command, self.invalidCommand)
        await func(ctx, args, kwargs)
        
    