import view
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

            Model.getInstance().loadAgents()

        elif context["event"] == "HUMAN_INPUT":

            Model.getInstance().sendUserInputToChatBotAgent(context["object"])

        elif context["event"] == "BOT_ANSWER":

            view.GuiChat.getInstance().update({ 'event': 'UPDATE_CHAT' , 'object': context["object"] })