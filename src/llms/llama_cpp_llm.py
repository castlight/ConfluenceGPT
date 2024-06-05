import os
from langchain.llms import LlamaCpp
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from dotenv import load_dotenv
import requests


load_dotenv()

COMMON_PARENT_PATH= os.environ.get('COMMON_PARENT_PATH')
if not os.path.isdir(COMMON_PARENT_PATH):
    os.mkdir(COMMON_PARENT_PATH)

MODEL_PATH = os.path.join(COMMON_PARENT_PATH, os.environ.get('LLM_MODEL'))
MODEL_DOWNLOAD_URL=  os.environ.get('LLM_MODEL_URL')



MAX_TOKENS=os.environ.get('N_PREDICT')
CONTEXT_WINDOW_SIZE=os.environ.get('MODEL_N_CTX')
k=int(os.environ.get('NO_OF_DOCS_TO_SEARCH_FROM'))

def fileNotPresent(filePath):
    return os.path.isfile(filePath) is False
def isDirectoryEmpty(directory):
    return not os.listdir(directory)

def lllNotExist():
    return isDirectoryEmpty(MODEL_PATH) is True

def loadModel():
    if fileNotPresent(MODEL_PATH) is True:
        downloadModel()

def downloadModel():
    print("started downloading model file")
    download_file(MODEL_DOWNLOAD_URL, MODEL_PATH)
    print("Successfully downloaded model file")


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r: #, verify=False
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=None):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                if chunk:
                    f.write(chunk)
    return local_filename

if fileNotPresent(MODEL_PATH):
    downloadModel()


llm = LlamaCpp(
    model_path=MODEL_PATH,
    n_gpu_layers=1,
    n_batch=700,
    n_ctx=CONTEXT_WINDOW_SIZE,
    f16_kv=True,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    temperature=0,
    top_k=k,
    verbose=False,
    use_mlock=True,
    max_tokens=MAX_TOKENS
)

def getLLM():
    return llm

