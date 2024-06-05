import os
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv


load_dotenv()

COMMON_PARENT_PATH= os.environ.get('COMMON_PARENT_PATH')
if not os.path.isdir(COMMON_PARENT_PATH):
    os.mkdir(COMMON_PARENT_PATH)

EMBEDDINGS_MODEL_NAME = os.environ.get('EMBEDDINGS_MODEL_NAME')
EMBEDDING_CACHE_FOLDER = os.path.join(COMMON_PARENT_PATH, os.environ.get('EMBEDDING_CACHE_FOLDER'))

if not os.path.isdir(EMBEDDING_CACHE_FOLDER):
    os.mkdir(EMBEDDING_CACHE_FOLDER)

EMBEDDINGS=HuggingFaceEmbeddings(
    model_name=EMBEDDINGS_MODEL_NAME,
    cache_folder=EMBEDDING_CACHE_FOLDER
)


def getEmbedding():
    return EMBEDDINGS