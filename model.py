from agents import ChatBotAgent
from agents import AnalyzerAgent
from agents import ClassifierAgent

class Model:
    
    __instance = None

    @staticmethod
    def getInstance():
        
        if Model.__instance is None:
            Model.__instance = Model()
        
        return Model.__instance

    def loadAgents(self):

        # Instanciamos el agente Clasificador.
        self.analyzerAgent = AnalyzerAgent("dasi3@blabber.im", "dasiproject3")
        # Indicamos al agente que comience (setup).
        future = self.analyzerAgent.start()
        # Esperamos a la inicialización completa del agente.
        future.result()

        # Instanciamos el agente Clasificador.
        self.classifierAgent = ClassifierAgent("dasi2@blabber.im", "dasiproject2")
        # Indicamos al agente que comience (setup).
        future = self.classifierAgent.start()
        # Esperamos a la inicialización completa del agente.
        future.result()   

        # Instanciamos el agente ChatBot.
        self.chatBotAgent = ChatBotAgent("dasi1@blabber.im", "dasiproject1")
        # Indicamos al agente que comience (setup).
        self.chatBotAgent.start()
        
    def sendUserInputToChatBotAgent(self, text):
        
        # Pasamos el texto de entrada al agente del ChatBot.
        self.chatBotAgent.setUserText(text)