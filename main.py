import view
import controller as ctrl

# Carga todos los datos necesarios antes de ejecutar la aplicación.
ctrl.Controller.getInstance().action({"event": "INITALIZE", "object": None})

# Ejecuta a aplicación.
view.Window().mainloop()
