import os
import langchain
from dotenv import load_dotenv
from flask import Flask, render_template
from datetime import datetime
from flask import request
from flask_cors import CORS
from langchain.chains import RetrievalQA
from flask import jsonify
from flask_sock import Sock
import json
import numpy as np
from src.config.appconfiguration import getLogosFolder

load_dotenv()

template_dir = os.path.abspath('./src/templates')
static_folder=getLogosFolder()
app = Flask(__name__, template_folder=template_dir, static_folder=static_folder)

cors = CORS(app, origins=['*'])
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}
sock = Sock(app)

k=int(os.environ.get('NO_OF_DOCS_TO_SEARCH_FROM'))
pdfretriever=[]

@app.route('/qa')
def qa():
    from src.config.appconfiguration import getPageText
    pageText = getPageText()
    return render_template('index.html', title=pageText["title"], appName = pageText["appName"], appDescription=pageText["appDescription"], chooseAreatext=pageText["chooseAreatext"], text = pageText["text"],
                           exampleQuestion1Area= pageText["exampleQuestion1Area"], exampleQuestion1= pageText["exampleQuestion1"],
                           exampleQuestion2Area= pageText["exampleQuestion2Area"], exampleQuestion2= pageText["exampleQuestion2"], exampleQuestion3Area=pageText["exampleQuestion3Area"],
                           exampleQuestion3=pageText["exampleQuestion3"], exampleQuestion4Area= pageText["exampleQuestion4Area"], exampleQuestion4=pageText["exampleQuestion4"])

@app.route('/')
def qa_with_websockets():
    from src.config.appconfiguration import getPageText
    pageText = getPageText()
    return render_template('index-ws.html', title=pageText["title"], appName = pageText["appName"], appDescription=pageText["appDescription"], chooseAreatext=pageText["chooseAreatext"], text = pageText["text"],
                           exampleQuestion1Area= pageText["exampleQuestion1Area"], exampleQuestion1= pageText["exampleQuestion1"],
    exampleQuestion2Area= pageText["exampleQuestion2Area"], exampleQuestion2= pageText["exampleQuestion2"], exampleQuestion3Area=pageText["exampleQuestion3Area"],
    exampleQuestion3=pageText["exampleQuestion3"], exampleQuestion4Area= pageText["exampleQuestion4Area"], exampleQuestion4=pageText["exampleQuestion4"])

def isDirectoryEmpty(directory):
    return not os.listdir(directory)




#Backend APIs used by above pages
@sock.route('/ask/ws')
def echo(ws):
    while True:
        start = datetime.now()
        data = ws.receive()
        print('query received in /ask/ws: ', data)
        data=json.loads(data)
        query = data.get('query')
        area = data.get('area')
        from src.dataloaders.confluenceLoader import getRetriever
        from src.utils.StreamHandler import WebSocketStreamHandler
        from src.llms.llama_cpp_llm import getLLM
        langchain.debug=True
        qa = RetrievalQA.from_chain_type( chain_type="stuff", retriever=getRetriever(area), llm=getLLM(), return_source_documents=True)
        callBack = WebSocketStreamHandler(ws)
        result = qa({"query": query}, callbacks=[callBack])
        # convert to html formatw
        end = datetime.now()
        td = (end - start).total_seconds()
        print(f"Finished querying. The time of execution of above program was : {td} seconds")
        sources=[]
        resultDocumentList = result['source_documents']
        for document in resultDocumentList:
            sources.append(document.metadata.get('source'))

        uniqueSources = np.unique(sources).tolist()
        print("sources considered for this answer:")
        for source in uniqueSources:
            print(source)
        response = {"completed": True,
                    "sources": uniqueSources
                    }
        ws.send(json.dumps(response))


