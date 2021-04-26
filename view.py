from tkinter import *
from controller import Controller
from tkinter.scrolledtext import ScrolledText

# **********************************************************************************************************************
# **********************************************************************************************************************
# **********************************************************************************************************************

class Window(Tk):

    def __init__(self, *args, **kwargs):
        
        Tk.__init__(self, *args, **kwargs)

        self.title('News App')
        self.geometry('800x480')
        self.configure(bg='white')
        self.resizable(width=False, height=False)

        self.frames = {}
        self.mainContainer = Frame(self)
        self.mainContainer.grid_rowconfigure(0, weight=1)
        self.mainContainer.grid_columnconfigure(0, weight=1)
        self.mainContainer.pack(side="top", fill="both", expand = True)

        for frameClass in (ChatMenu,):

            frameInstance = frameClass(self.mainContainer, self.__changeWindowFrameTo, self.__closeWindow)

            frameInstance.grid(row=0, column=0, sticky="nsew")

            self.frames[frameClass] = frameInstance

        self.__changeWindowFrameTo(ChatMenu)

    def changeWindowFrameTo(self, frame):

        self.frames[frame].tkraise()

    def closeWindow(self):

        self.destroy()

# **********************************************************************************************************************
# **********************************************************************************************************************
# **********************************************************************************************************************

class ChatMenu(Frame):
   
    def __init__(self, parent, changeWindowFrameTo, closeWindow):
    
        Frame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)    
        
        self.txtInfo = ScrolledText(self, font=("Arial Bold", 14))
        self.txtInfo.grid(row=0, column=0, padx=10, pady=10)
        self.txtInfo.configure(state='disabled')

        self.etrInput = Entry(self, font=("Arial Bold", 20), justify='center')        
        self.etrInput.grid(row=1, column=0, padx=10, pady=10, sticky=W+E)

        self.btnVolver = Button(self, text="ENVIAR", font=("Arial Bold", 20), command=lambda : closeWindow())
        self.btnVolver.grid(row=2, column=0, padx=10, pady=10, sticky=W+E)

        self.btnVolver = Button(self, text="SALIR DEL PROGRAMA", font=("Arial Bold", 20), command=lambda : closeWindow())
        self.btnVolver.grid(row=3, column=0, padx=10, pady=10, sticky=W+E)
