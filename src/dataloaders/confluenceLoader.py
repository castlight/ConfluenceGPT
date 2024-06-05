import os
from langchain.document_loaders import ConfluenceLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from src.embedding_models.Embeddings import getEmbedding
from src.dataloaders.confluenceChildPageList import getAllPageIds
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from datetime import datetime
# Comment below 3 lines for local(non docker) installation. This is fix for sql lite issue - https://gist.github.com/defulmere/8b9695e415a44271061cc8e272f3c300 on older linux systems e.g. in IAC environments
#__import__('pysqlite3')
#import sys
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ----- end of fix ---------
import chromadb

load_dotenv()

COMMON_PARENT_PATH= os.environ.get('COMMON_PARENT_PATH')
if not os.path.isdir(COMMON_PARENT_PATH):
    os.mkdir(COMMON_PARENT_PATH)

url=os.environ.get('CONFLUENCE_URL')
username=os.environ.get('CONFLUENCE_USERNAME')
encrypted_api_key=os.environ.get('CONFLUENCE_PASSWORD_OR_APIKEY')
key = os.environ.get('CONFLUENCE_APIKEY_ENCKEY')
f = Fernet(key)
api_key=f.decrypt(encrypted_api_key)

parent_chunk_size = int(os.environ.get('PARENT_PARAGRAPH_SIZE'))
child_chunk_size = int(os.environ.get('CHILD_PARAGRAPH_SIZE'))

loader = ConfluenceLoader(
    url=url,
    username=username,
    api_key=api_key
)

PERSIST_DIRECTORY = os.path.join(COMMON_PARENT_PATH, os.environ.get('PERSIST_DIRECTORY_CONFLUENCE'))
if not os.path.isdir(PERSIST_DIRECTORY):
    os.mkdir(PERSIST_DIRECTORY)

def getRootPersistentDirectory():
    return PERSIST_DIRECTORY

VECTORSTORE=[]

def getPersistentDirectoryForArea(area:str):
    return os.path.join(PERSIST_DIRECTORY, area)



def initializeVectorDB():
    from src.dataloaders.confluenceChildPageList import getArea
    areaList=  getArea()
    for area in areaList:
        persist_directory=getPersistentDirectoryForArea(area)
        persistent_client = chromadb.PersistentClient(path=persist_directory)
        collectionName = ''.join(letter for letter in area if letter.isalnum())
        vectorStoreForArea = Chroma(
            client=persistent_client,
            collection_name=collectionName,
            embedding_function=getEmbedding(),
        )
        VECTORSTORE.append({'area': area,'index': vectorStoreForArea})

initializeVectorDB()
def getSpecificIndex(area):
    if area is None:
        area = 'All'
    for vectorstoremapping in VECTORSTORE:
        if area == vectorstoremapping.get('area'):
            return vectorstoremapping.get('index')

    #print('No index was found for this area, index corruption OR a non-supported area observed')

#Optimize the quality of the output using the best retriever configuration here

areaToRetrieverCache=[]
def getRetriever(area):
    for areaToRetriever in areaToRetrieverCache:
        if area == areaToRetriever.get('area'):
            retriever = areaToRetriever.get('retriever')
            print('Found retriever in the cache')
            return retriever
    print('Initializing index for area: ', area)
    start = datetime.now()
    vectorstore=getSpecificIndex(area)
    from langchain.storage import LocalFileStore, create_kv_docstore
    fileStorePath = getRootPersistentDirectory()+"/"+area+"/parentdocs"
    fileStore = LocalFileStore(fileStorePath)
    store = create_kv_docstore(fileStore)
    from langchain.retrievers import ParentDocumentRetriever
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=100)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=child_chunk_size)
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter
    )
    if os.path.isdir(fileStorePath) is False:
        DOCUMENTS=getDOCUMENTS(area)
        chunkSize=100
        if(len(DOCUMENTS) < chunkSize):
            chunkSize=len(DOCUMENTS)
        for i in range(0, len(DOCUMENTS), chunkSize):
            batch = DOCUMENTS[i:i+chunkSize]
            retriever.add_documents(batch, ids=None)
    areaToRetrieverCache.append({'area': area, 'retriever': retriever})
    end = datetime.now()
    td = (end - start).total_seconds()
    print(f"Finished loading documents. The time of execution of above program was : {td} seconds")
    return retriever


DOCUMENTS_PER_AREA=[]
def getDOCUMENTS(area):
    for item in DOCUMENTS_PER_AREA:
        if item.get('area') == area:
            print('cache hit')
            return item.get('documents')

    print('cache miss, adding in cache')
    area_to_root_page_id=getAllPageIds()
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=350)
    for mapping in area_to_root_page_id:
        if area == mapping.get('area'):
            pages = mapping.get('pages')
            docs = loader.load(page_ids=pages,  keep_markdown_format=True, keep_newlines=True) #include_attachments=True,
            DOCUMENTS = child_splitter.split_documents(docs)
            DOCUMENTS_PER_AREA.append({'area': mapping.get('area'),'documents': DOCUMENTS})
            return DOCUMENTS










