import discord
class CommandsController():
    def __init__(self):
        self._cmdList = {
            "test": self.testFunc,
            "repeat": self.repeatFunc
        }

    @property
    def valid_commands(self):
        return self._cmdList.keys()
    
    async def testFunc(self, ctx, args):
        await ctx.channel.send(f"This is the test command.\nArgs:{args}")

    async def repeatFunc(self, ctx, args):
        msg = "This command repeats back your message\n\t"
        if len(args) > 0:
            msg = msg + (' '.join(args).capitalize())
        else:
            msg = msg + 'N/A'
        await ctx.channel.send(msg)

    async def invalidCommand(self, ctx, args):
        msg = f"Invalid command. Valid commands are:\n"
        print(self.valid_commands)
        for cmd in self.valid_commands:
            print(cmd)
            msg = msg + f"\t\t!{cmd}\n"
        await ctx.channel.send(msg)

    async def exec(self, ctx, command, args):
        await self._cmdList.get(command, self.invalidCommand)(ctx, args)
    