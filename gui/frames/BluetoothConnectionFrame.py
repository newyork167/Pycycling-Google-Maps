from tkinter import Tk, Frame, Button, Label, Listbox, MULTIPLE, END

from training_plans.test_plan import TestPlan


class BluetoothConnectionFrame(Frame):
    bluetooth_selector_box = None

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        Label(master=self, text="Select Bluetooth Devices:").pack()

        self.bluetooth_selector_box = Listbox(
            master=self, selectmode=MULTIPLE, height=10, width=50)
        self.bluetooth_selector_box.pack()

        # Don't need references to these
        Button(master=self,
               text="Get Test Plan!",
               width=25,

               height=5,
               command=lambda: controller.add_button_coro(TestPlan.generate())
               ).pack()

        Button(master=self,
               text="START!",
               width=25,

               height=5,
               command=lambda: controller.start_cycling()
               ).pack()

        Button(master=self,
               text='Quit',
               command=controller.stop
               ).pack()

    def bluetooth_notification_received(self, devices):
        for device in devices:
            self.bluetooth_selector_box.insert(END, device.name)