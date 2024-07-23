from tkinter import Tk, Frame, Button, Label, Listbox, MULTIPLE


class CyclingFrame(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

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