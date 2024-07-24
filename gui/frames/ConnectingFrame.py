from tkinter import Frame, Label, HORIZONTAL
from tkinter.ttk import Progressbar


class BluetoothConnectingFrame(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.label = Label(master=self, text="Connecting to Bluetooth Devices...")
        self.label.pack()

        self.progress_bar = Progressbar(master=self, orient=HORIZONTAL, mode='indeterminate')
        self.progress_bar.pack()

    def stop(self):
        self.progress_bar.stop()
        self.progress_bar.destroy()
        self.label.destroy()
        self.destroy()
