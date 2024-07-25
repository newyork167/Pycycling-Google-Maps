import asyncio

from tkinter import Tk, messagebox
from tortoise import Tortoise


class AsyncTk(Tk):
    def __init__(self):
        super().__init__()
        self.running = True
        self.runners = [self.tk_loop()]
        self.button_presses = []
        self.frames = []

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    async def tk_loop(self):
        while self.running:
            self.update()
            await asyncio.sleep(0.05)
            if len(self.button_presses) > 0:
                await self.button_presses.pop(0)
        await Tortoise.close_connections()

    def stop(self):
        self.running = False

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.stop()
            self.destroy()

    async def run(self):
        await asyncio.gather(*self.runners)

    def add_button_coro(self, coro):
        print(f"Adding button press: {coro}")
        task = asyncio.create_task(coro)
        self.button_presses.append(task)

    def show_frame(self, frame):
        frame.tkraise()
        self.update()

    async def async_show_frame(self, frame):
        frame.tkraise()
        self.update()

    def show_frame_at_index(self, cont):
        self.show_frame(self.frames[cont])