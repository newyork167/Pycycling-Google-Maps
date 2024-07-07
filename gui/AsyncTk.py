import asyncio

from tkinter import Tk
from tortoise import Tortoise


class AsyncTk(Tk):
    "Basic Tk with an asyncio-compatible event loop"
    def __init__(self):
        super().__init__()
        self.running = True
        self.runners = [self.tk_loop()]
        self.button_presses = []

    async def tk_loop(self):
        "asyncio 'compatible' tk event loop?"
        # Is there a better way to trigger loop exit than using a state vrbl?
        while self.running:
            self.update()
            await asyncio.sleep(0.05) # obviously, sleep time could be parameterized
            if len(self.button_presses) > 0:
                await self.button_presses.pop(0)
        await Tortoise.close_connections()

    def stop(self):
        self.running = False

    async def run(self):
        await asyncio.gather(*self.runners)

    def add_button_coro(self, coro):
        print(f"Adding button press: {coro}")
        task = asyncio.create_task(coro)
        self.button_presses.append(task)