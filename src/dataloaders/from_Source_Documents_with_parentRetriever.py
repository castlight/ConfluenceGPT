import os
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
from src.embedding_models.Embeddings import getEmbedding

# Comment below 3 lines for local installation. This is fix for sql lite issue - https://gist.github.com/defulmere/8b9695e415a44271061cc8e272f3c300 on older linux systems e.g. in IAC environments
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ----- end of fix ---------
import chromadb


load_dotenv()
COMMON_PARENT_PATH= os.environ.get('COMMON_PARENT_PATH')
if not os.path.isdir(COMMON_PARENT_PATH):
    os.mkdir(COMMON_PARENT_PATH)

PERSIST_DIRECTORY = os.path.join(COMMON_PARENT_PATH, os.environ.get('PERSIST_DIRECTORY_PDF'))
if not os.path.isdir(PERSIST_DIRECTORY):
    os.mkdir(PERSIST_DIRECTORY)

print('PERSIST_DIRECTORY: ',PERSIST_DIRECTORY)
SOURCE_DOCUMENTS = os.environ.get('SOURCE_DOCUMENTS')

from langchain.text_splitter import RecursiveCharacterTextSplitter
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=1400, chunk_overlap=100)
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
persistent_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
vectorstore = Chroma(
    client=persistent_client,
    embedding_function=getEmbedding(),
)

from langchain.storage import LocalFileStore, create_kv_docstore
fileStorePath=PERSIST_DIRECTORY+"/parent_docs"
fileStore = LocalFileStore(fileStorePath)
store = create_kv_docstore(fileStore)
from langchain.retrievers import ParentDocumentRetriever
retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)
if os.path.isdir(fileStorePath) is False:
    DOCUMENTS=[]
    for pdf in os.listdir(SOURCE_DOCUMENTS):
        loader = PyPDFLoader(SOURCE_DOCUMENTS+"/"+pdf)
        DOCUMENTS.extend(child_splitter.split_documents(loader.load()))
    print("no of document: ",len(DOCUMENTS))
    retriever.add_documents(DOCUMENTS, ids=None)


def getRetriever(area):
    return retriever

def getDocumentsForSinglePDF(pdfName: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    file = pdfName
    loader = PyPDFLoader(SOURCE_DOCUMENTS+"/"+file)
    documents = loader.load()
    textDocuments = text_splitter.split_documents(documents)
    vectorDB = Chroma.from_documents(textDocuments, getEmbedding())
    return [textDocuments,vectorDB]
