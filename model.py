import json
import pandas

class Model:
    
    __instance = None

    def __init__(self):
        pass

    @staticmethod
    def getInstance():

        if Model.__instance is None:
            Model.__instance = Model()

        return Model.__instance

    def loadNews(self):
        pass
        
