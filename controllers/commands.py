import discord
class CommandsController():
    def __init__(self):
        self._cmdList = {
            "test": self.testFunc,
            "repeat": self.repeatFunc
        }
    async def testFunc(self, ctx, args):
        await ctx.channel.send(f"This is the test command.\nArgs:{args}")

    async def repeatFunc(self, ctx, args):
        msg = "This command repeats back your message\n\t"
        if len(args) > 0:
            msg = msg + (' '.join(args).capitalize())
        else:
            msg = msg.join("N/A")
        await ctx.channel.send(msg)

    async def invalidCommand(self, ctx, args):
        await ctx.channel.send("Invalid command.")

    async def exec(self, ctx, command, args):
        await self._cmdList.get(command, self.invalidCommand)(ctx, args)
    