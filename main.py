from view import Window
from controller import Controller

# Carga todos los datos necesarios antes de ejecutar la aplicación.
Controller.getInstance().action({"event": "INITALIZE", "object": None})

# Ejecuta a aplicación.
Window().mainloop()
