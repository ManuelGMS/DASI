import controller as ctrl

from json import dumps

from asyncio import sleep

from os import remove
from os import devnull
from os.path import exists

from contextlib import redirect_stdout

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import State
from spade.behaviour import FSMBehaviour



class ChatBotAgent(Agent):

    __auxAnalizer = {
        "new": "",
        "type": ""
    }

    # Para almacenar el texto que llega de la GUI.
    __textFromGui = None
    
    def __init__(self, *args, **kwargs):

        # Llamada a la super (Agent).
        super().__init__(*args, **kwargs)

        # Texto a responder para clasificar.
        self.answerForClassification = "give me the new"

        # Texto a responder para analizar.
        self.answerForAnalyze = "choose the new"

    # Establece el último texto que llegó de la GUI.
    @staticmethod
    def setUserText(text):
        ChatBotAgent.__textFromGui = text
        
    # Obtiene el último texto que llegó de la GUI.
    @staticmethod
    def getUserText():
        return ChatBotAgent.__textFromGui

    @staticmethod
    def setAnalyzerData(text, tipo):
        ChatBotAgent.__auxAnalizer[tipo] = text
        
    @staticmethod
    def getAnalyzerData():
        return ChatBotAgent.__auxAnalizer

    # Esta clase interna sirve para definir el comportamiento del agente.
    class FsmBehaviour(FSMBehaviour):
        pass

    # Estado de la FSM.
    class initState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):

            # Para comprobar si hay que reentrenar al ChatBot.
            trainingNeeded = False

            # Si no existe el fichero ... hay que realizar el entrenamiento.
            if not exists("chatterbot/database.sqlite3"):
                trainingNeeded = True
    
            # Cargamos el ChatBot en el agente.
            self.agent.chatBot = ChatBot(
                # Nombre del ChatBot.
                name='ChatBot',
                # Evita que el bot aprenda de las conversaciones que tienen lugar después del entrenamiento.
                read_only=True,
                # Los datos relacionados con las conversaciones se almacenarán en una base de datos SQL.
                storage_adapter='chatterbot.storage.SQLStorageAdapter', 
                # Indica la base de datos en la que se almacenará la información de las conversaciones.
                database_uri='sqlite:///chatterbot/database.sqlite3',
                # Los preprocesadores son funciones que modifican la entrada que recibe el bot antes de que esta sea procesada por un adaptador lógico.
                preprocessors=[
                    # Elimina espacios en blanco adicionales que son innecesarios.
                    'chatterbot.preprocessors.clean_whitespace'
                ],
                # Los adaptadores lógicos determinan cómo se selecciona una respuesta ante una entrada.
                logic_adapters=[
                    {
                        # Adaptador lógico que devuelve una salida en base a la mayor coincidencia con una entrada conocida.
                        'import_path': 'chatterbot.logic.BestMatch',
                        # Establecemos como método para comparación de frases la Distancia de Levenshtein.
                        "statement_comparison_function": 'chatterbot.comparisons.levenshtein_distance',
                        # Umbral de similitud con las frases introducidas.
                        'maximum_similarity_threshold': 0.90,
                        # Respuesta por defecto cuando la entrada es desconocida.
                        'default_response': "I'm sorry, but I don't understand."
                    }
                ]
            )

            # Comprobamos si hace falta reentrenar al ChatBot.
            if trainingNeeded:

                # Objeto para entrenar al bot con nuestro propio corpus.
                trainer = ChatterBotCorpusTrainer(self.agent.chatBot)

                # Indicamos la ruta en la que se encuentra el corpus y realizamos un entrenamiento silencioso.
                with redirect_stdout(open(devnull, "w")):
                    trainer.train('./chatterbot/corpus.json')

                # Eliminamos el fichero.
                if exists("sentence_tokenizer.pickle"):
                    remove("sentence_tokenizer.pickle")

            # Cambiamos al estado INPUT en que averiguamos que quiere el usuario.
            self.set_next_state("INPUT_STATE")

    # Estado de la FSM.
    class inputState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):
            
            # Mientras no se detecte una entrada del usuario.
            while ChatBotAgent.getUserText() is None:
                pass
            
            # Recogemos la respuesta del chatBot.
            text = str(self.agent.chatBot.get_response(ChatBotAgent.getUserText()))

            # Devolvemos el texto para que llegue a la GUI.
            ctrl.Controller.getInstance().action({'event': 'BOT_ANSWER', 'object': "bot > " + text})

            # Volvemos a dejar el texto en None para que vuelva a quedarse esperando en el bucle.
            ChatBotAgent.setUserText(None)

            # Classify -> True ; Analyze -> False
            self.agent.classifyOrAnalyze = None

            # Analizamos la respuesta del ChatBot y en base a esta decidimos el siguiente estado.
            if text == self.agent.answerForClassification:
                self.agent.classifyOrAnalyze = True
                self.set_next_state("SEND_STATE")
            elif text == self.agent.answerForAnalyze:
                self.agent.classifyOrAnalyze = False
                self.set_next_state("MID_STATE")
            else:
                self.set_next_state("INPUT_STATE")
    
    # Estado de la FSM.
    class sendState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):

            # Mientras no se detecte una entrada del usuario.
            while ChatBotAgent.getUserText() is None:
                pass

            # Envía el mensaje.
            if self.agent.classifyOrAnalyze:
                await self.send(msg=Message(to="dasi2@blabber.im", body=ChatBotAgent.getUserText()))
            else:
                # Añadimos la categoria a analizar
                ChatBotAgent.setAnalyzerData(ChatBotAgent.getUserText(), "type")
                await self.send(msg=Message(to="dasi3@blabber.im", body=dumps(ChatBotAgent.getAnalyzerData())))

            # Si no se introduce un poco de retardo, el envío podría no completarse.
            await sleep(0.2)

            # Volvemos a dejar el texto en None para que vuelva a quedarse esperando en el bucle.
            ChatBotAgent.setUserText(None)

            # Pasamos al estado de escucha para que el agente de clasificación nos pueda devolver el tipo de noticia.
            self.set_next_state("RECEIVE_STATE")

    # Estado de la FSM.
    class receiveState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):

            # Espera como mucho N segundos para recibir algún mensaje.
            msg = await self.receive(timeout=3600)
            
            # msg es un objeto o bien Message o bien None.
            if msg:

                # Devolvemos el texto para que llegue a la GUI.
                ctrl.Controller.getInstance().action({'event': 'BOT_ANSWER', 'object': "bot > " + msg.body})

            # Volvemos al estado inicial para saber que quiere el usuario.
            self.set_next_state("INPUT_STATE")

    # Estado de la FSM.
    class midState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):

            # Mientras no se detecte una entrada del usuario.
            while ChatBotAgent.getUserText() is None:
                pass

            # Guardamos la noticia.
            ChatBotAgent.setAnalyzerData(ChatBotAgent.getUserText(), "new")

            # Volvemos a dejar el texto en None para que vuelva a quedarse esperando en el bucle.
            ChatBotAgent.setUserText(None)

            # Pedimos al usuario que introduzca la categoria que quiere analizar
            ctrl.Controller.getInstance().action({'event': 'BOT_ANSWER', 'object': "bot > What do you want to know? \nChoose one or more: Organization, Person, Location, Date, Time, Money, Percent, Facility or GPE"})

            # Pasamos al estado de escucha para que el agente de clasificación nos pueda devolver el tipo de noticia.
            self.set_next_state("SEND_STATE")

    # Este método se llama cuando se inicializa el agente.
    async def setup(self):
        
        # Declaramos el comportamiento compuesto.
        fsm = self.FsmBehaviour()
        
        # Declaramos los subcomportamientos.
        fsm.add_state(name="INIT_STATE", state=self.initState(), initial=True)
        fsm.add_state(name="INPUT_STATE", state=self.inputState())
        fsm.add_state(name="SEND_STATE", state=self.sendState())
        fsm.add_state(name="RECEIVE_STATE", state=self.receiveState())
        fsm.add_state(name="MID_STATE", state=self.midState())

        # Declaramos las posibles transiciones entre estados.
        fsm.add_transition(source="INIT_STATE", dest="INPUT_STATE")
        fsm.add_transition(source="INPUT_STATE", dest="INPUT_STATE")
        fsm.add_transition(source="INPUT_STATE", dest="SEND_STATE")
        fsm.add_transition(source="INPUT_STATE", dest="MID_STATE")
        fsm.add_transition(source="MID_STATE", dest="SEND_STATE")
        fsm.add_transition(source="SEND_STATE", dest="RECEIVE_STATE")
        fsm.add_transition(source="RECEIVE_STATE", dest="INPUT_STATE")

        # Encolamos el siguiente comportamiento.
        self.add_behaviour(behaviour=fsm, template=Template(to="dasi1@blabber.im"))