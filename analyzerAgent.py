from asyncio import sleep

from os.path import join
from os.path import exists

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import State
from spade.behaviour import FSMBehaviour

from nltk import pos_tag
from nltk import sent_tokenize
from nltk import ne_chunk_sents
from nltk.tokenize import word_tokenize



class AnalyzerAgent(Agent):

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

                # Comprobamos que la noticia esté en la carpeta.                
                if exists(join("news", msg.body)):

                    # Aquí volcaremos el contenido del fichero.
                    fileContent = None

                    # Leemos el contenido del fichero.
                    with open(join("news", msg.body), 'r') as file:

                        # Obtenemos el contenido del fichero.
                        fileContent = file.read()

                    sentences = sent_tokenize(fileContent)
                    tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]
                    tagged_sentences = [pos_tag(sentence) for sentence in tokenized_sentences]
                    chunked_sentences = ne_chunk_sents(tagged_sentences, binary=True)

                    def extract_entity_names(t):
                        entity_names = []

                        if hasattr(t, 'label') and t.label:
                            if t.label() == 'NE':
                                entity_names.append(' '.join([child[0] for child in t]))
                            else:
                                for child in t:
                                    entity_names.extend(extract_entity_names(child))

                        return entity_names


                    entity_names = []
                    for tree in chunked_sentences:
                        # Print results per sentence
                        # print extract_entity_names(tree)

                        entity_names.extend(extract_entity_names(tree))

                    # Print all entity names
                    #print(entity_names)

                    # Print unique entity names
                    #print(set(entity_names))

                    self.agent.lastAnalyze = str(set(entity_names))

                    #print(sorted(names.items(), key=lambda x:x[1], reverse=True))

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