from asyncio import sleep

from GoogleNews import GoogleNews

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import State
from spade.behaviour import FSMBehaviour

class RecomenderAgent(Agent):

    # Esta clase interna sirve para definir el comportamiento del agente.
    class FsmBehaviour(FSMBehaviour):
        pass

    # Estado de la FSM.
    class initState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):
            # Definimos la configuracion para la busqueda.
            googlenews = GoogleNews()
            googlenews.set_lang('en')  # Idioma elegido ingles.
            googlenews.set_period('7d') # Noticias de los ultimos 7 dias.
            googlenews.set_encode('utf-8') # Formato de codificacion de caracteres UTF-8.       

            self.agent.googlenews = googlenews

            # Una vez comfigurado todo pasamos al estado de recepción a la espera de noticias que clasificar.
            self.set_next_state("RECEIVE_STATE")

    # Estado de la FSM.
    class receiveState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):

            # Espera como mucho N segundos para recibir algún mensaje.
            msg = await self.receive(timeout=3600)

            # msg es un objeto o bien Message o bien None.
            if msg:
                
                # Buscamos noticias de la categoria de msg.body
                self.agent.googlenews.search(msg.body)

                # results() devuelve una lista de diccionarios con varios campos de informacion.
                solucion = self.agent.googlenews.results()

                # Borramos los datos que tiene la variable googlenews tras realizar la busqueda.
                self.agent.googlenews.clear()

                # Preparamos el texto que se va a devolver, cogiendo los campos que nos interesan.
                res = ""
                for a in solucion:
                    res += str(a['title']) + '\n' + str(a['desc']) + '\n' + str(a['date']) + '\n'
                    if str(a['datetime']) != "None":
                        res += str(a['datetime']) + '\n'
                    res += str(a['link']) + '\n' + '\n'

                # Respuesta a devolver si no se han encontrado noticias.
                if res == "":
                    res = "I cant find news about that topic"

                # Almacenamos la respuesta.
                self.agent.lastPrediction = res

            # Una vez se ha clasificado la noticia pasamos al estado de envío para informar al agente ChatBot.
            self.set_next_state("SEND_STATE")

    # Estado de la FSM.
    class sendState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):
            
            # Envía el mensaje.
            await self.send(msg=Message(to="dasi1@blabber.im", body=self.agent.lastPrediction))

            # Si no se introduce un poco de retardo, el envío podría no completarse.
            await sleep(0.2)

            # Pasamos al estado de escucha para que el agente de clasificación nos pueda devolver el tipo de noticia.
            self.set_next_state("RECEIVE_STATE")

    # Este método se llama cuando se inicializa el agente.
    async def setup(self):

        # Declaramos el comportamiento compuesto.
        fsm = self.FsmBehaviour()
        
        # Declaramos los subcomportamientos.
        fsm.add_state(name="INIT_STATE", state=self.initState(), initial=True)
        fsm.add_state(name="RECEIVE_STATE", state=self.receiveState())
        fsm.add_state(name="SEND_STATE", state=self.sendState())

        # Declaramos las posibles transiciones entre estados.
        fsm.add_transition(source="INIT_STATE", dest="RECEIVE_STATE")
        fsm.add_transition(source="RECEIVE_STATE", dest="SEND_STATE")
        fsm.add_transition(source="SEND_STATE", dest="RECEIVE_STATE")

        # Encolamos el siguiente comportamiento.
        self.add_behaviour(behaviour=fsm, template=Template(to="dasi4@blabber.im"))