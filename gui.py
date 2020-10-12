"""
Creates a front-end GUI for AnalyseThis.py
author: matta_idlecoder at protonmail dot com
"""
from tkinter import Tk, Frame, StringVar, IntVar
from tkinter import NORMAL, DISABLED, RAISED, END
from tkinter import Button, Radiobutton, Checkbutton
from tkinter import Toplevel, Entry, Label
import tkinter.constants, tkinter.filedialog
import tkinter.messagebox
import os
 
 
 
class PythonGUI(Frame):
    """The object space for creating your dashboard and launching your app
   """
    def __init__(self, root):
        """This is where you define & initialise all your GUI variables
        """
        Frame.__init__(self, root)
        self.master = root
        self.YourAppDashboard()
        return
 
 
    def YourAppDashboard(self):
        """The function that creates your dashboard and all its widgets
        """
        std_pos_opts = {'fill':tkinter.constants.BOTH, 'padx':10}
 
        BlankLine = ' ' * 80
 
        Button(self, textvariable=self.textstatus, font=('Helvetica', 16),
               command=self.GetNameOfTextToAnalyse,
               **self.std_button_opts).pack(pady=20, **std_pos_opts)
 
        Button(self, textvariable=self.StartTrigButtonName,
               command=self.GetStartTrig, **self.std_button_opts).pack(pady=5,
               **std_pos_opts)
 
        Button(self, textvariable=self.StopTrigButtonName,
               command=self.GetStopTrig, **self.std_button_opts).pack(pady=5,
               **std_pos_opts)
 
        Label(self, text=BlankLine).pack()
 
        Checkbutton(self, text="List proper nouns separately",
                    variable=self.IgnoreAndListPropers).pack(**std_pos_opts)
 
        Checkbutton(self, text='List contractions used',
                    variable=self.ListContractions).pack(**std_pos_opts)
 
        Checkbutton(self, text='List hyphenated compounds\nwords separately',
                    variable=self.SplitCompoundsAndList).pack(**std_pos_opts)
 
        Label(self, text=BlankLine).pack()
 
        Checkbutton(self, text='Do a spell check', variable=self.spellcheck,
                    command=self.onSpellCheck).pack(**std_pos_opts)
 
        self.SelectDictButton = Button(self, text=self.dictstatus,
               textvariable=self.dictstatus, command=self.GetNameOfDictToUse,
               state=NORMAL, **self.std_button_opts)
 
        self.SelectDictButton.pack(**std_pos_opts)
 
        Label(self, text=BlankLine).pack()
 
        Radiobutton(self, text='Sort word frequency analysis\nalphabetically by word',
                    variable=self.SortByAlpha, value=1).\
                    pack(**std_pos_opts)
 
        Radiobutton(self, text='Sort word frequency analysis\nby word frequencies',
                    variable=self.SortByAlpha, value=0).\
                    pack(**std_pos_opts)
 
        Button(self, text='Analyse', command=self.analyse_text, relief=RAISED,
               bd=4, padx=10, pady=5, font=('Helvetica', 16)).pack(padx=10, pady=10)
 
        Button(self, text='Quit', command=self.quit, relief=RAISED,
               bd=4, padx=10, pady=5, font=('Helvetica', 16)).pack(padx=5, pady=10)
        return
 



 

 
 
if __name__=='__main__':
    root = Tk()
 
    HalfScreenWidth = int(root.winfo_screenwidth()/2)
    HalfScreenHeight = int(root.winfo_screenheight()/2)
 
    w = HalfScreenWidth - 200
    h = HalfScreenHeight - 350
    # Centre window:
    geom_string = "+{}+{}".format(w, h)
 
    root.geometry(geom_string)
    root.title('VPN GUI')
    root.lift()
    PythonGUI(root).pack()
 
    root.mainloop()