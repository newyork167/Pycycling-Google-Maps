from tkinter import Frame, Button, Label, Listbox, END, SINGLE


class BluetoothConnectionFrame(Frame):
    cycling_bluetooth_selector_box = None
    bluetooth_devices = []

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        Label(master=self, text="Select Cycling Bluetooth Device:").grid(row=0, column=0)

        self.cycling_bluetooth_selector_box = Listbox(
            exportselection=0,
            master=self,
            selectmode=SINGLE,
            height=10,
            width=50)
        self.cycling_bluetooth_selector_box.grid(row=1, column=0, sticky="nsew")

        Label(master=self, text="Select HR Bluetooth Device:").grid(row=2, column=0)
        self.hr_bluetooth_selector_box = Listbox(
            exportselection=0,
            master=self,
            selectmode=SINGLE,
            height=10,
            width=50)
        self.hr_bluetooth_selector_box.grid(row=3, column=0, sticky="nsew")

        Button(master=self,
               text="START!",
               width=25,
               height=5,
               command=lambda: controller.start_cycling()
               ).grid(row=4, column=0, sticky="nsew")

        Button(master=self,
               text="TEST!",
               width=25,
               height=5,
               command=lambda: controller.start_test()
               ).grid(row=5, column=0, sticky="nsew")

        Button(master=self,
               text='Quit',
               command=controller.stop
               ).grid(row=6, column=0, sticky="nsew")

    def bluetooth_notification_received(self, devices):
        for device in devices:
            self.bluetooth_devices.append(device)
            self.cycling_bluetooth_selector_box.insert(END, device.name)
            self.hr_bluetooth_selector_box.insert(END, device.name)