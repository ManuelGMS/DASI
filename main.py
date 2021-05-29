import view
import controller as ctrl

# Carga todos los datos necesarios antes de ejecutar la aplicación.
ctrl.Controller.getInstance().action({"event": "INITALIZE", "object": None})

# Lanza la ventana de la aplicación.
view.Window().mainloop()
