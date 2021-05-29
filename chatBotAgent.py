import controller as ctrl

from asyncio import sleep

from os import remove
from os.path import exists

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import State
from spade.behaviour import FSMBehaviour



class ChatBotAgent(Agent):

    __textFromGui = None

    def __init__(self, *args, **kwargs):

        # Llamada a la super (Agent).
        super().__init__(*args, **kwargs)

        # Texto a responder para clasificar.
        self.answerForClassification = "give me the new"

        # Texto a responder para analizar.
        self.answerForAnalyze = "choose the new"

        # Texto a mostrar por defecto cuando no se entiende la entrada del usuario.
        self.defaultAnswer = "I'm sorry, but I don't understand."

        # True == Classify, False == Analyze
        self.classifyOrAnalyze = None

    @staticmethod
    def setUserText(text):
        ChatBotAgent.__textFromGui = text
        
    @staticmethod
    def getUserText():
        return ChatBotAgent.__textFromGui

    # Esta clase interna sirve para definir el comportamiento del agente.
    class FsmBehaviour(FSMBehaviour):
        pass

    class initState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):

            # Comprobamos que existen ambos ficheros, de lo contrario hay que realizar el entrenamiento.
            if not (exists("chatterbot/database.sqlite3") and exists("sentence_tokenizer.pickle")):

                # Si queda alguno de ellos hay que eliminarlos para volver a generarlos.
                if exists("chatterbot/database.sqlite3"): remove("database.sqlite3")
                if exists("sentence_tokenizer.pickle"): remove("sentence_tokenizer.pickle")

                # Instanciamos un chatBot.
                self.agent.chatBot = ChatBot(
                    silence_performance_warning=True,
                    # Nombre del ChatBot.
                    name='ChatBot',
                    # Evita que el bot aprenda de las conversaciones que tienen lugar después del entrenamiento.
                    read_only=True,
                    # Los datos relacionados con las conversaciones se almacenarán en una base de datos SQL.
                    storage_adapter='chatterbot.storage.SQLStorageAdapter', 
                    # Indica la base de datos en la que se almacenará la información de las conversaciones.
                    database_uri='sqlite:///chatterbot/database.sqlite3',
                    # Los adaptadores lógicos determinan cómo se selecciona una respuesta ante una entrada.
                    logic_adapters=[
                        {
                            # Adaptador lógico que devuelve una salida en base a la mayor coincidencia con una entrada conocida.
                            'import_path': 'chatterbot.logic.BestMatch',
                            # Umbral de similitud con las frases introducidas.
                            'maximum_similarity_threshold': 0.80,
                            # Respuesta por defecto cuando la entrada es desconocida.
                            'default_response': self.agent.defaultAnswer
                        }
                    ]
                )

                # Grafos de las conversaciones.
                dialogs = (
                    ['classify', self.agent.answerForClassification],
                    ['classify new', self.agent.answerForClassification],
                    ['classify that', self.agent.answerForClassification],
                    ['classify this', self.agent.answerForClassification],
                    ['i want you to classify this new', self.agent.answerForClassification],
                    ['analyze', self.agent.answerForAnalyze],
                    ['analyze new', self.agent.answerForAnalyze],
                    ['analyze that', self.agent.answerForAnalyze],
                    ['analyze this', self.agent.answerForAnalyze],
                    ['i want you to analyze this new', self.agent.answerForAnalyze]
                )

                # Objeto para entrenar al bot con las conversaciones definidas.
                trainer = ListTrainer(self.agent.chatBot)

                # Entrenamos al bot con las conversaciones definidas.
                for dialog in dialogs:
                    trainer.train(dialog)

            else:

                # Instanciamos un chatBot.
                self.agent.chatBot = ChatBot(
                    # Nombre del ChatBot.
                    name='ChatBot',
                    # Evita que el bot aprenda de las conversaciones que tienen lugar después del entrenamiento.
                    read_only=True,
                    # Los datos relacionados con las conversaciones se almacenarán en una base de datos SQL.
                    storage_adapter='chatterbot.storage.SQLStorageAdapter', 
                    # Indica la base de datos en la que se almacenará la información de las conversaciones.
                    database_uri='sqlite:///chatterbot/database.sqlite3',
                    # Los adaptadores lógicos determinan cómo se selecciona una respuesta ante una entrada.
                    logic_adapters=[
                        {
                            # Adaptador lógico que devuelve una salida en base a la mayor coincidencia con una entrada conocida.
                            'import_path': 'chatterbot.logic.BestMatch',
                            # Umbral de similitud con las frases introducidas.
                            'maximum_similarity_threshold': 0.80,
                            # Respuesta por defecto cuando la entrada es desconocida.
                            'default_response': self.agent.defaultAnswer
                        }
                    ]
                )

            # Cambiamos al estado INPUT en que averiguamos que quiere el usuario.
            self.set_next_state("INPUT_STATE")

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

            # Pasamos a clasificar o ciclamos en el estado.
            if text == self.agent.answerForClassification:
                self.agent.classifyOrAnalyze = True
                self.set_next_state("SEND_STATE")
            elif text == self.agent.answerForAnalyze:
                self.agent.classifyOrAnalyze = False
                self.set_next_state("SEND_STATE")
            else:
                self.set_next_state("INPUT_STATE")
            
    class sendState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):

            # Mientras no se detecte una entrada del usuario.
            while ChatBotAgent.getUserText() is None:
                pass

            # Envía el mensaje.
            await self.send(msg=Message(to="dasi2@blabber.im" if self.agent.classifyOrAnalyze else "dasi3@blabber.im", body=ChatBotAgent.getUserText()))

            # Si no se introduce un poco de retardo, el envío podría no completarse.
            await sleep(0.2)

            # Volvemos a dejar el texto en None para que vuelva a quedarse esperando en el bucle.
            ChatBotAgent.setUserText(None)

            # Pasamos al estado de escucha para que el agente de clasificación nos pueda devolver el tipo de noticia.
            self.set_next_state("RECEIVE_STATE")

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

    # Este método se llama cuando se inicializa el agente.
    async def setup(self):
        
        # Declaramos el comportamiento compuesto.
        fsm = self.FsmBehaviour()
        
        # Declaramos los subcomportamientos.
        fsm.add_state(name="INIT_STATE", state=self.initState(), initial=True)
        fsm.add_state(name="INPUT_STATE", state=self.inputState())
        fsm.add_state(name="SEND_STATE", state=self.sendState())
        fsm.add_state(name="RECEIVE_STATE", state=self.receiveState())

        # Declaramos las posibles transiciones entre estados.
        fsm.add_transition(source="INIT_STATE", dest="INPUT_STATE")
        fsm.add_transition(source="INPUT_STATE", dest="INPUT_STATE")
        fsm.add_transition(source="INPUT_STATE", dest="SEND_STATE")
        fsm.add_transition(source="SEND_STATE", dest="RECEIVE_STATE")
        fsm.add_transition(source="RECEIVE_STATE", dest="INPUT_STATE")

        # Encolamos el siguiente comportamiento.
        self.add_behaviour(behaviour=fsm, template=Template(to="dasi1@blabber.im"))