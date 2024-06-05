import os
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.embedding_models.Embeddings import getEmbedding

# Comment below 3 lines for local(non docker) installation. This is fix for sql lite issue - https://gist.github.com/defulmere/8b9695e415a44271061cc8e272f3c300 on older linux systems e.g. in IAC environments
#__import__('pysqlite3')
#import sys
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ----- end of fix ---------
from langchain.vectorstores import Chroma

load_dotenv()

COMMON_PARENT_PATH= os.environ.get('COMMON_PARENT_PATH')
if not os.path.isdir(COMMON_PARENT_PATH):
    os.mkdir(COMMON_PARENT_PATH)

PERSIST_DIRECTORY = os.path.join(COMMON_PARENT_PATH, os.environ.get('PERSIST_DIRECTORY_PDF'))
if not os.path.isdir(PERSIST_DIRECTORY):
    os.mkdir(PERSIST_DIRECTORY)

print('PERSIST_DIRECTORY: ',PERSIST_DIRECTORY)
SOURCE_DOCUMENTS = os.environ.get('SOURCE_DOCUMENTS')

def isDirectoryEmpty(directory):
    return not os.listdir(directory)

def indexNotExist():
    return isDirectoryEmpty(PERSIST_DIRECTORY) is True

def getDocuments():
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    DOCUMENTS = []
    for pdf in os.listdir(SOURCE_DOCUMENTS):
        loader = PyPDFLoader(SOURCE_DOCUMENTS+"/"+pdf)
        DOCUMENTS.extend(text_splitter.split_documents(loader.load()))
    for d in  DOCUMENTS[:10]:
        print(d)
        print("===================================== Next page content ====================")
    return DOCUMENTS


if indexNotExist() is True:
    message = {"message" : "====================== Creating Index ==========================="}
    DOCUMENTS = getDocuments()
    print('pre-processing source documents, number of documents created:')
    print(len(DOCUMENTS))
    VECTORSTORE = Chroma.from_documents(persist_directory=PERSIST_DIRECTORY, documents=DOCUMENTS, embedding=getEmbedding())
    print("====================== Created Index ===========================")
else :
    print("vectore store already exist, reusing that. If there is a data change, please delete persistent directory  and restart.")
    VECTORSTORE = Chroma( embedding_function=getEmbedding(),  persist_directory=PERSIST_DIRECTORY)


def getRetriever():
    return VECTORSTORE.as_retriever()

def getDocumentsForSinglePDF(pdfName: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=500)
    file = pdfName
    loader = PyPDFLoader(SOURCE_DOCUMENTS+"/"+file)
    documents = loader.load()
    textDocuments = text_splitter.split_documents(documents)
    vectorDB = Chroma.from_documents(textDocuments, getEmbedding())
    return [textDocuments,vectorDB]
