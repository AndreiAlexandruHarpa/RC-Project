from tkinter import *
import tkinter as tk


class GUI:
    def __init__(self, guiObject):
        leftframe1 = Frame(guiObject)
        leftframe1.pack(side=LEFT)
        leftframe2 = Frame(guiObject)
        leftframe2.pack(side=LEFT)
        bottomframe = Frame(guiObject)
        bottomframe.pack(side=BOTTOM)
        rightframe = Frame(guiObject)
        rightframe.pack(side=RIGHT)

        option1 = IntVar()
        option2 = IntVar()
        option3 = IntVar()
        option4 = IntVar()
        option5 = IntVar()
        option6 = IntVar()
        option7 = IntVar()
        option8 = IntVar()
        option9 = IntVar()
        option10 = IntVar()

        go = Button(bottomframe, text="GO")
        O1 = Checkbutton(leftframe1, text="Option 1", variable=option1, onvalue=1, offvalue=0, height=2, width=6)
        O2 = Checkbutton(leftframe1, text="Option 2", variable=option2, onvalue=1, offvalue=0, height=2, width=6)
        O3 = Checkbutton(leftframe1, text="Option 3", variable=option3, onvalue=1, offvalue=0, height=2, width=6)
        O4 = Checkbutton(leftframe1, text="Option 4", variable=option4, onvalue=1, offvalue=0, height=2, width=6)
        O5 = Checkbutton(leftframe1, text="Option 5", variable=option5, onvalue=1, offvalue=0, height=2, width=6)
        O6 = Checkbutton(leftframe2, text="Option 6", variable=option6, onvalue=1, offvalue=0, height=2, width=6)
        O7 = Checkbutton(leftframe2, text="Option 7", variable=option7, onvalue=1, offvalue=0, height=2, width=6)
        O8 = Checkbutton(leftframe2, text="Option 8", variable=option8, onvalue=1, offvalue=0, height=2, width=6)
        O9 = Checkbutton(leftframe2, text="Option 9", variable=option9, onvalue=1, offvalue=0, height=2, width=6)
        O10 = Checkbutton(leftframe2, text="Option 10", variable=option10, onvalue=1, offvalue=0, height=2, width=6)

        text = Text(rightframe)

        text.insert(INSERT, "TESTTTTTTTTT")

        O1.pack()
        O2.pack()
        O3.pack()
        O4.pack()
        O5.pack()
        O6.pack()
        O7.pack()
        O8.pack()
        O9.pack()
        O10.pack()
        text.pack(side=RIGHT)
        go.pack(side=BOTTOM)