#For Demo
@sock.route('/ask/ws/fromdocs')
def demo(ws):
    while True:
        start = datetime.now()
        data = ws.receive()
        print('query received in /ask/ws/fromdocs: ', data)
        data=json.loads(data)
        query = data.get('query')
        area = data.get('area')
        from src.dataloaders.dataloader_from_source_documents_folder import getRetriever
        from src.utils.StreamHandler import WebSocketStreamHandler
        from src.llms.llama_cpp_llm import getLLM
        #langchain.debug=True
        qa = RetrievalQA.from_chain_type( chain_type="stuff", retriever=getRetriever(), llm=getLLM(), return_source_documents=True)
        callBack=WebSocketStreamHandler(ws)
        result = qa({"query": query}, callbacks=[callBack])
        # convert to html format
        end = datetime.now()
        td = (end - start).total_seconds()
        print(f"Finished querying. The time of execution of above program was : {td} seconds")
        sources=[]
        resultDocumentList = result['source_documents']
        for document in resultDocumentList:
            sources.append(document.metadata.get('source'))

        uniqueSources = np.unique(sources).tolist()
        print("sources considered for this answer:")
        for source in uniqueSources:
            print(source)
        response = {"completed": True,
                    "sources": uniqueSources
                    }
        ws.send(json.dumps(response))

@app.route("/ask", methods=['GET'])
def main():
    start = datetime.now()
    args = request.args
    query=args.get("query")
    area=args.get("area")
    print('query received: '+str(query))
    print('area: ',area)
    from src.llms.llama_cpp_llm import getLLM
    from src.dataloaders.confluenceLoader import getRetriever
    qa = RetrievalQA.from_chain_type( chain_type="stuff", retriever=getRetriever(area), llm=getLLM(),  return_source_documents=True)
    result = qa({"query": query})
    answer = result['result']
    answer = answer.replace('\n', '<br/>')
    end = datetime.now()
    td = (end - start).total_seconds()
    print('')
    print(f"Finished querying. The time of execution of above program is : {td} seconds")
    sources=[]
    resultDocumentList = result['source_documents']
    for document in resultDocumentList:
        sources.append(document.metadata.get('source'))

    uniqueSources = np.unique(sources).tolist()
    print("sources considered for this answer:")
    for source in uniqueSources:
        print(source)
    response = {
        "answer": answer,
        "sources": uniqueSources
    }

    return jsonify(response)

def sortFunction(document):
    return document[1]

@app.route("/api/area", methods=['GET'])
def getConfluenceArea():
    from src.dataloaders.confluenceChildPageList import getArea
    area = getArea()
    return jsonify(area)

@app.route("/api/sources", methods=['GET'])
def getMatchingDocuments():
    start = datetime.now()
    args = request.args
    query=args.get("query")
    area=args.get("area")
    print('query received : '+str(query))
    print('area: ',area)
    from src.dataloaders.confluenceLoader import getRetriever
    docs = getRetriever(area).get_relevant_documents(query=query)
    print("================= sources for query: ========================= "+str(query))
    sources=[]
    for d in docs:
        sources.append(d.metadata.get('source'))

    uniqueSources = np.unique(sources).tolist()
    for uniqueSource in uniqueSources:
        print(uniqueSource)

    end = datetime.now()
    td = (end - start).total_seconds()
    print(f"The time of execution of above program is : {td} seconds")
    return jsonify(uniqueSources)

def hardreset():
    print('Removing existing data')
    COMMON_PARENT_PATH= os.environ.get('COMMON_PARENT_PATH')
    import  shutil
    for files in os.listdir(COMMON_PARENT_PATH):
        path = os.path.join(COMMON_PARENT_PATH, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)
    print('Flushing cache')
    from src.dataloaders import confluenceLoader
    confluenceLoader.DOCUMENTS_PER_AREA=[]
    confluenceLoader.VECTORSTORE=[]
    confluenceLoader.areaToRetrieverCache=[]
    print('Flushed the cache')


@app.route("/api/init", methods=['GET'])
def resetIndex():
    args = request.args
    query=args.get("hardreset")
    if query == 'true':
        hardreset()
    from src.dataloaders.confluenceLoader import initializeVectorDB, getRetriever
    initializeVectorDB()
    from src.dataloaders.confluenceChildPageList import getArea
    differentArea=getArea()
    for area in differentArea:
        getRetriever(area)
    #from src.dataloaders.from_Source_Documents_with_parentRetriever import getRetriever
    #getRetriever('All')
    from src.llms.llama_cpp_llm import loadModel
    loadModel()
    print('------------- initialization completed  ----------')
    response={'status': "reset completed"}
    return jsonify(response)





