from tkinter import scrolledtext
from tkinter.constants import INSERT
import controller as ctrl

from spade import quit_spade

from tkinter import W
from tkinter import E
from tkinter import Tk
from tkinter import END
from tkinter import Frame
from tkinter import Entry
from tkinter import Button
from tkinter import INSERT
from tkinter.scrolledtext import ScrolledText

# **********************************************************************************************************************
# **********************************************************************************************************************
# **********************************************************************************************************************
# **********************************************************************************************************************

# Clase que representa la ventana de la aplicación.
class Window(Tk):

    # Inicializamos las propiedades de la ventana.
    def __init__(self, *args, **kwargs):
        
        Tk.__init__(self, *args, **kwargs)

        self.title('News App')
        self.geometry('800x480')
        self.configure(bg='white')
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", lambda: self.closeWindow())
        
        self.frames = {}
        self.mainContainer = Frame(self)
        self.mainContainer.grid_rowconfigure(0, weight=1)
        self.mainContainer.grid_columnconfigure(0, weight=1)
        self.mainContainer.pack(side="top", fill="both", expand = True)

        self.frames[GuiChat] = GuiChat.getInstance(self.mainContainer)
        self.frames[GuiChat].tkraise()
    
    # Este método se llama al pulsarse el aspa de cierre de la ventana.
    def closeWindow(self):

        quit_spade()
        self.destroy()
        
# **********************************************************************************************************************
# **********************************************************************************************************************
# **********************************************************************************************************************
# **********************************************************************************************************************

# Clase "interfaz" para GUI's.
class GUI(Frame):
    # Método para actualizar la interfaz de usuario. 
    def update(self, context):
        pass

# Clase "abstract" para hacer "singleton" una GUI concreta.
class GuiChat(GUI):

    __instance = None

    @staticmethod
    def getInstance(parent=None):

        if GuiChat.__instance is None:
            GuiChat.__instance = GuiChatImp(parent)

        return GuiChat.__instance

# **********************************************************************************************************************
# **********************************************************************************************************************
# **********************************************************************************************************************

# Clase que hereda de ScrolledText para gestionar la caja de texto y sus eventos.
class Notepad(ScrolledText):

    def __init__(self, master, **kw):
        ScrolledText.__init__(self, master, **kw)
        self.bind('<Control-c>', self.__copy)
        self.bind('<Key>', lambda param : "break")

    def __copy(self, event=None):
        self.clipboard_clear()
        self.clipboard_append(self.get("sel.first", "sel.last"))

# **********************************************************************************************************************
# **********************************************************************************************************************
# **********************************************************************************************************************

# Clase implementación de una interfaz gráfica de usuario.
class GuiChatImp(GuiChat):
   
    # Inicializamos los elementos de la GUI en el contructor.
    def __init__(self, parent):
    
        Frame.__init__(self, parent)

        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)    
        
        self.txtInfo = Notepad(self, font=("Arial Bold", 14))
        self.txtInfo.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.etrInput = Entry(self, font=("Arial Bold", 20), justify='center')        
        self.etrInput.grid(row=1, column=0, padx=10, pady=10, sticky=W+E)
        self.etrInput.bind('<Return>', lambda param : self.__send())
        self.etrInput.focus()

        self.btnEnviar = Button(self, text="SEND", font=("Arial Bold", 20), command=lambda : self.__send())
        self.btnEnviar.grid(row=1, column=1, padx=10, pady=10, sticky=W+E)
        self.btnEnviar.bind('<Return>', lambda event : self.__send())

    # Este método se llama al ser pulsado el botón SEND, obtiene el texto de la GUI y lo pasa al controlador.
    def __send(self):

        if str(self.etrInput.get()).strip() != "":

            text = self.etrInput.get()
            self.etrInput.delete(0, END)

            self.txtInfo.insert(END, "human > " + text + "\n")
            self.txtInfo.see(END)

            ctrl.Controller.getInstance().action({ 'event': 'HUMAN_INPUT', 'object': str(text).lower() })

    # Método para actualizar la interfaz de usuario.
    def update(self, context):

        if context["event"] == "UPDATE_CHAT":
            
            self.txtInfo.insert(END, context["object"] + "\n")
            self.txtInfo.see(END)
