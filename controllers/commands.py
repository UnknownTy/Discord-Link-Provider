import discord
class CommandsController():
    def __init__(self):
        self._cmdList = {
            "test": self.testFunc
        }
    async def testFunc(self, a,b, *args):
        print("TEST FUNCTION WENT THROUGH")

    async def invalidCommand(self, a,b, *args):
        print("TEST FUNCTION FAILED")

    async def exec(self, message, command, *args):
        await self._cmdList.get(command, self.invalidCommand)(message, args)
    