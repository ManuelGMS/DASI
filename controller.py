from model import Model

class Controller:

    __instance = None

    @staticmethod
    def getInstance():

        if Controller.__instance is None:
            Controller.__instance = Controller()

        return Controller.__instance

    def action(self, context):

        if context["event"] == "INITALIZE":

            model = Model.getInstance()


