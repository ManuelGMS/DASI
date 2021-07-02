import view
import model

class Controller:

    __instance = None

    @staticmethod
    def getInstance():

        if Controller.__instance is None:
            Controller.__instance = Controller()

        return Controller.__instance

    # Este método gestiona los eventos de la aplicación.
    def action(self, context):

        if context["event"] == "INITALIZE":

            model.Model.getInstance().loadAgents()

        elif context["event"] == "HUMAN_INPUT":

            model.Model.getInstance().sendUserInputToChatBotAgent(context["object"])

        elif context["event"] == "BOT_ANSWER":

            view.GuiChat.getInstance().update({ 'event': 'UPDATE_CHAT' , 'object': context["object"] })
            