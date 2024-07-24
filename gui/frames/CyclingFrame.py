from tkinter import Tk, Frame, Button, Label, Listbox, MULTIPLE


class CyclingFrame(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller

        self.cadence_label = Label(master=self, text='Cadence: ')
        self.cadence_label.grid(row=0, column=0, sticky="nsew")

        self.current_cadence_label = Label(master=self, text='0.0')
        self.current_cadence_label.grid(row=0, column=1, sticky="nsew")

        self.speed_label = Label(master=self, text='Speed: ')
        self.speed_label.grid(row=1, column=0, sticky="nsew")

        self.current_speed_label = Label(master=self, text='0.0')
        self.current_speed_label.grid(row=1, column=1, sticky="nsew")

        self.hr_label = Label(master=self, text='Heart Rate: ')
        self.hr_label.grid(row=2, column=0, sticky="nsew")

        self.current_hr_label = Label(master=self, text='0.0')
        self.current_hr_label.grid(row=2, column=1, sticky="nsew")

        self.resistance_label = Label(master=self, text='Resistance: ')
        self.resistance_label.grid(row=3, column=0, sticky="nsew")

        self.current_resistance_label = Label(master=self, text='0.0')
        self.current_resistance_label.grid(row=3, column=1, sticky="nsew")

    def training_update(self, cadence, speed, hr):
        self.current_cadence_label.config(text=cadence)
        self.current_speed_label.config(text=speed)
        self.current_hr_label.config(text=hr)

    def receive_hr_data(self, bpm):
        self.current_hr_label.config(text=bpm)
        self.update()  # Maybe come back and add decorators
        self.parent.update()

    def receive_cadence_data(self, cadence):
        self.current_cadence_label.config(text=cadence)
        self.update()
        self.parent.update()

    def receive_speed_data(self, speed):
        self.current_speed_label.config(text=speed)
        self.update()
        self.parent.update()

    def receive_resistance_data(self, resistance):
        self.current_resistance_label.config(text=resistance)
        self.update()
        self.parent.update()

