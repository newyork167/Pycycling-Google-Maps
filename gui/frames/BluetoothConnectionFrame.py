from tkinter import Tk, Frame, Button, Label, Listbox, MULTIPLE, END, SINGLE

from training_plans.test_plan import TestPlan


class BluetoothConnectionFrame(Frame):
    cycling_bluetooth_selector_box = None
    bluetooth_devices = []

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        Label(master=self, text="Select Cycling Bluetooth Device:").pack()

        self.cycling_bluetooth_selector_box = Listbox(
            exportselection=0,
            master=self,
            selectmode=SINGLE,
            height=10,
            width=50)
        self.cycling_bluetooth_selector_box.pack()

        Label(master=self, text="Select HR Bluetooth Device:").pack()
        self.hr_bluetooth_selector_box = Listbox(
            exportselection=0,
            master=self,
            selectmode=SINGLE,
            height=10,
            width=50)
        self.hr_bluetooth_selector_box.pack()

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
            self.bluetooth_devices.append(device)
            self.cycling_bluetooth_selector_box.insert(END, device.name)
            self.hr_bluetooth_selector_box.insert(END, device.name)