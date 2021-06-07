from pickle import dump
from pickle import load

from csv import writer
from asyncio import sleep
from pandas import read_csv

from os import walk
from os import remove
from os.path import join
from os.path import exists
from os.path import basename

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
from spade.behaviour import State
from spade.behaviour import FSMBehaviour

from nltk import pos_tag
from nltk.corpus import stopwords as sw
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer



class ClassifierAgent(Agent):

    def preprocessing(self, text):

        # Contendrá el texto lematizado de una noticia.
        lemmatizedText = ""
        
        # Lematizador de palabras.
        lemmatizer = WordNetLemmatizer()
        
        # Tokenizamos el texto (lo dividimos en palabras) y luego para cada una obtenemos un par (word, typeOfWord).
        for word, typeOfWord in pos_tag(word_tokenize(text.lower())):
            
            # Si la palabra es completamente alfabética y no es una stopword (no tiene significado por sí misma: artículos, pronombres, preposiciones, adverbios, etc ...).
            if word.isalpha() and word not in sw.words('english'):

                # Lematizamos la palabra y la añadimos al texto de la noticia lematizada.
                lemmatizedText += lemmatizer.lemmatize(word) + " "
        
        # Devolvemos la noticia lematizada.
        return lemmatizedText.rstrip()

    # Esta clase interna sirve para definir el comportamiento del agente.
    class FsmBehaviour(FSMBehaviour):
        pass

    # Estado de la FSM.
    class initState(State):

        # Este método se llama después de ejecutarse on_start().
        async def run(self):

            # Crearemos un corpus, es decir, un conjunto de textos de diversas clases ordenados y clasificados. 
            corpus = None

            # Comprobamos que exista el fichero con las noticias clsificadas.
            if not exists('classifier/newsClassified.csv'):

                # Creamos el fichero que contendrá las noticias clasificadas.
                with open('classifier/newsClassified.csv', 'w') as csvFile:

                    # Escribimos una primera fila a modo de cabecera.
                    csvWriter = writer(csvFile)
                    csvWriter.writerow(["news", "label"])

                    # Obtenemos las listas de los ficheros de cada directorio.
                    for directory, _, files in walk('bbcsport'):

                        # Recorremos la lista de ficheros del directorio actual.
                        for f in files:

                            # Abrimos el fichero que corresponda del directorio actual.
                            with open(join(directory, f), 'r', encoding='latin-1') as file:

                                # Escribimos dos columnas: contenido de la noticia y tipo de deporte.
                                csvWriter.writerow([file.read(), basename(directory)])

                # Creamos un corpus, es decir, un conjunto de textos de diversas clases ordenados y clasificados. 
                corpus = read_csv("classifier/newsClassified.csv", encoding='utf-8')

                # Preprocesamos los textos de cada noticia.
                corpus['lemmatizedNew'] = corpus['news'].map(self.agent.preprocessing)

                # Si queda alguno de estos ficheros hay que eliminarlos para volver a generarlos.
                if exists("classifier/svm.pkl"): remove("classifier/svm.pkl")
                if exists("classifier/labelEncoder.pkl"): remove("classifier/labelEncoder.pkl")
                if exists("classifier/tFidfMatrixVector.pkl"): remove("classifier/tFidfMatrixVector.pkl")

                # Otenemos para el texto de cada noticia su vector TF-IDF.
                tfIdfMatrixVectors = TfidfVectorizer()
                texts = tfIdfMatrixVectors.fit_transform(corpus['lemmatizedNew'])

                # LabelEncoder convierte las etiquetas de las clases en identificadores numéricos que van de 0 a N-Clases.
                labelEncoder = LabelEncoder()
                labels = labelEncoder.fit_transform(corpus['label'])

                # Dividimos los datos en un set de entrenamiento y en un set de pruebas.
                trainValues, testValues, trainResults, testResults = train_test_split(texts, labels, test_size=0.25)

                '''

                Clasificador SVM

                C: Factor de regularización. 
                    (<<): se ajustarán los hiperplanos para tener menor margen de separación y así conseguir que todos los puntos de entrenamiento se clasifiquen correctamente.
                    (>>): se ajustarńa los hiperplanos para tener un mayor margen de separación.
                
                kernel: linear.
                
                '''
                svm = SVC(C=1, kernel='linear')

                # Ajusta el clasificador al modelo de datos.
                svm.fit(trainValues, trainResults)

                # Serializamos los objetos.
                dump(svm, open('classifier/svm.pkl', 'wb'))
                dump(labelEncoder, open('classifier/labelEncoder.pkl', 'wb'))
                dump(tfIdfMatrixVectors, open('classifier/tFidfMatrixVector.pkl', 'wb'))

            # Cargar la máquina de vectores de soporte.
            self.agent.svm = load(open('classifier/svm.pkl', 'rb'))

            # Cargamos el conversor de etiquetas.
            self.agent.labelEncoder = load(open('classifier/labelEncoder.pkl', 'rb'))

            # Cargamos la matriz de vectores TF-IDF.
            self.agent.tFidfMatrixVector = load(open('classifier/tFidfMatrixVector.pkl', 'rb'))

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
                
                # Comprobamos que la noticia esté en la carpeta.                
                if exists(join("news", msg.body)):

                    # Aquí volcaremos el contenido del fichero.
                    fileContent = None

                    # Leemos el contenido del fichero.
                    with open(join("news", msg.body), 'r') as file:

                        # Obtenemos el contenido del fichero.
                        fileContent = file.read()

                    # Vamos a clasificar un nuevo texto ajeno a los textos para el entrenamiento y el testing.
                    tfIdfVectorOfNewText = self.agent.tFidfMatrixVector.transform([self.agent.preprocessing(fileContent)])

                    # Realizamos la predicción.
                    svmPrediction = self.agent.svm.predict(tfIdfVectorOfNewText)

                    # Alamacenamos esta predicción como la última realizada.
                    self.agent.lastPrediction = "I think it's a " + self.agent.labelEncoder.inverse_transform(svmPrediction)[0] + " news"

                else:

                    # No se ha encontrado la noticia.
                    self.agent.lastPrediction = "The notice wasn't found in 'news' folder"

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
        self.add_behaviour(behaviour=fsm, template=Template(to="dasi2@blabber.im"))