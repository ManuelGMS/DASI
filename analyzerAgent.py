from json import loads

from asyncio import sleep

from os.path import join
from os.path import exists

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import State
from spade.behaviour import FSMBehaviour

from nltk import Tree
from nltk.tokenize import word_tokenize
from nltk import word_tokenize, pos_tag, ne_chunk



class AnalyzerAgent(Agent):

    def get_continuous_chunks(self, text, label):
        
        # Parseamos el texto (text) para poder analizarlo.
        chunked = ne_chunk(pos_tag(word_tokenize(text)))
        continuous_chunk = []
        current_chunk = []

        # Bucle en el que compara las etiquetas de cada palabra con la categoria dada (label).
        for subtree in chunked:
            if type(subtree) == Tree and subtree.label() == label:
                current_chunk.append(" ".join([token for token, pos in subtree.leaves()]))
            if current_chunk:
                named_entity = " ".join(current_chunk)
                if named_entity not in continuous_chunk:
                    continuous_chunk.append(named_entity)
                    current_chunk = []
            else:
                continue

        # Devolvemos la lista de palabras de la categoria dada (label).
        return continuous_chunk

    # Esta clase interna sirve para definir el comportamiento del agente.
    class FsmBehaviour(FSMBehaviour):
        pass

    class receiveState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):
            
            # Espera como mucho N segundos para recibir algún mensaje.
            msg = await self.receive(timeout=3600)
            
            # msg es un objeto o bien Message o bien None.
            if msg:
                # Volvemos a crear el diccionario
                dictdictAux = loads(msg.body)

                # Comprobamos que la noticia esté en la carpeta.                
                if exists(join("news", dictdictAux["new"])):

                    # Aquí volcaremos el contenido del fichero.
                    fileContent = None

                    # Leemos el contenido del fichero.
                    with open(join("news", dictdictAux["new"]), 'r') as file:

                        # Obtenemos el contenido del fichero.
                        fileContent = file.read()
                    
                    # Sacamos la informacion del texto por cada categoria.
                    category = dictdictAux["type"]
                    valores = {}
                    for cate in category.split():
                        # Llamamos a la funcion get_continuous_chunks() con el texto y la categoria en mayuscula.
                        valores[cate] = self.agent.get_continuous_chunks(fileContent, cate.upper())

                    # Damos forma al texto con la informacion extraida de cada categoria.
                    encontrado = ""
                    for cate in valores:
                        if valores[cate] == []:
                            # Si no encuentra informacion.
                            encontrado += "Can't find words of the category " + cate + " on this news\n"
                        else:
                            # Si encuentra informacion.
                            encontrado += "Words of the category " + cate + " are: \n\t"
                            for word in valores[cate]:
                                encontrado += word + ", "
                            encontrado += "\n"

                    # Almacenamos la informacion.
                    self.agent.lastAnalyze = encontrado

                else:
                    # No se ha encontrado la noticia.
                    self.agent.lastAnalyze = "The notice wasn't found in 'news' folder"

            # Una vez se ha clasificado la noticia pasamos al estado de envío para informar al agente ChatBot.
            self.set_next_state("SEND_STATE")

    class sendState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):

            # Envía el mensaje.
            await self.send(msg=Message(to="dasi1@blabber.im", body=self.agent.lastAnalyze))

            # Si no se introduce un poco de retardo, el envío podría no completarse.
            await sleep(0.2)

            # Pasamos al estado de escucha para que el agente de clasificación nos pueda devolver el tipo de noticia.
            self.set_next_state("RECEIVE_STATE")
    
    # Este método se llama cuando se inicializa el agente.
    async def setup(self):

        # Declaramos el comportamiento compuesto.
        fsm = self.FsmBehaviour()
        
        # Declaramos los subcomportamientos.
        fsm.add_state(name="RECEIVE_STATE", state=self.receiveState(), initial=True)
        fsm.add_state(name="SEND_STATE", state=self.sendState())

        # Declaramos las posibles transiciones entre estados.
        fsm.add_transition(source="RECEIVE_STATE", dest="SEND_STATE")
        fsm.add_transition(source="SEND_STATE", dest="RECEIVE_STATE")

        # Encolamos el siguiente comportamiento.
        self.add_behaviour(behaviour=fsm, template=Template(to="dasi3@blabber.im"))