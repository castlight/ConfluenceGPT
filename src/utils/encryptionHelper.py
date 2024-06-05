from cryptography.fernet import Fernet
import sys
import dotenv
import os



def getEncruptedAPIKey(plainAPIKey) :
    # key is generated
    key = Fernet.generate_key()

    CONFLUENCE_APIKEY_ENCKEY = key.decode()


    f = Fernet(key)

    bytesVal = bytes(plainAPIKey, 'utf-8')

    # the plainAPIKey is converted to encrypted text
    token = f.encrypt(bytesVal)

    # decrypting the ciphertext
    d = f.decrypt(token)

    return {'CONFLUENCE_APIKEY_ENCKEY' : CONFLUENCE_APIKEY_ENCKEY, 'CONFLUENCE_PASSWORD_OR_APIKEY': token.decode() }



if __name__ == "__main__":
    n = len(sys.argv)
    if n != 2:
        print("Incorrect number of arguments.")
        print("Usage: ./src/utils/encryptionHelper.py <confluenceApiKeyValue>")
    else:
        plainKey = sys.argv[1]
        keys = getEncruptedAPIKey(plainKey)
        dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(dotenv_file)
        print('CONFLUENCE_APIKEY_ENCKEY: '+keys['CONFLUENCE_APIKEY_ENCKEY'])
        print('CONFLUENCE_PASSWORD_OR_APIKEY: '+keys['CONFLUENCE_PASSWORD_OR_APIKEY'])
        os.environ["CONFLUENCE_APIKEY_ENCKEY"] = keys['CONFLUENCE_APIKEY_ENCKEY']
        os.environ["CONFLUENCE_PASSWORD_OR_APIKEY"] = keys['CONFLUENCE_PASSWORD_OR_APIKEY']
        # Update the .env file
        dotenv.set_key(dotenv_file, 'CONFLUENCE_APIKEY_ENCKEY', keys['CONFLUENCE_APIKEY_ENCKEY'])
        dotenv.set_key(dotenv_file, 'CONFLUENCE_PASSWORD_OR_APIKEY', keys['CONFLUENCE_PASSWORD_OR_APIKEY'])