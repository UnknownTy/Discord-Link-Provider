import discord
from controllers import linkProvider
class CommandsController():
    def __init__(self):
        self._cmdList = {
            "test": self.testFunc,
            "repeat": self.repeatFunc,
            "update": self.updateFunc,
            "list"  : self.listFunc
        }

    @property
    def valid_commands(self):
        return self._cmdList.keys()
    
    async def testFunc(self, ctx, args, c):
        await ctx.channel.send(f"This is the test command.\nArgs:{args}")

    async def repeatFunc(self, ctx, args, c):
        msg = "This command repeats back your message\n\t"
        if len(args) > 0:
            msg = msg + (' '.join(args).capitalize())
        else:
            msg = msg + 'N/A'
        await ctx.channel.send(msg)
    
    async def updateFunc(self, ctx, args, controller):
        try:
            result, cId, cName = await controller.link_updater(ctx, args)
        except KeyError:
            await ctx.channel.send("I don't have any data on that channel ID")
        except:
            await ctx.channel.send("AN ERROR OCCURED")
            result = False
        if result: #Check if true
            await ctx.channel.send(f"Updated the link for {cName} ({cId})")

    async def listFunc(self, ctx, args):
        pass

    async def invalidCommand(self, ctx, args, c):
        msg = f"Invalid command. Valid commands are:\n"
        print(self.valid_commands)
        for cmd in self.valid_commands:
            print(cmd)
            msg = msg + f"\t\t!{cmd}\n"
        await ctx.channel.send(msg)


    async def exec(self, ctx, command, args, controller=None):
        await self._cmdList.get(command, self.invalidCommand)(ctx, args, controller)
    